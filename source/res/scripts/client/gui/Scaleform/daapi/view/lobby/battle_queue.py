# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/battle_queue.py
import weakref
import BigWorld
from adisp import adisp_process, adisp_async
from client_request_lib.exceptions import ResponseCodes
import MusicControllerWWISE
import constants
from CurrentVehicle import g_currentVehicle
from PlayerEvents import g_playerEvents
from debug_utils import LOG_DEBUG
from frameworks.wulf import WindowLayer
from gui import makeHtmlString
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.event_boards.formaters import getClanTag
from gui.Scaleform.daapi.view.lobby.rally import vo_converters
from gui.Scaleform.daapi.view.meta.BattleQueueMeta import BattleQueueMeta
from gui.Scaleform.daapi.view.meta.BattleStrongholdsQueueMeta import BattleStrongholdsQueueMeta
from gui.impl.lobby.comp7 import comp7_shared, comp7_i18n_helpers, comp7_model_helpers
from gui.shared.view_helpers.blur_manager import CachedBlur
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control import prb_getters, prbEntityProperty
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME, getTypeBigIconPath
from gui.shared.image_helper import getTextureLinkByID, ImagesFetchCoordinator
from gui.shared.system_factory import registerBattleQueueProvider, collectBattleQueueProvider
from gui.shared.view_helpers import ClanEmblemsHelper
from gui.sounds.ambients import BattleQueueEnv
from helpers import dependency, i18n, time_utils, int2roman
from helpers.i18n import makeString
from skeletons.gui.game_control import IWinbackController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
TYPES_ORDERED = (('heavyTank', ITEM_TYPES.VEHICLE_TAGS_HEAVY_TANK_NAME),
 ('mediumTank', ITEM_TYPES.VEHICLE_TAGS_MEDIUM_TANK_NAME),
 ('lightTank', ITEM_TYPES.VEHICLE_TAGS_LIGHT_TANK_NAME),
 ('AT-SPG', ITEM_TYPES.VEHICLE_TAGS_AT_SPG_NAME),
 ('SPG', ITEM_TYPES.VEHICLE_TAGS_SPG_NAME))
_LONG_WAITING_LEVELS = (9, 10)
_HTMLTEMP_PLAYERSLABEL = 'html_templates:lobby/queue/playersLabel'

@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def needShowLongWaitingWarning(lobbyContext=None):
    vehicle = g_currentVehicle.item
    return lobbyContext is not None and vehicle is not None and vehicle.type == VEHICLE_CLASS_NAME.SPG and vehicle.level in _LONG_WAITING_LEVELS


class QueueProvider(object):

    def __init__(self, proxy, qType=constants.QUEUE_TYPE.UNKNOWN):
        super(QueueProvider, self).__init__()
        self._proxy = weakref.proxy(proxy)
        self._queueType = qType
        self._queueCallback = None
        return

    def start(self):
        g_playerEvents.onQueueInfoReceived += self.processQueueInfo
        self.requestQueueInfo()

    def stop(self):
        g_playerEvents.onQueueInfoReceived -= self.processQueueInfo
        if self._queueCallback is not None:
            BigWorld.cancelCallback(self._queueCallback)
            self._queueCallback = None
        self._queueType = constants.QUEUE_TYPE.UNKNOWN
        self._proxy = None
        return

    def getQueueType(self):
        return self._queueType

    def requestQueueInfo(self):
        self._queueCallback = None
        currPlayer = BigWorld.player()
        if currPlayer is not None and hasattr(currPlayer, 'requestQueueInfo'):
            self._doRequestQueueInfo(currPlayer)
            self._queueCallback = BigWorld.callback(5, self.requestQueueInfo)
        return

    def processQueueInfo(self, qInfo):
        pass

    def needAdditionalInfo(self):
        return False

    def additionalInfo(self):
        pass

    def getAdditionalParams(self):
        return {}

    def getTitle(self, guiType):
        titleRes = R.strings.menu.loading.battleTypes.num(guiType)
        return backport.text(titleRes()) if titleRes.exists() else ''

    def getIconPath(self, iconlabel):
        return backport.image(R.images.gui.maps.icons.battleTypes.c_136x136.dyn(iconlabel)())

    def getTankInfoLabel(self):
        return makeString(MENU.PREBATTLE_TANKLABEL)

    def getTankIcon(self, vehicle):
        return getTypeBigIconPath(vehicle.type)

    def getTankName(self, vehicle):
        return vehicle.shortUserName

    def getLayoutStr(self):
        pass

    def forceStart(self):
        currPlayer = BigWorld.player()
        if currPlayer is not None and hasattr(currPlayer, 'createArenaFromQueue'):
            currPlayer.createArenaFromQueue()
        return

    def _doRequestQueueInfo(self, currPlayer):
        params = self._getRequestQueueInfoParams()
        LOG_DEBUG('Requestion queue info: ', params)
        currPlayer.requestQueueInfo(*params)

    def _getRequestQueueInfoParams(self):
        return (self._queueType,)


class RandomQueueProvider(QueueProvider):

    def __init__(self, proxy, qType=constants.QUEUE_TYPE.UNKNOWN):
        super(RandomQueueProvider, self).__init__(proxy, qType)
        self._needAdditionalInfo = None
        return

    def processQueueInfo(self, qInfo):
        info = dict(qInfo)
        if 'classes' in info:
            vClasses = info['classes']
            vClassesLen = len(vClasses)
        else:
            vClasses = []
            vClassesLen = 0
        self._createCommonPlayerString(sum(vClasses))
        if vClassesLen:
            vClassesData = []
            for vClass, message in TYPES_ORDERED:
                idx = constants.VEHICLE_CLASS_INDICES[vClass]
                vClassesData.append({'type': message,
                 'icon': getTypeBigIconPath(vClass),
                 'count': vClasses[idx] if idx < vClassesLen else 0})

            self._proxy.as_setDPS(vClassesData)
        self._proxy.as_showStartS(self._isStartButtonDisplayed(vClasses))

    def needAdditionalInfo(self):
        if self._needAdditionalInfo is None:
            self._needAdditionalInfo = needShowLongWaitingWarning()
        return self._needAdditionalInfo

    def additionalInfo(self):
        return text_styles.main(makeString(MENU.PREBATTLE_WAITINGTIMEWARNING))

    @staticmethod
    def _isStartButtonDisplayed(vClasses):
        return constants.IS_DEVELOPMENT and sum(vClasses) > 1

    def _createCommonPlayerString(self, playerCount):
        self._proxy.flashObject.as_setPlayers(makeHtmlString(_HTMLTEMP_PLAYERSLABEL, 'players', {'count': playerCount}))


class _EventQueueProvider(RandomQueueProvider):
    pass


class _RankedQueueProvider(RandomQueueProvider):
    pass


class _MapboxQueueProvider(RandomQueueProvider):
    pass


class _BattleRoyaleQueueProvider(RandomQueueProvider):

    def processQueueInfo(self, qInfo):
        playersCount = qInfo.get('players', 0)
        self._createCommonPlayerString(playersCount)
        modesData = []
        for mode in constants.BattleRoyaleMode.ALL:
            modesData.append({'type': backport.text(R.strings.menu.prebattle.battleRoyale.dyn(mode)()),
             'icon': RES_ICONS.getBattleRoyaleModeIconPath(mode),
             'count': qInfo.get(mode, 0)})

        self._proxy.as_setDPS(modesData)

    def getLayoutStr(self):
        pass

    def getAdditionalParams(self):
        guiType = prb_getters.getArenaGUIType(queueType=self._queueType)
        titleRes = R.strings.menu.loading.battleTypes.subTitle.num(guiType)
        return {'subTitle': backport.text(titleRes()) if titleRes.exists() else ''}


class _Comp7QueueProvider(RandomQueueProvider):

    def processQueueInfo(self, qInfo):
        info = dict(qInfo)
        ranks = info.get('ranks', {})
        qualPlayers = info.get('qualPlayers', 0)
        allPlayersCount = info.get('players', sum(ranks.values()) + qualPlayers)
        self._createCommonPlayerString(allPlayersCount)
        if ranks:
            ranksData = []
            isInQualification = comp7_shared.isQualification()
            playerRankIdx = comp7_shared.getPlayerDivision().rank if not isInQualification else None
            for rankIdx, playersCount in ranks.items():
                rankName = comp7_i18n_helpers.RANK_MAP[rankIdx]
                ranksData.append(self.__getRankData(rankName, playersCount, rankIdx == playerRankIdx))

            ranksData.append(self.__getRankData('qualification', qualPlayers, isInQualification))
            self._proxy.as_setDPS(ranksData)
        self._proxy.as_showStartS(constants.IS_DEVELOPMENT and allPlayersCount > 1)
        return

    def getLayoutStr(self):
        pass

    def getTankInfoLabel(self):
        pass

    def getTankIcon(self, vehicle):
        pass

    def getTankName(self, vehicle):
        pass

    def needAdditionalInfo(self):
        return False

    def additionalInfo(self):
        pass

    def __getRankData(self, rankName, playersCount, isHighlight):
        seasonName = comp7_model_helpers.getSeasonNameEnum().value
        rankImg = R.images.gui.maps.icons.comp7.ranks.dyn(seasonName).c_40.dyn(rankName)
        rankStr = R.strings.comp7.rank.dyn(rankName)
        return {'type': backport.text(rankStr()),
         'icon': backport.image(rankImg()),
         'count': playersCount,
         'highlight': isHighlight}


class _WinbackQueueProvider(RandomQueueProvider):
    __winbackController = dependency.descriptor(IWinbackController)

    def getLayoutStr(self):
        pass

    def getTitle(self, guiType):
        return backport.text(R.strings.winback.winbackBattleQueue.title())

    def getAdditionalParams(self):
        subTitleMainText = backport.text(R.strings.winback.winbackBattleQueue.subTitle.text())
        subTitleBattlesLeft = backport.text(R.strings.winback.winbackBattleQueue.subTitle.battleRemaining(), battlesCount=text_styles.tutorial(str(self.__winbackController.getWinbackBattlesCountLeft())))
        return {'subTitle': ' '.join((subTitleMainText, text_styles.stats(subTitleBattlesLeft))),
         'footerText': backport.text(R.strings.winback.winbackBattleQueue.footer.text())}


registerBattleQueueProvider(constants.QUEUE_TYPE.RANDOMS, RandomQueueProvider)
registerBattleQueueProvider(constants.QUEUE_TYPE.EVENT_BATTLES, _EventQueueProvider)
registerBattleQueueProvider(constants.QUEUE_TYPE.RANKED, _RankedQueueProvider)
registerBattleQueueProvider(constants.QUEUE_TYPE.BATTLE_ROYALE, _BattleRoyaleQueueProvider)
registerBattleQueueProvider(constants.QUEUE_TYPE.MAPBOX, _MapboxQueueProvider)
registerBattleQueueProvider(constants.QUEUE_TYPE.COMP7, _Comp7QueueProvider)
registerBattleQueueProvider(constants.QUEUE_TYPE.WINBACK, _WinbackQueueProvider)

def _providerFactory(proxy, qType):
    provider = collectBattleQueueProvider(qType) or QueueProvider
    return provider(proxy, qType)


class BattleQueue(BattleQueueMeta, LobbySubView):
    __sound_env__ = BattleQueueEnv

    def __init__(self, _=None):
        super(BattleQueue, self).__init__()
        self.__createTime = 0
        self.__timerCallback = None
        self.__provider = None
        self._blur = CachedBlur()
        return

    @prbEntityProperty
    def prbEntity(self):
        return None

    def onEscape(self):
        dialogsContainer = self.app.containerManager.getContainer(WindowLayer.TOP_WINDOW)
        if not dialogsContainer.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.LOBBY_MENU}):
            self.fireEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_MENU)), scope=EVENT_BUS_SCOPE.LOBBY)

    def startClick(self):
        if self.__provider is not None:
            self.__provider.forceStart()
        return

    def exitClick(self):
        self.prbEntity.exitFromQueue()

    def onStartBattle(self):
        self.__stopUpdateScreen()

    def _populate(self):
        super(BattleQueue, self)._populate()
        self._blur.enable()
        self.addListener(events.GameEvent.SHOW_EXTERNAL_COMPONENTS, self._onShowExternals, scope=EVENT_BUS_SCOPE.GLOBAL)
        self.addListener(events.GameEvent.HIDE_EXTERNAL_COMPONENTS, self._onHideExternals, scope=EVENT_BUS_SCOPE.GLOBAL)
        g_playerEvents.onArenaCreated += self.onStartBattle
        self.__updateQueueInfo()
        self.__updateTimer()
        self.__updateClientState()
        MusicControllerWWISE.play()

    def _dispose(self):
        self.__stopUpdateScreen()
        g_playerEvents.onArenaCreated -= self.onStartBattle
        self.removeListener(events.GameEvent.SHOW_EXTERNAL_COMPONENTS, self._onShowExternals, scope=EVENT_BUS_SCOPE.GLOBAL)
        self.removeListener(events.GameEvent.HIDE_EXTERNAL_COMPONENTS, self._onHideExternals, scope=EVENT_BUS_SCOPE.GLOBAL)
        self._blur.fini()
        super(BattleQueue, self)._dispose()

    def __updateClientState(self):
        if self.prbEntity is None:
            return
        else:
            permissions = self.prbEntity.getPermissions()
            if not permissions.canExitFromQueue():
                self.as_showExitS(False)
            guiType = prb_getters.getArenaGUIType(queueType=self.__provider.getQueueType())
            title = self.__provider.getTitle(guiType)
            descriptionRes = R.strings.menu.loading.battleTypes.desc.num(guiType)
            description = backport.text(descriptionRes()) if descriptionRes.exists() else ''
            if guiType != constants.ARENA_GUI_TYPE.UNKNOWN and guiType in constants.ARENA_GUI_TYPE_LABEL.LABELS:
                iconlabel = constants.ARENA_GUI_TYPE_LABEL.LABELS[guiType]
            else:
                iconlabel = 'neutral'
            if self.__provider.needAdditionalInfo():
                additional = self.__provider.additionalInfo()
            else:
                additional = ''
            vehicle = g_currentVehicle.item
            textLabel = self.__provider.getTankInfoLabel()
            tankName = self.__provider.getTankName(vehicle)
            iconPath = self.__provider.getTankIcon(vehicle)
            layoutStr = self.__provider.getLayoutStr()
            typeInfo = {'iconLabel': iconlabel,
             'iconPath': self.__provider.getIconPath(iconlabel),
             'title': title,
             'description': description,
             'additional': additional,
             'tankLabel': text_styles.main(textLabel),
             'tankIcon': iconPath,
             'tankName': tankName,
             'layoutStr': layoutStr}
            typeInfo.update(self.__provider.getAdditionalParams())
            self.as_setTypeInfoS(typeInfo)
            return

    def __stopUpdateScreen(self):
        if self.__timerCallback is not None:
            BigWorld.cancelCallback(self.__timerCallback)
            self.__timerCallback = None
        if self.__provider is not None:
            self.__provider.stop()
            self.__provider = None
        return

    def __updateQueueInfo(self):
        if self.prbEntity is None:
            return
        else:
            qType = self.prbEntity.getQueueType()
            self.__provider = _providerFactory(self, qType)
            self.__provider.start()
            return

    def __updateTimer(self):
        self.__timerCallback = None
        self.__timerCallback = BigWorld.callback(1, self.__updateTimer)
        textLabel = text_styles.main(makeString(MENU.PREBATTLE_TIMERLABEL))
        timeLabel = '%d:%02d' % divmod(self.__createTime, 60)
        if self.__provider is not None and self.__provider.needAdditionalInfo():
            timeLabel = text_styles.concatStylesToSingleLine(timeLabel, '*')
        self.as_setTimerS(textLabel, timeLabel)
        self.__createTime += 1
        return

    def _getProvider(self):
        return self.__provider

    def _onHideExternals(self, _):
        self._blur.disable()

    def _onShowExternals(self, _):
        self._blur.enable()


class BattleStrongholdsQueue(BattleStrongholdsQueueMeta, LobbySubView, ClanEmblemsHelper, IGlobalListener):
    __sound_env__ = BattleQueueEnv
    itemsCache = dependency.descriptor(IItemsCache)
    ANIMATION_DEFAULT_DURATION = 5

    def __init__(self, _=None):
        super(BattleStrongholdsQueue, self).__init__()
        self.__timerCallback = None
        self.__startAnimationTime = None
        self.__animationDuration = self.ANIMATION_DEFAULT_DURATION
        self.__groups = []
        self.__battleQueueVO = {}
        self.__imagesFetchCoordinator = ImagesFetchCoordinator()
        self._blur = CachedBlur()
        return

    @prbEntityProperty
    def prbEntity(self):
        return None

    def exitClick(self):
        self.prbEntity.exitFromQueue()

    def onClanEmblem32x32Received(self, clanDbID, emblem):
        clanEmblem = getTextureLinkByID(self.getMemoryTexturePath(emblem)) if emblem else None
        self.__battleQueueVO['myClanIcon'] = clanEmblem or ''
        self.as_setTypeInfoS(self.__battleQueueVO)
        if self.prbEntity is None:
            return
        else:
            self.prbEntity.getMatchmakingInfo(callback=self.__onMatchmakingInfo)
            return

    def onEscape(self):
        dialogsContainer = self.app.containerManager.getContainer(WindowLayer.TOP_WINDOW)
        if not dialogsContainer.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.LOBBY_MENU}):
            self.fireEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_MENU)), scope=EVENT_BUS_SCOPE.LOBBY)

    def onStartBattle(self):
        self.__stopUpdateScreen()

    def onStrongholdMaintenance(self, showWindow):
        self.__showBattleRoom()

    def onUnitFlagsChanged(self, flags, timeLeft):
        if not self.prbEntity.canShowStrongholdsBattleQueue():
            self.__showBattleRoom()

    def onUpdateHeader(self, header, isFirstBattle, isUnitFreezed):
        self.__battleQueueVO['title'] = self.__getTitle()
        self.as_setTypeInfoS(self.__battleQueueVO)
        self.__requestClanIcon()

    def _populate(self):
        super(BattleStrongholdsQueue, self)._populate()
        self._blur.enable()
        self.addListener(events.GameEvent.SHOW_EXTERNAL_COMPONENTS, self._onShowExternals, scope=EVENT_BUS_SCOPE.GLOBAL)
        self.addListener(events.GameEvent.HIDE_EXTERNAL_COMPONENTS, self._onHideExternals, scope=EVENT_BUS_SCOPE.GLOBAL)
        self.startPrbListening()
        self.addListener(events.StrongholdEvent.STRONGHOLD_ON_TIMER, self.__onMatchmakingTimerChanged, scope=EVENT_BUS_SCOPE.STRONGHOLD)
        g_playerEvents.onArenaCreated += self.onStartBattle
        if self.prbEntity is not None:
            permissions = self.prbEntity.getPermissions()
            self.as_showExitS(permissions.canStopBattleQueue())
        self.as_showWaitingS('')
        self.__battleQueueVO = self.__getBattleQueueVO()
        self.__requestClanIcon()
        MusicControllerWWISE.play()
        return

    def _dispose(self):
        self.__stopUpdateScreen()
        g_playerEvents.onArenaCreated -= self.onStartBattle
        self.stopPrbListening()
        self.removeListener(events.StrongholdEvent.STRONGHOLD_ON_TIMER, self.__onMatchmakingTimerChanged, scope=EVENT_BUS_SCOPE.STRONGHOLD)
        self.__imagesFetchCoordinator.fini()
        self.removeListener(events.GameEvent.SHOW_EXTERNAL_COMPONENTS, self._onShowExternals, scope=EVENT_BUS_SCOPE.GLOBAL)
        self.removeListener(events.GameEvent.HIDE_EXTERNAL_COMPONENTS, self._onHideExternals, scope=EVENT_BUS_SCOPE.GLOBAL)
        self._blur.fini()
        super(BattleStrongholdsQueue, self)._dispose()

    def __getBattleQueueVO(self):
        return {'iconLabel': constants.ARENA_GUI_TYPE_LABEL.LABELS[constants.ARENA_GUI_TYPE.SORTIE_2],
         'title': self.__getTitle(),
         'leagueIcon': '',
         'myClanIcon': '',
         'myClanName': '',
         'myClanElo': text_styles.highTitleDisabled('--'),
         'myClanRating': ''}

    def __requestClanIcon(self):
        myClanIcon = self.__battleQueueVO['myClanIcon']
        if not myClanIcon:
            entity = self.prbEntity
            if entity is not None and entity.isStrongholdSettingsValid():
                clan = entity.getStrongholdSettings().getHeader().getClan()
                self.requestClanEmblem32x32(clan.getId())
                self.__battleQueueVO['myClanName'] = getClanTag(clan.getTag(), clan.getColor())
        return

    def __getTitle(self):
        entity = self.prbEntity
        if entity is not None and entity.isStrongholdSettingsValid():
            header = entity.getStrongholdSettings().getHeader()
            if header.isSortie():
                level = int2roman(header.getMaxLevel())
                title = makeString(FORTIFICATIONS.STRONGHOLDINFO_SORTIE) % {'level': level}
            else:
                direction = vo_converters.getDirection(header.getDirection())
                title = makeString(FORTIFICATIONS.STRONGHOLDINFO_STRONGHOLD) % {'direction': direction}
        else:
            title = ''
        return title

    @adisp_async
    @adisp_process
    def __parseClanData(self, clanData, serviceLeaguesEnabled, callback):
        updateData = {}
        myClanName = getClanTag(clanData.get('tag'), clanData.get('color') or '')
        if myClanName:
            updateData['myClanName'] = myClanName
        myClanIcon = yield self.__imagesFetchCoordinator.fetchImageByUrl(clanData.get('emblem'), oneUse=False)
        if myClanIcon:
            updateData['myClanIcon'] = myClanIcon
        leagueIcon = yield self.__imagesFetchCoordinator.fetchImageByUrl(clanData.get('back_emblem'), oneUse=False)
        if leagueIcon:
            updateData['leagueIcon'] = leagueIcon
        if serviceLeaguesEnabled:
            myClanRating = clanData.get('position')
            if isinstance(myClanRating, int):
                textStyle = text_styles.highTitle
                updateData['myClanRating'] = textStyle(backport.getNiceNumberFormat(myClanRating))
            else:
                textStyle = text_styles.highTitleDisabled
                updateData['myClanRating'] = textStyle('--')
        else:
            textStyle = text_styles.highTitleDisabled
        myClanElo = clanData.get('elo')
        if isinstance(myClanElo, int):
            updateData['myClanElo'] = textStyle(backport.getNiceNumberFormat(myClanElo))
        callback(updateData)

    @adisp_async
    @adisp_process
    def __parseGroupsData(self, groupsData, callback):
        groups = []
        for group in groupsData:
            clans = []
            for clan in group.get('clans', []):
                clanVO = {'title': makeString(FORTIFICATIONS.BATTLEQUEUE_CLANPOSITION, position='--'),
                 'clanName': getClanTag(clan.get('tag'), clan.get('color') or ''),
                 'clanElo': '--',
                 'tooltip': ''}
                leagueIconUrl = clan.get('back_emblem')
                if leagueIconUrl:
                    clanVO['leagueIcon'] = yield self.__imagesFetchCoordinator.fetchImageByUrl(clan.get('back_emblem'), oneUse=False)
                    if not clanVO['leagueIcon']:
                        callback([])
                        return
                clanVO['clanIcon'] = yield self.__imagesFetchCoordinator.fetchImageByUrl(clan.get('emblem'), oneUse=False)
                if not clanVO['clanIcon']:
                    callback([])
                    return
                elo = clan.get('elo')
                if isinstance(elo, int):
                    clanVO['clanElo'] = backport.getNiceNumberFormat(elo)
                position = clan.get('position')
                if isinstance(position, int):
                    position = backport.getNiceNumberFormat(position)
                    clanVO['title'] = makeString(FORTIFICATIONS.BATTLEQUEUE_CLANPOSITION, position=position)
                clans.append(clanVO)

            groups.append({'title': group.get('title'),
             'leagues': clans})

        callback(groups)

    @adisp_process
    def __onMatchmakingInfo(self, response):
        if response.getCode() == ResponseCodes.NO_ERRORS and response.getData():
            data = response.getData()
            self.__animationDuration = data.get('animation_time', self.ANIMATION_DEFAULT_DURATION)
            groupsData = data.get('groups', [])
            updateData = yield self.__parseClanData(data.get('clan', {}), bool(groupsData))
            self.__battleQueueVO.update(updateData)
            self.as_setTypeInfoS(self.__battleQueueVO)
            self.__groups = yield self.__parseGroupsData(groupsData)

    def __stopUpdateScreen(self):
        if self.__timerCallback is not None:
            BigWorld.cancelCallback(self.__timerCallback)
            self.__timerCallback = None
        return

    def __onMatchmakingTimerChanged(self, event):
        data = event.ctx
        if data['dtime'] > 0 and data['textid'] in (TOOLTIPS.STRONGHOLDS_TIMER_SQUADINQUEUE, FORTIFICATIONS.ROSTERINTROWINDOW_INTROVIEW_FORTBATTLES_NEXTTIMEOFBATTLESOON):
            timerLabel = i18n.makeString(FORTIFICATIONS.BATTLEQUEUE_WAITBATTLE)
            currentTime = data['dtime']
        else:
            _, unit = self.prbEntity.getUnit()
            currentTime = 0
            if unit:
                timestamp = unit.getModalTimestamp()
                if timestamp:
                    currentTime = max(0, int(time_utils.getServerUTCTime() - timestamp))
            if data['isSortie'] or data['isFirstBattle']:
                timerLabel = i18n.makeString(FORTIFICATIONS.BATTLEQUEUE_SEARCHENEMY)
            else:
                timerLabel = i18n.makeString(FORTIFICATIONS.BATTLEQUEUE_WAITBATTLE)
        timeLabel = '%d:%02d' % divmod(currentTime, 60)
        self.as_setTimerS(timerLabel, timeLabel)
        n = len(self.__groups)
        if n != 0:
            self.as_hideWaitingS()
            if self.__startAnimationTime is None:
                self.__startAnimationTime = time_utils.getCurrentTimestamp()
            i, r = divmod(int(time_utils.getCurrentTimestamp() - self.__startAnimationTime), self.__animationDuration)
            if r == 0:
                self.as_setLeaguesS(self.__groups[i % n])
        return

    @staticmethod
    def __showBattleRoom():
        g_eventDispatcher.loadStrongholds()
        g_eventDispatcher.loadHangar()

    def _onHideExternals(self, _):
        self._blur.disable()

    def _onShowExternals(self, _):
        self._blur.enable()
