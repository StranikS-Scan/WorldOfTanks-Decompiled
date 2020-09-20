# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/clans/profile/ClanProfileSummaryView.py
from adisp import process
from constants import IS_CHINA
from gui.impl import backport
from helpers import i18n, dependency
from gui.clans.settings import CLIENT_CLAN_RESTRICTIONS as _RES
from gui.clans.items import formatField, isValueAvailable, StrongholdStatisticsData
from gui.clans.clan_helpers import isStrongholdsEnabled
from gui.clans.formatters import DUMMY_UNAVAILABLE_DATA
from gui.shared.formatters import icons, text_styles
from gui.shared.utils.functions import makeTooltip
from gui.shared.view_helpers.UsersInfoHelper import UsersInfoHelper
from gui.shared.events import OpenLinkEvent
from gui.Scaleform.genConsts.TEXT_MANAGER_STYLES import TEXT_MANAGER_STYLES as _STYLE
from gui.Scaleform.locale.CLANS import CLANS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.daapi.view.meta.ClanProfileSummaryViewMeta import ClanProfileSummaryViewMeta
from gui.shared.image_helper import ImagesFetchCoordinator
from skeletons.gui.lobby_context import ILobbyContext
_DIVISIONS = (6, 8, 10)

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
 _RES.CLAN_ENTER_COOLDOWN: _stateVO(True, enabledRequestBtn=False),
 _RES.DEFAULT: _stateVO(False)}

class StrongholdDataReceiver(object):

    def __init__(self, clanDossier, updateStrongholdCallback):
        self.__disposed = False
        self.__clanDossier = clanDossier
        self.__updateStrongholdCallback = updateStrongholdCallback
        self.__strongholdStats = StrongholdStatisticsData()
        self.__imagesFetchCoordinator = ImagesFetchCoordinator()

    def getStatsVO(self):
        stats = self.__strongholdStats
        isActual = stats.hasSorties() or stats.hasFortBattles()
        rows = (('rageLevel10',
          stats.getElo10(),
          isActual,
          CLANS.CLANPROFILE_SUMMARYVIEW_TOOLTIP_FORT_ELO_RAGE_10_BODY),
         ('rageLevel8',
          stats.getElo8(),
          isActual,
          CLANS.CLANPROFILE_SUMMARYVIEW_TOOLTIP_FORT_ELO_RAGE_8_BODY),
         ('rageLevel6',
          stats.getElo6(),
          isActual,
          CLANS.CLANPROFILE_SUMMARYVIEW_TOOLTIP_FORT_ELO_RAGE_6_BODY),
         ('sortiesPerDay',
          stats.getSortiesIn28Days(),
          True,
          CLANS.CLANPROFILE_SUMMARYVIEW_TOOLTIP_FORT_SORTIE_COUNT_28_BODY),
         ('battlesPerDay',
          stats.getFortBattlesIn28Days(),
          True,
          CLANS.CLANPROFILE_SUMMARYVIEW_TOOLTIP_FORT_BATTLES_COUNT_28_BODY),
         ('fortLevel',
          stats.getStrongholdLevel(),
          True,
          CLANS.CLANPROFILE_SUMMARYVIEW_TOOLTIP_FORT_LEVEL_BODY))
        if stats.getLeagues():
            excludes = ('rageLevel6', 'rageLevel8', 'rageLevel10')
        else:
            excludes = ('rageLevel6', 'rageLevel8') if IS_CHINA else ()
        return [ {'local': key,
         'value': DUMMY_UNAVAILABLE_DATA if elo is None else elo,
         'timeExpired': True if elo is None else not actual,
         'tooltip': tooltip,
         'isHidden': False} for key, elo, actual, tooltip in rows if key not in excludes ]

    def getLeaguesVO(self):
        return self.__strongholdStats.getLeagues()

    def dispose(self):
        self.__disposed = True
        self.__clanDossier = None
        self.__updateStrongholdCallback = None
        self.__strongholdStats = None
        self.__imagesFetchCoordinator.fini()
        return

    @process
    def updateStrongholdStatistics(self):
        self.__strongholdStats = yield self.__clanDossier.requestStrongholdStatistics()
        if self.__disposed:
            return
        leagues = self.__strongholdStats.getLeagues()
        for league in leagues:
            emblem = league.get('emblem')
            league['emblemImage'] = yield self.__imagesFetchCoordinator.fetchImageByUrl(emblem, oneUse=False)
            if self.__disposed:
                return

        self.__updateStrongholdStatistics()

    def __updateStrongholdStatistics(self):
        if self.__updateStrongholdCallback:
            self.__updateStrongholdCallback(self.getStatsVO(), self.getLeaguesVO())


class ClanProfileSummaryView(ClanProfileSummaryViewMeta, UsersInfoHelper):
    _lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        ClanProfileSummaryViewMeta.__init__(self)
        UsersInfoHelper.__init__(self)
        self.__stateMask = 0
        self.__strongholdStatsVOReceiver = None
        self._isGlobalMapEnabled = self._lobbyContext.getServerSettings().isGlobalMapEnabled()
        self._lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
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
        ratingStrBuilder.addStyledText(text_styles.promoTitle, formatField(getter=ratings.getEfficiency, formatter=backport.getIntegralFormat))
        ratingStrBuilder.addStyledText(text_styles.stats, CLANS.CLANPROFILE_SUMMARYVIEW_TOTALRAGE)
        motto = clanInfo.getMotto()
        if motto:
            description = text_styles.main(motto)
        else:
            description = text_styles.standard(CLANS.CLANPROFILE_SUMMARYVIEW_DEFAULTCLANDESCR)
        hasGlobalMap = globalMapStats.hasGlobalMap() and self._isGlobalMapEnabled
        self.as_setDataS({'totalRating': ratingStrBuilder.render(),
         'totalRatingTooltip': CLANS.CLANPROFILE_SUMMARYVIEW_TOOLTIP_TOTALRATING,
         'clanDescription': description,
         'isShowFortBtn': True,
         'isShowClanNavBtn': hasGlobalMap,
         'isShowUrlString': not hasGlobalMap,
         'isDetailLinkEnabled': self._isGlobalMapEnabled})
        self.as_updateGeneralBlockS(self.__makeGeneralBlock(clanInfo, syncUserInfo=True))
        self.as_updateGlobalMapBlockS(self.__makeGlobalMapBlock(globalMapStats, ratings))
        self.__updateStatus()
        if isStrongholdsEnabled():
            self.__strongholdStatsVOReceiver = StrongholdDataReceiver(clanDossier, self.__updateStrongholdBlock)
            self.__strongholdStatsVOReceiver.updateStrongholdStatistics()
        else:
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
        if self.__strongholdStatsVOReceiver:
            self.__strongholdStatsVOReceiver.dispose()
            self.__strongholdStatsVOReceiver = None
        self._lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        super(ClanProfileSummaryView, self)._dispose()
        return

    def __onServerSettingChanged(self, diff):
        ratings = yield self._clanDossier.requestClanRatings()
        globalMapStats = yield self._clanDossier.requestGlobalMapStats()
        if 'isGlobalMapEnabled' in diff or ('isGlobalMapEnabled', '_r') in diff:
            self._isGlobalMapEnabled = self._lobbyContext.getServerSettings().isGlobalMapEnabled()
            self.as_updateGlobalMapBlockS(self.__makeGlobalMapBlock(globalMapStats, ratings))

    def __updateStrongholdBlock(self, stats, leagues=None):
        if leagues:
            self.as_updateLeaguesBlockS({'leagues': self.__makeLeaguesBlock(leagues)})
        self.as_updateFortBlockS({'isShowHeader': True,
         'header': text_styles.highTitle(CLANS.CLANPROFILE_MAINWINDOWTAB_FORTIFICATION),
         'statBlocks': self.__makeStatsBlock(stats),
         'emptyLbl': '',
         'isActivated': True})
        self._hideWaiting()

    def __makeGeneralBlock(self, clanInfo, syncUserInfo=False):
        stats = [{'local': 'commander',
          'value': formatField(getter=clanInfo.getLeaderDbID, formatter=self.getGuiUserName),
          'textStyle': _STYLE.STATS_TEXT}, {'local': 'totalPlayers',
          'value': formatField(getter=clanInfo.getMembersCount, formatter=backport.getIntegralFormat)}]
        canSeeTreasury = self.webCtrl.getLimits().canSeeTreasury(self._clanDossier)
        if canSeeTreasury.success:
            stats.append({'local': 'gold',
             'value': formatField(getter=clanInfo.getTreasuryValue, formatter=backport.getIntegralFormat),
             'icon': RES_ICONS.MAPS_ICONS_LIBRARY_GOLDICON_2})
        if syncUserInfo:
            self.syncUsersInfo()
        return {'isShowHeader': False,
         'header': '',
         'statBlocks': self.__makeStatsBlock(stats),
         'isActivated': True}

    def __makeGlobalMapBlock(self, globalMapStats, ratings):
        hasGlobalMap = globalMapStats.hasGlobalMap()
        if hasGlobalMap and self._isGlobalMapEnabled:
            notActual = ratings.getGlobalMapBattlesFor28Days() <= 0
            stats = [{'local': 'rageLevel10',
              'value': formatField(getter=ratings.getGlobalMapEloRating10, formatter=backport.getIntegralFormat),
              'timeExpired': notActual,
              'tooltip': CLANS.CLANPROFILE_SUMMARYVIEW_TOOLTIP_GMAP_ELO_RAGE_10_BODY},
             {'local': 'rageLevel8',
              'value': formatField(getter=ratings.getGlobalMapEloRating8, formatter=backport.getIntegralFormat),
              'timeExpired': notActual,
              'tooltip': CLANS.CLANPROFILE_SUMMARYVIEW_TOOLTIP_GMAP_ELO_RAGE_8_BODY},
             {'local': 'rageLevel6',
              'value': formatField(getter=ratings.getGlobalMapEloRating6, formatter=backport.getIntegralFormat),
              'timeExpired': notActual,
              'tooltip': CLANS.CLANPROFILE_SUMMARYVIEW_TOOLTIP_GMAP_ELO_RAGE_6_BODY},
             {'local': 'battlesCount',
              'value': formatField(getter=ratings.getGlobalMapBattlesFor28Days, formatter=backport.getIntegralFormat),
              'tooltip': CLANS.CLANPROFILE_SUMMARYVIEW_TOOLTIP_GMAP_BATTLES_COUNT_BODY},
             {'local': 'provinces',
              'value': formatField(getter=globalMapStats.getCurrentProvincesCount, formatter=backport.getIntegralFormat),
              'tooltip': CLANS.CLANPROFILE_SUMMARYVIEW_TOOLTIP_GMAP_PROVINCE_BODY}]
            statsBlock = self.__makeStatsBlock(stats)
            emptyLbl = ''
        else:
            statsBlock = ()
            if self._isGlobalMapEnabled:
                if isValueAvailable(globalMapStats.hasGlobalMap):
                    emptyLbl = text_styles.standard(CLANS.CLANPROFILE_SUMMARYVIEW_BLOCKLBL_EMPTYGLOBALMAP)
                else:
                    emptyLbl = '%s %s' % (icons.alert(), text_styles.standard(CLANS.CLANPROFILE_SUMMARYVIEW_NODATA))
            else:
                hasGlobalMap = False
                emptyLbl = emptyLbl = '%s %s' % (icons.alert(), text_styles.standard(CLANS.GLOBALMAP_DISABLED))
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
            isHidden = item.get('isHidden', None)
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
                value = backport.getIntegralFormat(value)
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
             'truncateVo': truncateVo,
             'isHidden': isHidden})

        return lst

    def __makeLeaguesBlock(self, leagues):
        leaguesVO = []
        for league in leagues[:len(_DIVISIONS)]:
            division = league.get('max_vehicle_level')
            level = division if division in _DIVISIONS else _DIVISIONS[0]
            imgSource = league.get('emblemImage') or RES_ICONS.getDefaultLeagueIcon(level)
            elo = league.get('elo')
            if elo:
                elo = backport.getNiceNumberFormat(elo)
                label = text_styles.stats(elo) if league.get('position') else text_styles.main(elo)
            else:
                label = text_styles.main(DUMMY_UNAVAILABLE_DATA)
            tooltip = league.get('tooltip')
            if tooltip:
                tooltip = makeTooltip(tooltip.get('header'), tooltip.get('body'))
            leaguesVO.append({'imgSource': imgSource,
             'label': label,
             'tooltip': tooltip})

        return leaguesVO

    def __updateStatus(self):
        reason = self.webCtrl.getLimits().canSendApplication(self._clanDossier).reason
        self.as_updateStatusS(_STATES[reason])
