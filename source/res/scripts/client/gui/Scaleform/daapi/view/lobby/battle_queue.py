# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/battle_queue.py
import weakref
import BigWorld
import MusicControllerWWISE
import constants
from CurrentVehicle import g_currentVehicle
from PlayerEvents import g_playerEvents
from adisp import process, async
from client_request_lib.exceptions import ResponseCodes
from debug_utils import LOG_DEBUG
from frameworks.wulf import WindowLayer
from gui import makeHtmlString
from gui.impl.gen import R
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.event_boards.formaters import getClanTag
from gui.Scaleform.daapi.view.lobby.rally import vo_converters
from gui.Scaleform.daapi.view.meta.BattleQueueMeta import BattleQueueMeta
from gui.Scaleform.daapi.view.meta.BattleStrongholdsQueueMeta import BattleStrongholdsQueueMeta
from gui.shared.view_helpers.blur_manager import CachedBlur
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.impl import backport
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.prb_control import prb_getters, prbEntityProperty
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME, getTypeBigIconPath
from gui.shared.view_helpers import ClanEmblemsHelper
from gui.shared.image_helper import getTextureLinkByID, ImagesFetchCoordinator
from gui.sounds.ambients import BattleQueueEnv
from helpers import dependency, i18n, time_utils, int2roman
from helpers.i18n import makeString
from skeletons.gui.lobby_context import ILobbyContext
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from gui.Scaleform.locale.MENU import MENU
from skeletons.gui.shared import IItemsCache
TYPES_ORDERED = (('heavyTank', ITEM_TYPES.VEHICLE_TAGS_HEAVY_TANK_NAME),
 ('mediumTank', ITEM_TYPES.VEHICLE_TAGS_MEDIUM_TANK_NAME),
 ('lightTank', ITEM_TYPES.VEHICLE_TAGS_LIGHT_TANK_NAME),
 ('AT-SPG', ITEM_TYPES.VEHICLE_TAGS_AT_SPG_NAME),
 ('SPG', ITEM_TYPES.VEHICLE_TAGS_SPG_NAME))
_HTMLTEMP_PLAYERSLABEL = 'html_templates:lobby/queue/playersLabel'

@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def _needShowLongWaitingWarning(lobbyContext=None):
    vehicle = g_currentVehicle.item
    return lobbyContext is not None and vehicle is not None


class _QueueProvider(object):

    def __init__(self, proxy, qType=constants.QUEUE_TYPE.UNKNOWN):
        super(_QueueProvider, self).__init__()
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
            LOG_DEBUG('Requestion queue info: ', self._queueType)
            currPlayer.requestQueueInfo(self._queueType)
            self._queueCallback = BigWorld.callback(5, self.requestQueueInfo)
        return

    def processQueueInfo(self, qInfo):
        pass

    def needAdditionalInfo(self):
        return False

    def additionalInfo(self):
        pass

    def getTankInfoLabel(self):
        return makeString(MENU.PREBATTLE_TANKLABEL)

    def getTankIcon(self, vehicle):
        return getTypeBigIconPath(vehicle.type)

    def getLayoutStr(self):
        pass

    def forceStart(self):
        currPlayer = BigWorld.player()
        if currPlayer is not None and hasattr(currPlayer, 'createArenaFromQueue'):
            currPlayer.createArenaFromQueue()
        return


class _RandomQueueProvider(_QueueProvider):

    def __init__(self, proxy, qType=constants.QUEUE_TYPE.UNKNOWN):
        super(_RandomQueueProvider, self).__init__(proxy, qType)
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
            self._needAdditionalInfo = _needShowLongWaitingWarning()
        return self._needAdditionalInfo

    def additionalInfo(self):
        warning = text_styles.concatStylesToSingleLine('*', makeString(MENU.PREBATTLE_WAITINGTIMEWARNING))
        return text_styles.alert(warning)

    @staticmethod
    def _isStartButtonDisplayed(vClasses):
        return constants.IS_DEVELOPMENT and sum(vClasses) > 1

    def _createCommonPlayerString(self, playerCount):
        self._proxy.flashObject.as_setPlayers(makeHtmlString(_HTMLTEMP_PLAYERSLABEL, 'players', {'count': playerCount}))


class _EpicQueueProvider(_RandomQueueProvider):

    def forceStart(self):
        currPlayer = BigWorld.player()
        if currPlayer is not None and hasattr(currPlayer, 'forceEpicDevStart'):
            currPlayer.forceEpicDevStart()
        return

    def getTankInfoLabel(self):
        return makeString(MENU.PREBATTLE_STARTINGTANKLABEL)


class _EventQueueProvider(_RandomQueueProvider):
    pass


class _RankedQueueProvider(_RandomQueueProvider):
    pass


class _BattleRoyaleQueueProvider(_RandomQueueProvider):

    def processQueueInfo(self, qInfo):
        playersCount = qInfo.get('players', 0)
        self._createCommonPlayerString(playersCount)
        modesData = []
        for mode in constants.BattleRoyaleMode.ALL:
            modesData.append({'type': backport.text(R.strings.menu.prebattle.battleRoyale.dyn(mode)()),
             'icon': RES_ICONS.getBattleRoyaleModeIconPath(mode),
             'count': qInfo.get(mode, 0)})

        self._proxy.as_setDPS(modesData)

    def getTankIcon(self, vehicle):
        return RES_ICONS.getBattleRoyaleTankIconPath(vehicle.nationName)

    def getLayoutStr(self):
        pass


_PROVIDER_BY_QUEUE_TYPE = {constants.QUEUE_TYPE.RANDOMS: _RandomQueueProvider,
 constants.QUEUE_TYPE.EVENT_BATTLES: _EventQueueProvider,
 constants.QUEUE_TYPE.RANKED: _RankedQueueProvider,
 constants.QUEUE_TYPE.EPIC: _EpicQueueProvider,
 constants.QUEUE_TYPE.BATTLE_ROYALE: _BattleRoyaleQueueProvider}

def _providerFactory(proxy, qType):
    return _PROVIDER_BY_QUEUE_TYPE.get(qType, _QueueProvider)(proxy, qType)


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
        self.fireEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.HERO_TANK_MARKER, ctx={'isDisable': True}), EVENT_BUS_SCOPE.LOBBY)
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
        self.fireEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.HERO_TANK_MARKER, ctx={'isDisable': False}), EVENT_BUS_SCOPE.LOBBY)
        super(BattleQueue, self)._dispose()

    def __updateClientState(self):
        if self.prbEntity is None:
            return
        else:
            permissions = self.prbEntity.getPermissions()
            if not permissions.canExitFromQueue():
                self.as_showExitS(False)
            guiType = prb_getters.getArenaGUIType(queueType=self.__provider.getQueueType())
            title = MENU.loading_battletypes(guiType)
            description = MENU.loading_battletypes_desc(guiType)
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
            tankName = vehicle.shortUserName
            iconPath = self.__provider.getTankIcon(vehicle)
            layoutStr = self.__provider.getLayoutStr()
            self.as_setTypeInfoS({'iconLabel': iconlabel,
             'title': title,
             'description': description,
             'additional': additional,
             'tankLabel': text_styles.main(textLabel),
             'tankIcon': iconPath,
             'tankName': tankName,
             'layoutStr': layoutStr})
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
        self.fireEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.HERO_TANK_MARKER, ctx={'isDisable': True}), EVENT_BUS_SCOPE.LOBBY)
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
        self.fireEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.HERO_TANK_MARKER, ctx={'isDisable': False}), EVENT_BUS_SCOPE.LOBBY)
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

    @async
    @process
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
            textStyle = text_styles.highTitle
        myClanElo = clanData.get('elo')
        if isinstance(myClanElo, int):
            updateData['myClanElo'] = textStyle(backport.getNiceNumberFormat(myClanElo))
        callback(updateData)

    @async
    @process
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

    @process
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
