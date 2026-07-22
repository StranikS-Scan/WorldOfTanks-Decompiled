# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/control/sales/triggers.py
import BigWorld
from CurrentVehicle import g_currentVehicle
from gui.techtree.research_items_data import ResearchItemsData
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from tutorial.control.triggers import Trigger, TriggerWithSubscription, TriggerWithValidateVar
from tutorial.logger import LOG_DEBUG
__all__ = ('TimerTrigger', 'IsCollectibleVehicleTrigger', 'CurrentVehicleChangedTrigger', 'ItemsCacheSyncTrigger', 'ResearchGoToNextVehicleTrigger')

class TimerTrigger(TriggerWithValidateVar):

    def __init__(self, triggerID, validateVarID, setVarID=None, validateUpdateOnly=False):
        super(TimerTrigger, self).__init__(triggerID, validateVarID, setVarID, validateUpdateOnly)
        self.__timerCallback = None
        return

    def run(self):
        self.isRunning = True
        if self.__timerCallback is None:
            self.isSubscribed = True
            self.__timerCallback = BigWorld.callback(self.getVar(), self.__updateTimer)
        self.toggle(isOn=False)
        return

    def clear(self):
        if self.__timerCallback is not None:
            BigWorld.cancelCallback(self.__timerCallback)
            self.__timerCallback = None
        self.isSubscribed = False
        self.isRunning = False
        return

    def __updateTimer(self, *args):
        self.__timerCallback = None
        self.toggle(isOn=True)
        return


class IsCollectibleVehicleTrigger(Trigger):

    def run(self):
        g_currentVehicle.onChanged += self.__onCurrentVehicleChanged
        self.toggle(isOn=self.isOn())

    def isOn(self, *args):
        return g_currentVehicle.isCollectible()

    def clear(self):
        g_currentVehicle.onChanged -= self.__onCurrentVehicleChanged

    def __onCurrentVehicleChanged(self):
        self.toggle(isOn=self.isOn())


class CurrentVehicleChangedTrigger(TriggerWithSubscription):

    def __init__(self, triggerID, validateVarID, setVarID=None, validateUpdateOnly=False, unlockTargetIDs=None):
        super(CurrentVehicleChangedTrigger, self).__init__(triggerID, validateVarID, setVarID, validateUpdateOnly)
        self.__unlockTargetIDs = unlockTargetIDs or []

    def _subscribe(self):
        g_currentVehicle.onChanged += self.__onCurrentVehicleChanged

    def _unsubscribe(self):
        g_currentVehicle.onChanged -= self.__onCurrentVehicleChanged

    def __onCurrentVehicleChanged(self):
        LOG_DEBUG('CurrentVehicleChangedTrigger.onChanged', self.getID())
        self._tutorial.invalidateFlags()
        for targetID in self.__unlockTargetIDs:
            LOG_DEBUG('CurrentVehicleChangedTrigger.unlockState', self.getID(), targetID)
            self._tutorial.unlockState(targetID)

        LOG_DEBUG('CurrentVehicleChangedTrigger.toggle', self.getID())
        self.toggle()


class ItemsCacheSyncTrigger(TriggerWithSubscription):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, triggerID, validateVarID, setVarID=None, validateUpdateOnly=False, unlockTargetIDs=None):
        super(ItemsCacheSyncTrigger, self).__init__(triggerID, validateVarID, setVarID, validateUpdateOnly)
        self.__unlockTargetIDs = unlockTargetIDs or []

    def _subscribe(self):
        self.itemsCache.onSyncCompleted += self.__onItemsCacheSyncCompleted

    def _unsubscribe(self):
        self.itemsCache.onSyncCompleted -= self.__onItemsCacheSyncCompleted

    def __onItemsCacheSyncCompleted(self, *_):
        LOG_DEBUG('ItemsCacheSyncTrigger.onSyncCompleted', self.getID())
        self._tutorial.invalidateFlags()
        for targetID in self.__unlockTargetIDs:
            LOG_DEBUG('ItemsCacheSyncTrigger.unlockState', self.getID(), targetID)
            self._tutorial.unlockState(targetID)

        LOG_DEBUG('ItemsCacheSyncTrigger.toggle', self.getID())
        self.toggle()


class ResearchGoToNextVehicleTrigger(TriggerWithSubscription):

    def __init__(self, triggerID, validateVarID, setVarID=None, validateUpdateOnly=False, unlockTargetIDs=None):
        super(ResearchGoToNextVehicleTrigger, self).__init__(triggerID, validateVarID, setVarID, validateUpdateOnly)
        self.__unlockTargetIDs = unlockTargetIDs or []

    def _subscribe(self):
        LOG_DEBUG('ResearchGoToNextVehicleTrigger.subscribe', self.getID())
        ResearchItemsData.onGoToNextVehicle += self.__onGoToNextVehicle

    def _unsubscribe(self):
        LOG_DEBUG('ResearchGoToNextVehicleTrigger.unsubscribe', self.getID())
        ResearchItemsData.onGoToNextVehicle -= self.__onGoToNextVehicle

    def run(self):
        self.isRunning = True
        LOG_DEBUG('ResearchGoToNextVehicleTrigger.run', self.getID(), self.isSubscribed)
        if not self.isSubscribed:
            self.isSubscribed = True
            self._subscribe()
        self.isRunning = False

    def __onGoToNextVehicle(self, oldRootCD, newRootCD):
        LOG_DEBUG('ResearchGoToNextVehicleTrigger.onGoToNextVehicle', self.getID(), oldRootCD, newRootCD)
        self._tutorial.invalidateFlags()
        for targetID in self.__unlockTargetIDs:
            LOG_DEBUG('ResearchGoToNextVehicleTrigger.unlockState', self.getID(), targetID)
            self._tutorial.unlockState(targetID)

        LOG_DEBUG('ResearchGoToNextVehicleTrigger.toggle', self.getID())
        self.toggle()
