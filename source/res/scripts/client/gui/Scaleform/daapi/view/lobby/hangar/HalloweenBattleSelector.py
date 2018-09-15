# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/HalloweenBattleSelector.py
from gui.Scaleform.daapi.view.meta.HalloweenBattleSelectorMeta import HalloweenBattleSelectorMeta
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.prb_control.entities.listener import IGlobalListener
from constants import QUEUE_TYPE
from helpers import dependency
from skeletons.gui.game_control import IEventBattlesController
from skeletons.gui.server_events import IEventsCache
from CurrentVehicle import g_currentVehicle
from debug_utils import LOG_DEBUG_DEV
import BigWorld
_UPDATE_INTERVAL = 0.2

class HalloweenBattleSelector(HalloweenBattleSelectorMeta, IGlobalListener):
    eventBattlesCtrl = dependency.descriptor(IEventBattlesController)
    eventsCache = dependency.descriptor(IEventsCache)
    __background_alpha__ = 0
    __selected = None

    def onBossModeBtnClick(self):
        self._doSelect(QUEUE_TYPE.EVENT_BATTLES_2)

    def onPVPBtnClick(self):
        self._doSelect(QUEUE_TYPE.EVENT_BATTLES)

    def playerSelectionMade(self, isPVESelected):
        if isPVESelected:
            self.onBossModeBtnClick()
        else:
            self.onPVPBtnClick()

    def onEnqueued(self, queueType, *args):
        self.as_hideS()

    def onDequeued(self, queueType, *args):
        self.__updateHalloweenSettings()

    def onUnitFlagsChanged(self, flags, timeLeft):
        LOG_DEBUG_DEV('EventBattle Unit Flag Change', flags)
        if self.prbEntity.hasLockedState():
            LOG_DEBUG_DEV('[EventBattle] Entity Locked')
            if flags.isInSearch() or flags.isInQueue() or flags.isInArena():
                LOG_DEBUG_DEV('EventBattle Disabled', flags)
                self.as_disableButtonsS()
        else:
            self.as_enableButtonsS()
            if self.eventBattlesCtrl.getBattleType() != self.__selected:
                self.__matchSelectorWithBattleControl()

    def _populate(self):
        super(HalloweenBattleSelector, self)._populate()
        LOG_DEBUG_DEV('EventBattle Populate')
        self.startGlobalListening()
        self.eventBattlesCtrl.onSettingsChanged += self.__updateHalloweenSettings
        self.eventBattlesCtrl.onVehicleChanged += self.__updateHalloweenSettings
        self.eventsCache.onSyncCompleted += self._onEventsCacheResync
        self.as_initBattleSelectorS({'bossModeBattleTitleStr': INGAME_GUI.HALLOWEEN_LOBBY_BATTLETYPE_PVE_TITLE,
         'bossModeBattleBtnStr': INGAME_GUI.HALLOWEEN_LOBBY_BATTLETYPE_PVE_MESSAGE,
         'halloweenPVPTitleStr': INGAME_GUI.HALLOWEEN_LOBBY_BATTLETYPE_PVP_TITLE,
         'halloweenPVPBattleBtnStr': INGAME_GUI.HALLOWEEN_LOBBY_BATTLETYPE_PVP_MESSAGE})
        controlBattleType = self.eventBattlesCtrl.getBattleType()
        LOG_DEBUG_DEV('EventBattle On Populate Controller Battle Type', controlBattleType)
        if controlBattleType is not None:
            self._doSelect(controlBattleType)
        else:
            self.__selected = QUEUE_TYPE.EVENT_BATTLES_2
            LOG_DEBUG_DEV('[EventBattle] Setting selector to match: ', self.eventBattlesCtrl.getBattleType())
            self.as_startWithPvES(True)
        self.__updateHalloweenSettings()
        return

    def _dispose(self):
        LOG_DEBUG_DEV('EventBattle Dispose')
        self.stopGlobalListening()
        self.eventBattlesCtrl.onSettingsChanged -= self.__updateHalloweenSettings
        self.eventBattlesCtrl.onVehicleChanged -= self.__updateHalloweenSettings
        self.eventsCache.onSyncCompleted -= self._onEventsCacheResync
        super(HalloweenBattleSelector, self)._dispose()

    def __updateHalloweenSettings(self):
        LOG_DEBUG_DEV('Update EventBattle Settings')
        vehicle = g_currentVehicle
        if not self.eventBattlesCtrl.isEnabled() or vehicle is None or vehicle.item is None or 'event_battles' not in vehicle.item.tags:
            LOG_DEBUG_DEV('EventBattle Hidden')
            self.as_hideS()
        else:
            self.as_showS()
        if self.prbDispatcher.getFunctionalState().hasLockedState or not self.eventBattlesCtrl.canChangeBattleType():
            LOG_DEBUG_DEV('EventBattle Disabled')
            self.as_disableButtonsS()
        else:
            LOG_DEBUG_DEV('EventBattle Shown')
            self.as_enableButtonsS()
        self.__matchSelectorWithBattleControl()
        return

    def __matchSelectorWithBattleControl(self):
        LOG_DEBUG_DEV('[EventBattle] Setting selector to match: ', self.__selected, self.eventBattlesCtrl.getBattleType())
        self.__selected = self.eventBattlesCtrl.getBattleType()
        self.as_startWithPvES(self.__selected == QUEUE_TYPE.EVENT_BATTLES_2)

    def __doClose(self):
        pass

    def __updateTimerCallback(self):
        if self.eventBattlesCtrl.canChangeBattleType():
            self.as_enableButtonsS()
        else:
            BigWorld.callback(_UPDATE_INTERVAL, self.__updateTimerCallback)

    def _onEventsCacheResync(self):
        """
        Callback to be invoked when the event cache is re-synced.
        """
        self.__updateHalloweenSettings()

    def _doSelect(self, queueType):
        self.__selected = queueType
        if self.eventBattlesCtrl.canChangeBattleType():
            self.eventBattlesCtrl.setBattleType(queueType)
            LOG_DEBUG_DEV('DO ACTION: ', queueType)
            if self.prbEntity.isCommander():
                self.as_disableButtonsS()
                BigWorld.callback(_UPDATE_INTERVAL, self.__updateTimerCallback)
