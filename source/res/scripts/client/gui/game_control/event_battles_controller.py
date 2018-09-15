# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/event_battles_controller.py
import weakref
import Event
import account_helpers
from adisp import process
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from debug_utils import LOG_ERROR
from gui.prb_control.entities.base.ctx import LeavePrbAction
from gui.prb_control.entities.event.squad.ctx import ChangeEventQueueTypeCtx
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.storages import prequeue_storage_getter
from gui.shared.items_cache import CACHE_SYNC_REASON
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IEventBattlesController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from debug_utils import LOG_DEBUG_DEV
from CurrentVehicle import g_currentVehicle
from gui.prb_control import prb_getters

class _BaseDataStorage(IGlobalListener):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, proxy):
        super(_BaseDataStorage, self).__init__()
        self._proxy = weakref.proxy(proxy)

    def init(self):
        LOG_DEBUG_DEV('EventBattle Base Data Init')
        self.startGlobalListening()
        self._proxy.onSettingsChanged()

    def fini(self):
        self.stopGlobalListening()

    def isEnabled(self):
        LOG_DEBUG_DEV('EventBattle Base Enabled: False')
        return False

    def setEnabled(self, isEnabled):
        pass

    def getBattleType(self):
        LOG_DEBUG_DEV('EventBattle Base Get Battle: False')
        return QUEUE_TYPE.UNKNOWN

    def setBattleType(self, battleType):
        pass

    def addSelectedVehicle(self, vehInvID):
        pass

    def removeSelectedVehicle(self, vehInvID):
        pass

    def moveSelectedVehicle(self, vehInvID):
        pass

    def getSelectedSlots(self):
        pass

    def canChangeBattleType(self):
        return False


class _UserDataStorage(_BaseDataStorage):
    settingsCore = dependency.descriptor(ISettingsCore)

    @prequeue_storage_getter(QUEUE_TYPE.EVENT)
    def eventBattleStorage(self):
        return None

    def init(self):
        super(_UserDataStorage, self).init()
        LOG_DEBUG_DEV('EventBattle User Data Init')
        self.itemsCache.onSyncCompleted += self.__onItemsResync
        self.settingsCore.onSettingsChanged += self.__onSettingsResync

    def fini(self):
        self.itemsCache.onSyncCompleted -= self.__onItemsResync
        self.settingsCore.onSettingsChanged -= self.__onSettingsResync
        super(_UserDataStorage, self).fini()

    def isEnabled(self):
        LOG_DEBUG_DEV('EventBattle User Enabled')
        return self.eventBattleStorage.isEnabled()

    def getBattleType(self):
        LOG_DEBUG_DEV('EventBattle user data get battle type', self.eventBattleStorage.getBattleType())
        return self.eventBattleStorage.getBattleType()

    def setBattleType(self, battleType):
        LOG_DEBUG_DEV('EventBattle UserData set battle type', battleType)
        self.eventBattleStorage.setBattleType(battleType)

    def canChangeBattleType(self):
        return True

    def __onItemsResync(self, updateReason, _):
        if updateReason in (CACHE_SYNC_REASON.INVENTORY_RESYNC, CACHE_SYNC_REASON.CLIENT_UPDATE):
            self.eventBattleStorage.validateSelectedVehicle()
        if not (self.isEnabled() and self._proxy.isAvailable()) and self.prbDispatcher is not None and self.prbDispatcher.getFunctionalState().isInEventEntity():
            self.__leave()
        return

    def __onSettingsResync(self, diff):
        if {'halloweenBattleType', 'isEnabled'} & set(diff.keys()):
            self.eventBattleStorage.validateSelectedVehicle()
            self._proxy.onSettingsChanged()

    @process
    def __leave(self):
        yield self.prbDispatcher.doLeaveAction(LeavePrbAction())


class _EventSquadDataStorage(_BaseDataStorage):

    def __init__(self, proxy, battleType=QUEUE_TYPE.EVENT_BATTLES):
        super(_EventSquadDataStorage, self).__init__(proxy)
        self.__vehicles = []
        if battleType not in QUEUE_TYPE.EVENT:
            battleType = QUEUE_TYPE.EVENT_BATTLES
        self.eventBattleStorage.setBattleType(battleType)

    @prequeue_storage_getter(QUEUE_TYPE.EVENT)
    def eventBattleStorage(self):
        return None

    def init(self):
        self.__matchPrbEntityQueueType()
        prb_getters.getUnit(safe=True).onUnitUpdated += self.onUnitUpdated
        prb_getters.getUnit(safe=True).onUnitVehiclesChanged += self.onUnitVehiclesChanged
        super(_EventSquadDataStorage, self).init()

    def fini(self):
        self.__vehicles = []
        super(_EventSquadDataStorage, self).fini()

    def isEnabled(self):
        LOG_DEBUG_DEV('EventBattle User Enabled')
        return self.eventBattleStorage.isEnabled()

    def getBattleType(self):
        return self.eventBattleStorage.getBattleType()

    def setBattleType(self, battleType):
        if battleType != self.getBattleType():
            if not self.canChangeBattleType():
                LOG_ERROR('Cannot change battle type!', battleType)
                return
            LOG_DEBUG_DEV('EventBattle UserData set battle type', battleType)
            self.eventBattleStorage.setBattleType(battleType)
            self.__setEventType(battleType)

    def canChangeBattleType(self):
        return self.prbEntity.canChangeBattleType() if self.prbEntity.getQueueType() == QUEUE_TYPE.EVENT_BATTLES or self.prbEntity.getQueueType() == QUEUE_TYPE.EVENT_BATTLES_2 else False

    def onUnitUpdated(self):
        self.__matchPrbEntityQueueType()
        LOG_DEBUG_DEV('[EventBattle] Unit Updated: ', self.eventBattleStorage.getBattleType())
        self._proxy.onSettingsChanged()

    def onUnitVehiclesChanged(self, dbID, vInfos):
        if dbID == account_helpers.getAccountDatabaseID():
            self._proxy.onVehicleChanged()

    def onUnitPlayerRolesChanged(self, pInfo, pPermissions):
        if pInfo.isCurrentPlayer():
            self._proxy.onSettingsChanged()

    def __matchPrbEntityQueueType(self):
        if self.prbEntity.getQueueType() == QUEUE_TYPE.EVENT_BATTLES or self.prbEntity.getQueueType() == QUEUE_TYPE.EVENT_BATTLES_2:
            self.eventBattleStorage.setBattleType(self.prbEntity.getQueueType())

    @process
    def __setEventType(self, eventType):
        if self.prbDispatcher is not None:
            yield self.prbDispatcher.sendPrbRequest(ChangeEventQueueTypeCtx(eventType, 'prebattle/change_settings'))
        else:
            yield lambda callback: callback(True)
        return


class EventBattlesController(IEventBattlesController, IGlobalListener):
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        super(EventBattlesController, self).__init__()
        self.__evtManager = Event.EventManager()
        self.onSettingsChanged = Event.Event(self.__evtManager)
        self.onVehicleChanged = Event.Event(self.__evtManager)
        self.onSquadStatusChanged = Event.Event(self.__evtManager)
        self.__dataStorage = None
        return

    def init(self):
        self.__dataStorage = _BaseDataStorage(self)

    def fini(self):
        self.__evtManager.clear()
        self.__dataStorage = None
        g_currentVehicle.onChanged -= self.onVehicleChanged
        return

    def onLobbyStarted(self, event):
        LOG_DEBUG_DEV('Start EventBattle CONTROLLER')
        g_currentVehicle.onChanged += self.onVehicleChanged

    def onLobbyInited(self, event):
        self.startGlobalListening()
        LOG_DEBUG_DEV('Init EventBattle CONTROLLER')
        unitFunc = self.prbEntity
        if unitFunc is not None:
            LOG_DEBUG_DEV('EventBattle Unit', unitFunc, unitFunc.getEntityType())
            if unitFunc.getEntityType() in PREBATTLE_TYPE.EVENT_PREBATTLES:
                LOG_DEBUG_DEV('EventBattle SQUAD DATA')
                self.__dataStorage = _EventSquadDataStorage(self)
            else:
                LOG_DEBUG_DEV('EventBattle USER DATA')
                self.__dataStorage = _UserDataStorage(self)
        if self.__dataStorage is not None:
            self.__dataStorage.init()
        return

    def onAvatarBecomePlayer(self):
        self.__stop()

    def onDisconnected(self):
        self.__stop()

    def isAvailable(self):
        return self.eventsCache.isEventEnabled()

    def isEnabled(self):
        return self.isAvailable() and self.__dataStorage.isEnabled()

    def isSelected(self):
        return self.isEnabled()

    def setEnabled(self, isEnabled):
        self.__dataStorage.setEnabled(isEnabled)

    def getBattleType(self):
        return self.__dataStorage.getBattleType()

    def setBattleType(self, battleType):
        self.__dataStorage.setBattleType(battleType)

    def canChangeBattleType(self):
        return self.__dataStorage.canChangeBattleType()

    def _setStorageType(self):
        if self.prbDispatcher is None:
            return
        else:
            funcState = self.prbDispatcher.getFunctionalState()
            if (funcState.isQueueSelected(QUEUE_TYPE.EVENT_BATTLES) or funcState.isQueueSelected(QUEUE_TYPE.EVENT_BATTLES_2)) and funcState.isInUnit():
                LOG_DEBUG_DEV('EventBattle IN EVENT SQUAD')
                lastType = self.__dataStorage.getBattleType()
                self.__dataStorage.fini()
                self.__dataStorage = _EventSquadDataStorage(self, battleType=lastType)
                self.__dataStorage.init()
            elif funcState.isQueueSelected(QUEUE_TYPE.RANDOMS):
                LOG_DEBUG_DEV('EventBattle IN non-event battle')
                self.__dataStorage.fini()
                self.__dataStorage = _UserDataStorage(self)
                self.__dataStorage.init()
            else:
                LOG_DEBUG_DEV('EventBattle in other queue: ')
                self.__dataStorage.fini()
                self.__dataStorage = _BaseDataStorage(self)
                self.__dataStorage.init()
            self.onSettingsChanged()
            self.onSquadStatusChanged(funcState.isInUnit())
            return

    def onPrbEntitySwitched(self):
        LOG_DEBUG_DEV('EventBattle PRB SWITCH')
        self._setStorageType()

    def __stop(self):
        self.__dataStorage.fini()
        self.__dataStorage = _BaseDataStorage(self)
        self.stopGlobalListening()
