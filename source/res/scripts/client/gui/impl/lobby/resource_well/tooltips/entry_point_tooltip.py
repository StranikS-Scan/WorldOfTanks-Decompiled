# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/resource_well/tooltips/entry_point_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.resource_well.tooltips.entry_point_tooltip_model import EntryPointTooltipModel, EventState
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.resource_well.resource_well_helpers import isEventEndingsSoon, getSerialNumber, isForbiddenAccount
from helpers import dependency, time_utils
from skeletons.gui.game_control import IResourceWellController
from tutorial.control.game_vars import getVehicleByIntCD

class EntryPointTooltip(ViewImpl):
    __slots__ = ()
    __resourceWell = dependency.descriptor(IResourceWellController)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.resource_well.tooltips.EntryPointTooltip())
        settings.model = EntryPointTooltipModel()
        super(EntryPointTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(EntryPointTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(EntryPointTooltip, self)._onLoading(*args, **kwargs)
        self.__resourceWell.startNumberRequesters()
        with self.viewModel.transaction() as model:
            self.__fillEventTime(model=model)
            self.__fillRewardInfo(model=model)
            model.setVehicleName(getVehicleByIntCD(self.__resourceWell.getRewardVehicle()).userName)

    def _finalize(self):
        self.__resourceWell.stopNumberRequesters()
        super(EntryPointTooltip, self)._finalize()

    def _getEvents(self):
        return ((self.__resourceWell.onNumberRequesterUpdated, self.__fillRewardInfo), (self.__resourceWell.onEventUpdated, self.__fillEventTime))

    @replaceNoneKwargsModel
    def __fillEventTime(self, model=None):
        model.setEndDate(round(time_utils.makeLocalServerTime(self.__resourceWell.getFinishTime()), -1))
        model.setStartDate(round(time_utils.makeLocalServerTime(self.__resourceWell.getStartTime()), -1))
        isEventEnding = isEventEndingsSoon(resourceWell=self.__resourceWell)
        model.setIsEventEndingSoon(isEventEnding)
        if isEventEnding:
            model.setTimeLeft(self.__resourceWell.getFinishTime() - time_utils.getServerUTCTime())

    @replaceNoneKwargsModel
    def __fillRewardInfo(self, model=None):
        count = 0
        if self.__resourceWell.isCompleted():
            serialNumber = getSerialNumber(resourceWell=self.__resourceWell)
            state = EventState.TOPREWARDRECEIVED if serialNumber else EventState.REGULARREWARDRECEIVED
        elif isForbiddenAccount(resourceWell=self.__resourceWell):
            state = EventState.FORBIDDEN
        elif self.__resourceWell.isPaused():
            state = EventState.PAUSED
        elif self.__resourceWell.isNotStarted():
            state = EventState.NOTSTARTED
        else:
            state, count = self.__getRewardCountState()
        model.setRewardCount(count)
        model.setEventState(state)

    def __getRewardCountState(self):
        topRewardCount = self.__resourceWell.getRewardLeftCount(True)
        regularRewardCount = self.__resourceWell.getRewardLeftCount(False)
        if topRewardCount:
            return (EventState.TOPREWARDAVAILABLE, topRewardCount)
        return (EventState.REGULARREWARDAVAILABLE, regularRewardCount) if regularRewardCount else (EventState.NOREWARDS, 0)
