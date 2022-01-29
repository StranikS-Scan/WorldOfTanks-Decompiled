# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/progression_styles/stage_switcher.py
import logging
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.daapi.view.meta.StageSwitcherMeta import StageSwitcherMeta
from gui.customization.constants import CustomizationModes
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.customization.progression_styles.stage_switcher_model import StageSwitcherModel, SwitcherType
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class StageSwitcher(StageSwitcherMeta):

    def _makeInjectView(self):
        self.__view = StageSwitcherView(flags=ViewFlags.COMPONENT)
        return self.__view


class StageSwitcherView(ViewImpl):
    __customizationService = dependency.descriptor(ICustomizationService)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.lobby.customization.progression_styles.StageSwitcher())
        settings.flags = flags
        settings.model = StageSwitcherModel()
        self.__ctx = self.__customizationService.getCtx()
        super(StageSwitcherView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(StageSwitcherView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(StageSwitcherView, self)._initialize(*args, **kwargs)
        self.viewModel.onChange += self.__onChange
        self.__ctx.events.onItemsRemoved += self.__onItemsRemoved

    def _onLoading(self, *args, **kwargs):
        super(StageSwitcherView, self)._onLoading(*args, **kwargs)
        progressionLevel = self.__ctx.mode.getStyleProgressionLevel()
        with self.getViewModel().transaction() as model:
            model.setCurrentLevel(progressionLevel)
            model.setSelectedLevel(progressionLevel)
            style = self.__ctx.mode.modifiedStyle
            if style.isProgressionRewindEnabled:
                model.setNumberOfBullets(style.maxProgressionLevel)
                model.setIsBulletsBeforeCurrentDisabled(False)
                model.setSwitcherType(SwitcherType.TEXT)
                model.setStyleID(style.id)

    def _finalize(self):
        super(StageSwitcherView, self)._finalize()
        self.viewModel.onChange -= self.__onChange
        self.__ctx.events.onItemsRemoved -= self.__onItemsRemoved
        self.__ctx = None
        return

    def __onItemsRemoved(self, *_, **__):
        if self.__ctx is not None and self.__ctx.modeId == CustomizationModes.STYLED:
            with self.viewModel.transaction() as tx:
                tx.setSelectedLevel(self.__ctx.mode.getStyleProgressionLevel())
        return

    def __onChange(self, *args):
        if args and args[0]['selectedLevel'] is not None:
            selectedLevel = int(args[0]['selectedLevel'])
            with self.viewModel.transaction() as tx:
                tx.setSelectedLevel(args[0]['selectedLevel'])
            if self.__ctx is not None and self.__ctx.modeId == CustomizationModes.STYLED:
                self.__ctx.mode.changeStyleProgressionLevel(selectedLevel)
            else:
                self.__customizationService.changeStyleProgressionLevelPreview(selectedLevel)
        return
