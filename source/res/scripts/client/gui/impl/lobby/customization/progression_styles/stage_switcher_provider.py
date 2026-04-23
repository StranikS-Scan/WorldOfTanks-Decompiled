# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/customization/progression_styles/stage_switcher_provider.py
import logging
import weakref
from CurrentVehicle import g_currentVehicle
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.customization.customization_bill_data_packer import packBottomPanelBillData
from helpers.events_handler import EventsHandler
from gui.customization.constants import CustomizationModes
from gui.impl.gen.view_models.views.lobby.customization.progression_styles.stage_switcher_widget_model import StageSwitcherWidgetModel, SwitcherType
from helpers import dependency
from skeletons.gui.customization import ICustomizationService
_logger = logging.getLogger(__name__)

class StageSwitcherProvider(EventsHandler):
    __slots__ = ('__customizationService', '__ctx', '__mainView', 'isVisible')
    __customizationService = dependency.descriptor(ICustomizationService)

    def __init__(self, mainView):
        self.__mainView = weakref.proxy(mainView)
        self.__ctx = self.__customizationService.getCtx()
        self.isVisible = False
        self._subscribe()

    def fini(self):
        self._unsubscribe()

    @property
    def viewModel(self):
        return self.__mainView.viewModel.stageSwitcherWidgetModel

    def setVisibility(self, isVisible):
        if isVisible == self.isVisible:
            return
        self.isVisible = isVisible
        if isVisible:
            self._fillModel()
        else:
            with self.viewModel.transaction() as tx:
                tx.setIsVisible(isVisible)

    def _fillModel(self):
        progressionLevel = self.__ctx.mode.getStyleProgressionLevel()
        with self.viewModel.transaction() as model:
            model.setCurrentLevel(progressionLevel)
            model.setSelectedLevel(progressionLevel)
            model.setIsVisible(self.isVisible)
            style = self.__ctx.mode.modifiedStyle
            if style.isProgressionRewindEnabled:
                model.setNumberOfBullets(style.maxProgressionLevel)
                model.setIsBulletsBeforeCurrentDisabled(False)
                model.setSwitcherType(SwitcherType.TEXT)
                model.setStyleID(style.id)

    def _getEvents(self):
        return ((self.viewModel.onChange, self.__onChange),
         (self.__ctx.events.onItemsRemoved, self.__onItemsRemoved),
         (self.__ctx.events.onItemInstalled, self.__onItemInstalled),
         (self.__ctx.events.onChangesCanceled, self.__onChangesCanceled))

    def __onItemsRemoved(self, *_, **__):
        if self.__ctx is not None and self.__ctx.modeId == CustomizationModes.STYLED_3D:
            with self.viewModel.transaction() as tx:
                tx.setSelectedLevel(self.__ctx.mode.getStyleProgressionLevel())
        return

    def __onItemInstalled(self, *_):
        if self.__ctx is not None and self.__ctx.modeId == CustomizationModes.STYLED_3D:
            self.__updateModel()
        return

    def __onChangesCanceled(self):
        if self.__ctx is not None and self.__ctx.modeId == CustomizationModes.STYLED_3D:
            self.__updateModel()
        return

    def __updateModel(self):
        with self.viewModel.transaction() as tx:
            style = self.__ctx.mode.modifiedStyle
            tx.setSelectedLevel(self.__ctx.mode.getStyleProgressionLevel())
            if style is not None:
                tx.setCurrentLevel(style.getLatestOpenedProgressionLevel(g_currentVehicle.item))
        return

    @args2params(int)
    def __onChange(self, selectedLevel):
        with self.viewModel.transaction() as tx:
            tx.setSelectedLevel(selectedLevel)
        if self.__ctx is not None and self.__ctx.modeId == CustomizationModes.STYLED_3D:
            self.__ctx.mode.changeStyleProgressionLevel(selectedLevel)
            packBottomPanelBillData(self.__mainView.viewModel.billModel)
        else:
            self.__customizationService.changeStyleProgressionLevelPreview(selectedLevel)
        return
