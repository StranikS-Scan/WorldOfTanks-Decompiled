# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_preview/info/progression_styles_buying_panel.py
from gui.impl.gen import R
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.customization import ICustomizationService
from gui.Scaleform.daapi.view.meta.VehiclePreviewProgressionStylesBuyingPanelMeta import VehiclePreviewProgressionStylesBuyingPanelMeta
from gui.impl.gen.view_models.views.lobby.vehicle_preview.buying_panel.progression_styles_buying_panel_model import ProgressionStylesBuyingPanelModel
from gui.impl.lobby.tooltips.progression_styles_info_tooltip import ProgressionStylesInfoTooltip

class VehiclePreviewProgressionStylesBuyingPanel(VehiclePreviewProgressionStylesBuyingPanelMeta):

    def __init__(self):
        super(VehiclePreviewProgressionStylesBuyingPanel, self).__init__()
        self.__backAlias = None
        self.__backCallback = None
        return

    def setBackAlias(self, backAlias):
        self.__backAlias = backAlias

    def setBackCallback(self, backCallback):
        self.__backCallback = backCallback

    def _makeInjectView(self):
        self.__view = ProgressionStylesBuyingPanelView(flags=ViewFlags.COMPONENT)
        return self.__view


class ProgressionStylesBuyingPanelView(ViewImpl):
    customizationService = dependency.descriptor(ICustomizationService)

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.lobby.vehicle_preview.buying_panel.VPProgressionStylesBuyingPanel())
        settings.flags = flags
        settings.model = ProgressionStylesBuyingPanelModel()
        super(ProgressionStylesBuyingPanelView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ProgressionStylesBuyingPanelView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return ProgressionStylesInfoTooltip()

    def _initialize(self, *args, **kwargs):
        super(ProgressionStylesBuyingPanelView, self)._initialize(*args, **kwargs)
        self.viewModel.onChange += self.__onChange

    def _onLoading(self, *args, **kwargs):
        super(ProgressionStylesBuyingPanelView, self)._onLoading(*args, **kwargs)
        with self.getViewModel().transaction() as model:
            model.setCurrentLevel(1)
            model.setSelectedLevel(1)

    def _onLoaded(self, *args, **kwargs):
        currentLevel = self.customizationService.getCurrentProgressionStyleLevel()
        with self.getViewModel().transaction() as model:
            model.setCurrentLevel(currentLevel if currentLevel else 1)
            model.setSelectedLevel(currentLevel if currentLevel else 1)

    def _finalize(self):
        super(ProgressionStylesBuyingPanelView, self)._finalize()
        self.viewModel.onChange -= self.__onChange

    def __onChange(self, *args):
        if args:
            if args[0]['selectedLevel'] is not None:
                with self.viewModel.transaction() as tx:
                    tx.setSelectedLevel(args[0]['selectedLevel'])
                self.customizationService.changeStyleProgressionLevelPreview(int(args[0]['selectedLevel']))
        return
