# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/main_widget.py
from comp7_light_progression.gui.shared.event_dispatcher import showProgressionView
from frameworks.wulf import ViewFlags, ViewSettings
from comp7_light_progression.skeletons.game_controller import IComp7LightProgressionOnTokensController
from gui.impl.lobby.comp7.tooltips.widget_tooltip_view import WidgetTooltipView
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.comp7.main_widget_model import MainWidgetModel, BattleStatus
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller

class Comp7MainWidgetComponent(InjectComponentAdaptor):
    __slots__ = ('__view',)

    def __init__(self):
        super(Comp7MainWidgetComponent, self).__init__()
        self.__view = None
        return

    def _dispose(self):
        self.__view = None
        super(Comp7MainWidgetComponent, self)._dispose()
        return

    def _makeInjectView(self):
        self.__view = Comp7MainWidget(flags=ViewFlags.VIEW)
        return self.__view


class Comp7MainWidget(ViewImpl):
    comp7LightProgression = dependency.descriptor(IComp7LightProgressionOnTokensController)
    __slots__ = ()
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.lobby.comp7.MainWidget())
        settings.flags = flags
        settings.model = MainWidgetModel()
        super(Comp7MainWidget, self).__init__(settings)

    @property
    def viewModel(self):
        return super(Comp7MainWidget, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return WidgetTooltipView() if contentID == R.views.lobby.comp7.tooltips.WidgetTooltipView() else super(Comp7MainWidget, self).createToolTipContent(event, contentID)

    def updateModel(self):
        isInProgress = self.comp7LightProgression.isEnabled and not self.comp7LightProgression.isFinished
        currentStage = 0
        if isInProgress:
            currentStage = self.comp7LightProgression.getCurrentStageData().get('currentStage')
        with self.viewModel.transaction() as model:
            model.setCurrentProgression(currentStage)
            model.setBattleStatus(BattleStatus.INPROGRESS if isInProgress else BattleStatus.COMPLETED)

    def _onLoading(self, *args, **kwargs):
        super(Comp7MainWidget, self)._onLoading(args, kwargs)
        self.updateModel()
        self.__addListeners()

    def __addListeners(self):
        self.viewModel.onOpenProgression += self.__onOpenProgression
        self.comp7LightProgression.onProgressPointsUpdated += self.updateModel
        self.comp7LightProgression.onSettingsChanged += self.updateModel

    def __removeListeners(self):
        self.viewModel.onOpenProgression -= self.__onOpenProgression
        self.comp7LightProgression.onProgressPointsUpdated -= self.updateModel
        self.comp7LightProgression.onSettingsChanged -= self.updateModel

    def _finalize(self):
        self.__removeListeners()
        super(Comp7MainWidget, self)._finalize()

    @staticmethod
    def __onOpenProgression():
        showProgressionView()
