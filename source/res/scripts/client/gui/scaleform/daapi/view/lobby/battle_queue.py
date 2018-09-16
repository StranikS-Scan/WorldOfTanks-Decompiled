# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/battle_queue.py
import weakref
import BigWorld
import MusicControllerWWISE
import constants
from CurrentVehicle import g_currentVehicle
from PlayerEvents import g_playerEvents
from debug_utils import LOG_DEBUG
from gui import makeHtmlString
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.BattleQueueMeta import BattleQueueMeta
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.prb_control import prb_getters, prbEntityProperty
from gui.Scaleform.locale.MENU import MENU
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME
from gui.sounds.ambients import BattleQueueEnv
from helpers import dependency
from helpers.i18n import makeString
from skeletons.gui.lobby_context import ILobbyContext
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
TYPES_ORDERED = (('heavyTank', ITEM_TYPES.VEHICLE_TAGS_HEAVY_TANK_NAME),
 ('mediumTank', ITEM_TYPES.VEHICLE_TAGS_MEDIUM_TANK_NAME),
 ('lightTank', ITEM_TYPES.VEHICLE_TAGS_LIGHT_TANK_NAME),
 ('AT-SPG', ITEM_TYPES.VEHICLE_TAGS_AT_SPG_NAME),
 ('SPG', ITEM_TYPES.VEHICLE_TAGS_SPG_NAME))
_LONG_WAITING_LEVELS = (9, 10)
_HTMLTEMP_PLAYERSLABEL = 'html_templates:lobby/queue/playersLabel'

def _getVehicleIconPath(vClass):
    return RES_ICONS.maps_icons_vehicletypes('big/{}.png'.format(vClass))


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def _needShowLongWaitingWarning(lobbyContext=None):
    vehicle = g_currentVehicle.item
    return lobbyContext is not None and lobbyContext.getServerSettings().isTemplateMatchmakerEnabled() and vehicle.type == VEHICLE_CLASS_NAME.SPG and vehicle.level in _LONG_WAITING_LEVELS


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
        self._proxy.flashObject.as_setPlayers(makeHtmlString(_HTMLTEMP_PLAYERSLABEL, 'players', {'count': sum(vClasses)}))
        if vClassesLen:
            vClassesData = []
            for vClass, message in TYPES_ORDERED:
                idx = constants.VEHICLE_CLASS_INDICES[vClass]
                vClassesData.append({'type': message,
                 'icon': _getVehicleIconPath(vClass),
                 'count': vClasses[idx] if idx < vClassesLen else 0})

            self._proxy.as_setDPS(vClassesData)
        self._proxy.as_showStartS(constants.IS_DEVELOPMENT and sum(vClasses) > 1)

    def needAdditionalInfo(self):
        if self._needAdditionalInfo is None:
            self._needAdditionalInfo = _needShowLongWaitingWarning()
        return self._needAdditionalInfo

    def additionalInfo(self):
        return text_styles.main(makeString(MENU.PREBATTLE_WAITINGTIMEWARNING))


class _EventQueueProvider(_RandomQueueProvider):
    pass


class _RankedQueueProvider(_RandomQueueProvider):
    pass


_PROVIDER_BY_QUEUE_TYPE = {constants.QUEUE_TYPE.RANDOMS: _RandomQueueProvider,
 constants.QUEUE_TYPE.EVENT_BATTLES: _EventQueueProvider,
 constants.QUEUE_TYPE.RANKED: _RankedQueueProvider}

def _providerFactory(proxy, qType):
    return _PROVIDER_BY_QUEUE_TYPE.get(qType, _QueueProvider)(proxy, qType)


class BattleQueue(BattleQueueMeta, LobbySubView):
    __sound_env__ = BattleQueueEnv

    def __init__(self, ctx=None):
        super(BattleQueue, self).__init__()
        self.__createTime = 0
        self.__timerCallback = None
        self.__provider = None
        return

    @prbEntityProperty
    def prbEntity(self):
        return None

    def onEscape(self):
        dialogsContainer = self.app.containerManager.getContainer(ViewTypes.TOP_WINDOW)
        if not dialogsContainer.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.LOBBY_MENU}):
            self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_MENU), scope=EVENT_BUS_SCOPE.LOBBY)

    def startClick(self):
        currPlayer = BigWorld.player()
        if currPlayer is not None and hasattr(currPlayer, 'createArenaFromQueue'):
            currPlayer.createArenaFromQueue()
        return

    def exitClick(self):
        self.prbEntity.exitFromQueue()

    def onStartBattle(self):
        self.__stopUpdateScreen()

    def _populate(self):
        super(BattleQueue, self)._populate()
        g_playerEvents.onArenaCreated += self.onStartBattle
        self.__updateQueueInfo()
        self.__updateTimer()
        self.__updateClientState()
        MusicControllerWWISE.play(MusicControllerWWISE.MUSIC_EVENT_LOBBY)
        MusicControllerWWISE.play(MusicControllerWWISE.AMBIENT_EVENT_LOBBY)

    def _dispose(self):
        self.__stopUpdateScreen()
        g_playerEvents.onArenaCreated -= self.onStartBattle
        super(BattleQueue, self)._dispose()

    def __updateClientState(self):
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
        textLabel = makeString(MENU.PREBATTLE_TANKLABEL)
        tankName = vehicle.shortUserName
        iconPath = _getVehicleIconPath(vehicle.type)
        self.as_setTypeInfoS({'iconLabel': iconlabel,
         'title': title,
         'description': description,
         'additional': additional,
         'tankLabel': text_styles.main(textLabel),
         'tankIcon': iconPath,
         'tankName': tankName})

    def __stopUpdateScreen(self):
        if self.__timerCallback is not None:
            BigWorld.cancelCallback(self.__timerCallback)
            self.__timerCallback = None
        if self.__provider is not None:
            self.__provider.stop()
            self.__provider = None
        return

    def __updateQueueInfo(self):
        qType = self.prbEntity.getQueueType()
        self.__provider = _providerFactory(self, qType)
        self.__provider.start()

    def __updateTimer(self):
        self.__timerCallback = None
        self.__timerCallback = BigWorld.callback(1, self.__updateTimer)
        textLabel = text_styles.main(makeString(MENU.PREBATTLE_TIMERLABEL))
        timeLabel = '%d:%02d' % divmod(self.__createTime, 60)
        if self.__provider.needAdditionalInfo():
            timeLabel = text_styles.concatStylesToSingleLine(timeLabel, '*')
        self.as_setTimerS(textLabel, timeLabel)
        self.__createTime += 1
        return
