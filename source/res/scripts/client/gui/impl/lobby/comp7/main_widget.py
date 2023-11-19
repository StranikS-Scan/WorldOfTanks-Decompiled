# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/main_widget.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.comp7.main_widget_model import MainWidgetModel
from gui.impl.lobby.comp7 import comp7_model_helpers, comp7_shared, comp7_qualification_helpers
from gui.impl.lobby.comp7.comp7_model_helpers import getSeasonNameEnum
from gui.impl.lobby.comp7.tooltips.main_widget_tooltip import MainWidgetTooltip
from gui.impl.lobby.comp7.tooltips.rank_inactivity_tooltip import RankInactivityTooltip
from gui.impl.pub import ViewImpl
from gui.shared import event_dispatcher
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
        if contentID == R.views.lobby.comp7.tooltips.MainWidgetTooltip():
            return MainWidgetTooltip()
        return RankInactivityTooltip() if contentID == R.views.lobby.comp7.tooltips.RankInactivityTooltip() else super(Comp7MainWidget, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(Comp7MainWidget, self)._onLoading(*args, **kwargs)
        self.__updateData()
        self.__addListeners()

    def _finalize(self):
        self.__removeListeners()
        super(Comp7MainWidget, self)._finalize()

    def __updateRating(self, *_, **__):
        rating = self.__comp7Controller.rating
        activitiPoints = self.__comp7Controller.activityPoints
        viewData = self.__comp7Controller.getViewData(HANGAR_ALIASES.COMP7_WIDGET)
        prevRating = viewData.get('prevRating', rating)
        prevActivityPoints = self.viewModel.getRankInactivityCount()
        if rating != prevRating or activitiPoints != prevActivityPoints:
            self.__updateData()

    def __updateData(self, *_, **__):
        if self.__comp7Controller.isFrozen() or not self.__comp7Controller.isEnabled():
            return
        with self.viewModel.transaction() as vm:
            vm.setIsEnabled(not self.__comp7Controller.isOffline)
            vm.setSeasonName(getSeasonNameEnum())
            self.__updateQualificationData(vm)
            self.__updateProgressionData(vm)

    def __updateQualificationData(self, model):
        comp7_qualification_helpers.setQualificationInfo(model.qualificationModel)

    def __updateProgressionData(self, model):
        division = comp7_shared.getPlayerDivision()
        rating = self.__comp7Controller.rating
        viewData = self.__comp7Controller.getViewData(HANGAR_ALIASES.COMP7_WIDGET)
        prevRating = viewData.get('prevRating', rating)
        viewData['prevRating'] = rating
        model.setRank(comp7_shared.getRankEnumValue(division))
        model.setCurrentScore(rating)
        model.setPrevScore(prevRating)
        comp7_model_helpers.setDivisionInfo(model=model.divisionInfo, division=division)
        comp7_model_helpers.setElitePercentage(model)
        if self.__comp7Controller.isAvailable():
            comp7_model_helpers.setRanksInactivityInfo(model)

    def __addListeners(self):
        self.__comp7Controller.onStatusUpdated += self.__updateData
        self.__comp7Controller.onRankUpdated += self.__updateRating
        self.__comp7Controller.onComp7ConfigChanged += self.__updateData
        self.__comp7Controller.onComp7RanksConfigChanged += self.__updateData
        self.__comp7Controller.onOfflineStatusUpdated += self.__updateData
        self.__comp7Controller.onQualificationBattlesUpdated += self.__updateData
        self.__comp7Controller.onQualificationStateUpdated += self.__updateData
        self.viewModel.onOpenMeta += self.__onOpenMetaClick

    def __removeListeners(self):
        self.__comp7Controller.onStatusUpdated -= self.__updateData
        self.__comp7Controller.onRankUpdated -= self.__updateRating
        self.__comp7Controller.onComp7ConfigChanged -= self.__updateData
        self.__comp7Controller.onComp7RanksConfigChanged -= self.__updateData
        self.__comp7Controller.onOfflineStatusUpdated -= self.__updateData
        self.__comp7Controller.onQualificationBattlesUpdated -= self.__updateData
        self.__comp7Controller.onQualificationStateUpdated -= self.__updateData
        self.viewModel.onOpenMeta -= self.__onOpenMetaClick

    @staticmethod
    def __onOpenMetaClick():
        event_dispatcher.showComp7MetaRootView()
