# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/clans/profile/ClanProfileSummaryView.py
import BigWorld
from adisp import process, async
from gui.Scaleform.daapi.view.lobby.fortifications import FortClanStatisticsData
from gui.clans import formatters as clan_fmts
from helpers import i18n
from gui.clans.settings import CLIENT_CLAN_RESTRICTIONS as _RES
from gui.clans.items import formatField, isValueAvailable
from gui.shared.formatters import icons, text_styles
from gui.shared.view_helpers.UsersInfoHelper import UsersInfoHelper
from gui.shared.events import OpenLinkEvent
from gui.Scaleform.genConsts.TEXT_MANAGER_STYLES import TEXT_MANAGER_STYLES as _STYLE
from gui.Scaleform.locale.CLANS import CLANS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_formatters
from gui.Scaleform.daapi.view.meta.ClanProfileSummaryViewMeta import ClanProfileSummaryViewMeta

def _stateVO(showRequestBtn, mainStatus=None, tooltip='', enabledRequestBtn=False, addStatus=None, showPersonalBtn=False):
    return {'isShowRequestBtn': showRequestBtn,
     'isEnabledRequestBtn': enabledRequestBtn,
     'isShowPersonnelBtn': showPersonalBtn,
     'mainStatus': mainStatus or '',
     'additionalStatus': addStatus or '',
     'tooltip': tooltip}


def _status(i18nKey, style, icon=None):
    message = CLANS.clanprofile_summaryview_statusmsg(i18nKey)
    if icon is not None:
        message = i18n.makeString(message, icon=icons.makeImageTag(icon, 16, 16, -4, 0))
    else:
        message = i18n.makeString(message)
    return style(message)


_STATES = {_RES.NO_RESTRICTIONS: _stateVO(True, enabledRequestBtn=True),
 _RES.OWN_CLAN: _stateVO(False, showPersonalBtn=True),
 _RES.ALREADY_IN_CLAN: _stateVO(False, addStatus=_status('inAnotherClan', text_styles.success)),
 _RES.FORBIDDEN_ACCOUNT_TYPE: _stateVO(False, addStatus=_status('banned', text_styles.error)),
 _RES.CLAN_IS_FULL: _stateVO(False, addStatus=_status('banned', text_styles.error)),
 _RES.CLAN_APPLICATION_ALREADY_SENT: _stateVO(False, addStatus=_status('requestSubmitted', text_styles.success)),
 _RES.CLAN_INVITE_ALREADY_RECEIVED: _stateVO(False, addStatus=_status('invitationSubmitted', text_styles.success)),
 _RES.SENT_INVITES_LIMIT_REACHED: _stateVO(True, mainStatus=_status('inviteLimit', text_styles.alert, RES_ICONS.MAPS_ICONS_LIBRARY_ALERTICON), tooltip=CLANS.CLANPROFILE_SUMMARYVIEW_TOOLTIP_JOINUNAVAILABLE_INVITESHASBEENREACHED),
 _RES.CLAN_CONSCRIPTION_CLOSED: _stateVO(True, mainStatus=_status('requestNotBeConsidered', text_styles.main, RES_ICONS.MAPS_ICONS_LIBRARY_INFORMATIONICON), tooltip=CLANS.CLANPROFILE_SUMMARYVIEW_TOOLTIP_JOINUNAVAILABLE_RECEIVINGREQUESTSCLOSED),
 _RES.RESYNCHRONIZE: _stateVO(False, addStatus=_status('resynchronize', text_styles.main)),
 _RES.DEFAULT: _stateVO(False)}

class _FortBaseDataReceiver(object):

    def __init__(self, ratings, clanDossier, updateCallback):
        self.__fortLevel = None
        self.__fortStats = None
        self.__fortLevelStr = clan_fmts.DUMMY_UNAVAILABLE_DATA
        self._clanDossier = clanDossier
        self.__ratings = ratings
        self.__updateCallback = updateCallback
        super(_FortBaseDataReceiver, self).__init__()
        self.__updateCallback(*self.__getStatsVO())
        return

    def __getStatsVO(self):
        notActual = self.__fortStats and self.__fortStats.getFbBattlesCount28d() <= 0
        hasFortRating = self.__ratings.hasFortRating()
        if self.__fortLevel is None:
            self.__getFortLevel()
        if self.__fortStats is None:
            self.__getFortStatistics()
        if not hasFortRating and not self.__has28dFortStatistics():
            if self.__fortLevel is None:
                fortInfo = (False, CLANS.CLANPROFILE_SUMMARYVIEW_BLOCKLBL_HASNOBATTLES)
            elif self.__fortLevel > 0:
                fortInfo = (True, 0)
            else:
                fortInfo = (False, CLANS.CLANPROFILE_SUMMARYVIEW_BLOCKLBL_EMPTYFORT)
        else:
            fortInfo = (True, '')
        if self.__fortStats:
            fsBattleCount28d = formatField(getter=self.__fortStats.getFsBattlesCount28d, formatter=BigWorld.wg_getIntegralFormat)
            fbBattleCount28d = formatField(getter=self.__fortStats.getFbBattlesCount28d, formatter=BigWorld.wg_getIntegralFormat)
        else:
            fsBattleCount28d, fbBattleCount28d = clan_fmts.DUMMY_UNAVAILABLE_DATA, clan_fmts.DUMMY_UNAVAILABLE_DATA
        return ([{'local': 'rageLevel10',
           'value': formatField(getter=self.__ratings.getEloRating10, formatter=BigWorld.wg_getIntegralFormat),
           'timeExpired': notActual,
           'tooltip': CLANS.CLANPROFILE_SUMMARYVIEW_TOOLTIP_FORT_ELO_RAGE_10_BODY},
          {'local': 'rageLevel8',
           'value': formatField(getter=self.__ratings.getEloRating8, formatter=BigWorld.wg_getIntegralFormat),
           'timeExpired': notActual,
           'tooltip': CLANS.CLANPROFILE_SUMMARYVIEW_TOOLTIP_FORT_ELO_RAGE_8_BODY},
          {'local': 'sortiesPerDay',
           'value': fsBattleCount28d,
           'tooltip': CLANS.CLANPROFILE_SUMMARYVIEW_TOOLTIP_FORT_SORTIE_COUNT_28_BODY},
          {'local': 'battlesPerDay',
           'value': fbBattleCount28d,
           'tooltip': CLANS.CLANPROFILE_SUMMARYVIEW_TOOLTIP_FORT_BATTLES_COUNT_28_BODY},
          {'local': 'fortLevel',
           'value': self.__fortLevelStr,
           'tooltip': CLANS.CLANPROFILE_SUMMARYVIEW_TOOLTIP_FORT_LEVEL_BODY}], fortInfo)

    def dispose(self):
        self.__updateCallback = None
        self.__ratings = None
        self._clanDossier = None
        self.__fortStats = None
        return

    @async
    def _requestFortLevel(self, callback):
        raise NotImplementedError

    @process
    def __getFortLevel(self):
        self.__fortLevel, self.__fortLevelStr = yield self._requestFortLevel()
        if self.__updateCallback:
            self.__updateCallback(*self.__getStatsVO())

    @process
    def __getFortStatistics(self):
        self.__fortStats = yield self._clanDossier.requestStrongholdStatistics()
        if self.__updateCallback:
            self.__updateCallback(*self.__getStatsVO())

    def __has28dFortStatistics(self):
        return self.__fortStats and (self.__fortStats.getFsBattlesCount28d() > 0 or self.__fortStats.getFbBattlesCount28d() > 0)


class _MyFortDataReceiver(_FortBaseDataReceiver):

    @async
    @process
    def _requestFortLevel(self, callback):
        fortData = yield FortClanStatisticsData.getDataObject()
        if fortData is not None:
            fortLevel = fortData.fortCtrl.getFort().level
            fortLevelStr = fort_formatters.getTextLevel(fortLevel)
        else:
            fortLevel = 0
            fortLevelStr = clan_fmts.DUMMY_UNAVAILABLE_DATA
        callback((fortLevel, fortLevelStr))
        return


class _FortDataReceiver(_FortBaseDataReceiver):

    @async
    @process
    def _requestFortLevel(self, callback):
        strongholdInfo = yield self._clanDossier.requestStrongholdInfo()
        fortLevel = strongholdInfo.getLevel()
        fortLevelStr = formatField(getter=strongholdInfo.getLevel, formatter=fort_formatters.getTextLevel)
        callback((fortLevel, fortLevelStr))


class ClanProfileSummaryView(ClanProfileSummaryViewMeta, UsersInfoHelper):

    def __init__(self):
        ClanProfileSummaryViewMeta.__init__(self)
        UsersInfoHelper.__init__(self)
        self.__stateMask = 0
        self.__fortStatsVOReceiver = None
        return

    @process
    def setClanDossier(self, clanDossier):
        super(ClanProfileSummaryView, self).setClanDossier(clanDossier)
        self._showWaiting()
        clanInfo = yield clanDossier.requestClanInfo()
        if not clanInfo.isValid():
            self._dummyMustBeShown = True
            self._updateDummy()
            self._hideWaiting()
            return
        ratings = yield clanDossier.requestClanRatings()
        globalMapStats = yield clanDossier.requestGlobalMapStats()
        if self.isDisposed():
            return
        self._updateClanInfo(clanInfo)
        ratingStrBuilder = text_styles.builder(delimiter='\n')
        ratingStrBuilder.addStyledText(text_styles.promoTitle, formatField(getter=ratings.getEfficiency, formatter=BigWorld.wg_getIntegralFormat))
        ratingStrBuilder.addStyledText(text_styles.stats, CLANS.CLANPROFILE_SUMMARYVIEW_TOTALRAGE)
        motto = clanInfo.getMotto()
        if motto:
            description = text_styles.main(motto)
        else:
            description = text_styles.standard(CLANS.CLANPROFILE_SUMMARYVIEW_DEFAULTCLANDESCR)
        hasGlobalMap = globalMapStats.hasGlobalMap()
        self.as_setDataS({'totalRating': ratingStrBuilder.render(),
         'totalRatingTooltip': CLANS.CLANPROFILE_SUMMARYVIEW_TOOLTIP_TOTALRATING,
         'clanDescription': description,
         'isShowFortBtn': True,
         'isShowClanNavBtn': hasGlobalMap,
         'isShowUrlString': not hasGlobalMap})
        self.as_updateGeneralBlockS(self.__makeGeneralBlock(clanInfo, syncUserInfo=True))
        if clanDossier.isMyClan():
            self.__fortStatsVOReceiver = _MyFortDataReceiver(ratings, clanDossier, self.__updateFortBlock)
        else:
            self.__fortStatsVOReceiver = _FortDataReceiver(ratings, clanDossier, self.__updateFortBlock)
        self.as_updateGlobalMapBlockS(self.__makeGlobalMapBlock(globalMapStats, ratings))
        self.__updateStatus()
        self._hideWaiting()

    def onAccountWebVitalInfoChanged(self, fieldName, value):
        self.__updateStatus()

    def onClanWebVitalInfoChanged(self, clanDbID, fieldName, value):
        if clanDbID == self._clanDossier.getDbID():
            self.__updateStatus()

    @process
    def onAccountClanProfileChanged(self, profile):
        clanInfo = yield self._clanDossier.requestClanInfo()
        if not self.isDisposed():
            self.as_updateGeneralBlockS(self.__makeGeneralBlock(clanInfo))

    def onClanEmblem128x128Received(self, clanDbID, emblem):
        pass

    def onClanEmblem256x256Received(self, clanDbID, emblem):
        if emblem:
            self.as_setClanEmblemS(self.getMemoryTexturePath(emblem))

    @process
    def onUserNamesReceived(self, names):
        clanInfo = yield self._clanDossier.requestClanInfo()
        if not self.isDisposed():
            self.as_updateGeneralBlockS(self.__makeGeneralBlock(clanInfo))

    def hyperLinkGotoDetailsMap(self):
        self.fireEvent(OpenLinkEvent(OpenLinkEvent.GLOBAL_MAP_PROMO_SUMMARY))

    def hyperLinkGotoMap(self):
        self.fireEvent(OpenLinkEvent(OpenLinkEvent.GLOBAL_MAP_SUMMARY))

    def sendRequestHandler(self):
        self._sendApplication()

    def _onAppSuccessfullySent(self):
        self.__updateStatus()

    def _updateClanEmblem(self, clanDbID):
        self.requestClanEmblem256x256(clanDbID)

    def _updateHeaderState(self):
        pass

    def _dispose(self):
        if self.__fortStatsVOReceiver:
            self.__fortStatsVOReceiver.dispose()
            self.__fortStatsVOReceiver = None
        super(ClanProfileSummaryView, self)._dispose()
        return

    def __updateFortBlock(self, stats, fortInfo):
        self.as_updateFortBlockS({'isShowHeader': True,
         'header': text_styles.highTitle(CLANS.CLANPROFILE_MAINWINDOWTAB_FORTIFICATION),
         'statBlocks': self.__makeStatsBlock(stats),
         'emptyLbl': text_styles.standard(fortInfo[1]),
         'isActivated': fortInfo[0]})

    def __makeGeneralBlock(self, clanInfo, syncUserInfo=False):
        stats = [{'local': 'commander',
          'value': formatField(getter=clanInfo.getLeaderDbID, formatter=self.getGuiUserName),
          'textStyle': _STYLE.STATS_TEXT}, {'local': 'totalPlayers',
          'value': formatField(getter=clanInfo.getMembersCount, formatter=BigWorld.wg_getIntegralFormat)}]
        canSeeTreasury = self.clansCtrl.getLimits().canSeeTreasury(self._clanDossier)
        if canSeeTreasury.success:
            stats.append({'local': 'gold',
             'value': formatField(getter=clanInfo.getTreasuryValue, formatter=BigWorld.wg_getIntegralFormat),
             'icon': RES_ICONS.MAPS_ICONS_LIBRARY_GOLDICON_2})
        if syncUserInfo:
            self.syncUsersInfo()
        return {'isShowHeader': False,
         'header': '',
         'statBlocks': self.__makeStatsBlock(stats),
         'isActivated': True}

    def __makeGlobalMapBlock(self, globalMapStats, ratings):
        hasGlobalMap = globalMapStats.hasGlobalMap()
        if hasGlobalMap:
            notActual = ratings.getGlobalMapBattlesFor28Days() <= 0
            stats = [{'local': 'rageLevel10',
              'value': formatField(getter=ratings.getGlobalMapEloRating10, formatter=BigWorld.wg_getIntegralFormat),
              'timeExpired': notActual,
              'tooltip': CLANS.CLANPROFILE_SUMMARYVIEW_TOOLTIP_GMAP_ELO_RAGE_10_BODY},
             {'local': 'rageLevel8',
              'value': formatField(getter=ratings.getGlobalMapEloRating8, formatter=BigWorld.wg_getIntegralFormat),
              'timeExpired': notActual,
              'tooltip': CLANS.CLANPROFILE_SUMMARYVIEW_TOOLTIP_GMAP_ELO_RAGE_8_BODY},
             {'local': 'rageLevel6',
              'value': formatField(getter=ratings.getGlobalMapEloRating6, formatter=BigWorld.wg_getIntegralFormat),
              'timeExpired': notActual,
              'tooltip': CLANS.CLANPROFILE_SUMMARYVIEW_TOOLTIP_GMAP_ELO_RAGE_6_BODY},
             {'local': 'battlesCount',
              'value': formatField(getter=ratings.getGlobalMapBattlesFor28Days, formatter=BigWorld.wg_getIntegralFormat),
              'tooltip': CLANS.CLANPROFILE_SUMMARYVIEW_TOOLTIP_GMAP_BATTLES_COUNT_BODY},
             {'local': 'provinces',
              'value': formatField(getter=globalMapStats.getCurrentProvincesCount, formatter=BigWorld.wg_getIntegralFormat),
              'tooltip': CLANS.CLANPROFILE_SUMMARYVIEW_TOOLTIP_GMAP_PROVINCE_BODY}]
            statsBlock = self.__makeStatsBlock(stats)
            emptyLbl = ''
        else:
            statsBlock = ()
            if isValueAvailable(globalMapStats.hasGlobalMap):
                emptyLbl = text_styles.standard(CLANS.CLANPROFILE_SUMMARYVIEW_BLOCKLBL_EMPTYGLOBALMAP)
            else:
                emptyLbl = '%s %s' % (icons.alert(), text_styles.standard(CLANS.CLANPROFILE_SUMMARYVIEW_NODATA))
        return {'isShowHeader': True,
         'header': text_styles.highTitle(CLANS.CLANPROFILE_MAINWINDOWTAB_GLOBALMAP),
         'statBlocks': statsBlock,
         'emptyLbl': emptyLbl,
         'isActivated': hasGlobalMap}

    def __makeStatsBlock(self, listValues):
        lst = []
        for item in listValues:
            flag = item.get('flag', None)
            if flag is not None and not bool(self.__stateMask & flag):
                continue
            localKey = item.get('local', None)
            value = item.get('value', None)
            isTimeExpired = item.get('timeExpired', False)
            tooltipBody = item.get('tooltip', None)
            textStyle = item.get('textStyle', None)
            isUseTextStylePattern = textStyle is not None
            valueStyle = text_styles.stats
            localKey = i18n.makeString(CLANS.clanprofile_summaryview_blocklbl(localKey))
            tooltipHeader = localKey
            if isTimeExpired:
                valueStyle = text_styles.standard
                tooltipBody = CLANS.CLANPROFILE_SUMMARYVIEW_TOOLTIP_RATINGOUTDATED_BODY
            elif tooltipBody is None:
                tooltipBody = None
                tooltipHeader = None
            if not isinstance(value, str):
                value = BigWorld.wg_getIntegralFormat(value)
            icon = item.get('icon', None)
            if icon is not None:
                icon = icons.makeImageTag(icon, 16, 16, -4, 0)
                value = icon + ' ' + value
            if isUseTextStylePattern:
                truncateVo = {'isUseTruncate': isUseTextStylePattern,
                 'textStyle': textStyle,
                 'maxWidthTF': 140}
            else:
                truncateVo = None
            lst.append({'label': text_styles.main(localKey),
             'value': valueStyle(str(value)) if not isUseTextStylePattern else value,
             'tooltipHeader': tooltipHeader,
             'tooltipBody': i18n.makeString(tooltipBody) if tooltipBody is not None else '',
             'isUseTextStyle': isUseTextStylePattern,
             'truncateVo': truncateVo})

        return lst

    def __updateStatus(self):
        reason = self.clansCtrl.getLimits().canSendApplication(self._clanDossier).reason
        assert reason in _STATES, 'Unknown reason, ' + reason
        self.as_updateStatusS(_STATES[reason])
