# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/lobby/feature/armory_yard_hangar_widget_view.py
from frameworks.wulf import ViewFlags, ViewSettings
from armory_yard_constants import State
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_carousel_widget_view_model import ArmoryYardCarouselWidgetViewModel
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency
from helpers.time_utils import getServerUTCTime
from skeletons.gui.game_control import IArmoryYardController, IBootcampController
from skeletons.gui.hangar import ICarouselEventEntry

class ArmoryYardCarouselWidgetView(ViewImpl, ICarouselEventEntry):
    __slots__ = ()
    __armoryYardCtrl = dependency.descriptor(IArmoryYardController)
    __bootcampCtrl = dependency.descriptor(IBootcampController)

    @staticmethod
    def getIsActive(state):
        return ArmoryYardCarouselWidgetView.__armoryYardCtrl.isEnabled() and not ArmoryYardCarouselWidgetView.__bootcampCtrl.isInBootcamp()

    def __init__(self):
        settings = ViewSettings(layoutID=R.views.armory_yard.lobby.feature.ArmoryYardWidgetView(), flags=ViewFlags.COMPONENT, model=ArmoryYardCarouselWidgetViewModel())
        super(ArmoryYardCarouselWidgetView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ArmoryYardCarouselWidgetView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(ArmoryYardCarouselWidgetView, self)._onLoading(*args, **kwargs)
        self.__updateModel()
        self.__armoryYardCtrl.onUpdated += self.__updateModel
        self.__armoryYardCtrl.onProgressUpdated += self.__updateModel
        self.__armoryYardCtrl.onQuestsUpdated += self.__updateModel

    def _finalize(self):
        super(ArmoryYardCarouselWidgetView, self)._finalize()
        self.__armoryYardCtrl.onUpdated -= self.__updateModel
        self.__armoryYardCtrl.onProgressUpdated -= self.__updateModel
        self.__armoryYardCtrl.onQuestsUpdated -= self.__updateModel

    def _getEvents(self):
        return ((self.__armoryYardCtrl.onUpdated, self.__updateModel), (self.viewModel.onAction, self.__showMainView))

    def __updateModel(self, *_):
        if not self.__armoryYardCtrl.isEnabled():
            return
        with self.viewModel.transaction() as model:
            startProgressionTime, finishProgressionTime = self.__armoryYardCtrl.getProgressionTimes()
            _, endSeasonDate = self.__armoryYardCtrl.getSeasonInterval()
            state = self.__armoryYardCtrl.getState()
            model.setStartTime(startProgressionTime)
            model.setEndTime(endSeasonDate if state == State.POSTPROGRESSION else finishProgressionTime)
            model.setCurrentTime(getServerUTCTime())
            if self.__armoryYardCtrl.isActive() and self.__armoryYardCtrl.isClaimedFinalReward():
                state = State.COMPLETED
            model.setState(state)

    def __showMainView(self):
        self.__armoryYardCtrl.goToArmoryYard()
