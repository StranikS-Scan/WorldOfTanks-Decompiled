# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/veh_post_progression/veh_post_progression_entry_point.py
import typing
from account_helpers import AccountSettings
from account_helpers.AccountSettings import BECOME_ELITE_VEHICLES_WATCHED
from gui.Scaleform.daapi.view.meta.ResearchMeta import ResearchMeta
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.Scaleform.genConsts.POSTPROGRESSION_CONSTS import POSTPROGRESSION_CONSTS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared import events
from gui.veh_post_progression.helpers import needToShowCounter
from soft_exception import SoftException
from gui.shared.gui_items.Vehicle import Vehicle
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import EliteStatusProgress

def _validateVehicle(vehicle):
    if not isinstance(vehicle, Vehicle):
        raise SoftException('vehicle has to be valid gui_items.Vehicle, got: {}'.format(vehicle))


class VehPostProgressionEntryPoint(EventSystemEntity):
    __slots__ = ('_eliteWatchedList', '_watchedListDirty', '_parentObj', '_vehicle', '_modulesToUnlock')

    def __init__(self, parentObj):
        super(VehPostProgressionEntryPoint, self).__init__()
        self._addListeners()
        self._eliteWatchedList = AccountSettings.getSettings(BECOME_ELITE_VEHICLES_WATCHED)
        self._parentObj = parentObj
        self._vehicle = None
        self._watchedListDirty = False
        self._modulesToUnlock = set()
        return

    def dispose(self):
        if self._watchedListDirty:
            AccountSettings.setSettings(BECOME_ELITE_VEHICLES_WATCHED, self._eliteWatchedList)
        self._removeListeners()
        self._eliteWatchedList = None
        self._parentObj = None
        self._vehicle = None
        return

    def redraw(self, vehicle):
        _validateVehicle(vehicle)
        self._vehicle = vehicle
        self.__updatePostProgressionData()

    def invalidateUnlocks(self, unlocks):
        if any((cd in self._modulesToUnlock for cd, _ in unlocks)):
            self.__updatePostProgressionData()

    @property
    def isUnlockShowed(self):
        return self._vehicle.intCD in self._eliteWatchedList

    def tryUnlock(self):
        if not self._vehicle:
            return
        if self._vehicle.postProgressionAvailability(unlockOnly=True) and not self.isUnlockShowed:
            self._eliteWatchedList.add(self._vehicle.intCD)
            self.__updatePostProgressionData()
            self._parentObj.as_showPostProgressionUnlockAnimationS()
            self._watchedListDirty = True

    def _addListeners(self):
        self.addListener(events.CloseWindowEvent.ELITE_WINDOW_CLOSED, self.__onEliteWindowClosed)
        self.addListener(events.CloseWindowEvent.BUY_VEHICLE_VIEW_CLOSED, self.__onBuyVehicleWindowClosed)

    def _removeListeners(self):
        self.removeListener(events.CloseWindowEvent.ELITE_WINDOW_CLOSED, self.__onEliteWindowClosed)
        self.removeListener(events.CloseWindowEvent.BUY_VEHICLE_VIEW_CLOSED, self.__onBuyVehicleWindowClosed)

    def __onEliteWindowClosed(self, _):
        self.tryUnlock()

    def __onBuyVehicleWindowClosed(self, event):
        if not event.isAgree:
            self.tryUnlock()

    def __updatePostProgressionData(self):
        self._parentObj.as_setPostProgressionDataS(self.__getPostProgressionData())

    def __getPostProgressionData(self):
        vehicle = self._vehicle
        if not vehicle or not vehicle.isPostProgressionExists:
            return {'state': POSTPROGRESSION_CONSTS.RESEARCH_STATE_HIDDEN}
        eliteProgress = vehicle.getEliteStatusProgress()
        self._modulesToUnlock = eliteProgress.toUnlock
        return {'state': self.__getUnlockState(),
         'vehicleId': vehicle.intCD,
         'moduleIds': eliteProgress.toUnlock,
         'label': self.__getLabel(eliteProgress),
         'showCounter': needToShowCounter(vehicle)}

    def __getLabel(self, eliteProgress):
        isPurchased = self._vehicle.isPurchased
        fullyUnlocked = not eliteProgress.toUnlock
        label = R.strings.veh_post_progression.researchEntry.status
        labelResId = None
        if self._vehicle.postProgressionAvailability(unlockOnly=True):
            return ''
        else:
            if not isPurchased and not fullyUnlocked:
                labelResId = label.notResearchedNotPurchased
            elif not isPurchased:
                labelResId = label.notPurchased
            elif not fullyUnlocked:
                labelResId = label.notResearched
            return labelResId and backport.text(labelResId())

    def __getUnlockState(self):
        return POSTPROGRESSION_CONSTS.RESEARCH_STATE_UNLOCKED if self._vehicle.postProgressionAvailability(unlockOnly=True) and self.isUnlockShowed else POSTPROGRESSION_CONSTS.RESEARCH_STATE_LOCKED
