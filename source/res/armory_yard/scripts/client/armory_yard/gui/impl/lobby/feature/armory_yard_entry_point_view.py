# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/lobby/feature/armory_yard_entry_point_view.py
from armory_yard.gui.impl.lobby.feature.tooltips.entry_point_active_tooltip_view import EntryPointActiveTooltipView
from armory_yard.gui.impl.lobby.feature.tooltips.entry_point_before_progression_tooltip_view import EntryPointBeforeProgressionTooltipView
from frameworks.wulf import ViewFlags, ViewSettings
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_entry_point_view_model import ArmoryYardEntryPointViewModel
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_main_view_model import TabId
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency, time_utils
from skeletons.gui.game_control import IArmoryYardController
from armory_yard_constants import State

class ArmoryYardEntryPointView(ViewImpl):
    __armoryYardCtrl = dependency.descriptor(IArmoryYardController)

    def __init__(self):
        settings = ViewSettings(layoutID=R.views.armory_yard.lobby.feature.ArmoryYardEntryPointView(), flags=ViewFlags.VIEW, model=ArmoryYardEntryPointViewModel())
        super(ArmoryYardEntryPointView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ArmoryYardEntryPointView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.armory_yard.lobby.feature.tooltips.EntryPointBeforeProgressionTooltipView():
            return EntryPointBeforeProgressionTooltipView()
        return EntryPointActiveTooltipView() if contentID == R.views.armory_yard.lobby.feature.tooltips.EntryPointActiveTooltipView() else super(ArmoryYardEntryPointView, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(ArmoryYardEntryPointView, self)._onLoading(*args, **kwargs)
        self.__updateModel()
        self.__armoryYardCtrl.onUpdated += self.__updateModel
        self.__armoryYardCtrl.onProgressUpdated += self.__updateModel
        self.__armoryYardCtrl.onQuestsUpdated += self.__updateModel

    def _finalize(self):
        super(ArmoryYardEntryPointView, self)._finalize()
        self.__armoryYardCtrl.onUpdated -= self.__updateModel
        self.__armoryYardCtrl.onProgressUpdated -= self.__updateModel
        self.__armoryYardCtrl.onQuestsUpdated -= self.__updateModel

    def _getEvents(self):
        return ((self.viewModel.onAction, self.__onActionClick),)

    def __updateModel(self, *_):
        if not self.__armoryYardCtrl.isEnabled():
            return
        else:
            currentTime = time_utils.getServerUTCTime()
            _, finishProgressionTime = self.__armoryYardCtrl.getProgressionTimes()
            deltaFinishProgressionTime = finishProgressionTime - currentTime
            state = self.__armoryYardCtrl.getState()
            availableQuestsCount = self.__armoryYardCtrl.getAvailableQuestsCount()
            if state == State.ACTIVE:
                nextCycle = self.__armoryYardCtrl.getNextCycle(currentTime)
                if nextCycle is not None and nextCycle.startDate - currentTime <= time_utils.ONE_DAY:
                    state = State.ACTIVE
                elif self.__armoryYardCtrl.isQuestActive() and availableQuestsCount == 0:
                    state = State.COMPLETED
            with self.viewModel.transaction() as model:
                model.setProgressionLevel(availableQuestsCount)
                model.setState(state)
                if deltaFinishProgressionTime < time_utils.ONE_DAY:
                    model.setEndTimestamp(deltaFinishProgressionTime)
            return

    def __onActionClick(self):
        self.__armoryYardCtrl.goToArmoryYard(tabId=TabId.QUESTS)
