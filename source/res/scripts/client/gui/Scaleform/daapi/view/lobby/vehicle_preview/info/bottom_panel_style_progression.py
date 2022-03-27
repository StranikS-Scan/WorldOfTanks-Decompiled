# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_preview/info/bottom_panel_style_progression.py
from CurrentVehicle import g_currentPreviewVehicle
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.daapi.view.meta.VehiclePreviewBottomPanelStyleProgressionMeta import VehiclePreviewBottomPanelStyleProgressionMeta
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.customization.progression_styles.stage_switcher_model import SwitcherType
from gui.impl.gen.view_models.views.lobby.vehicle_preview.buying_panel.progression_styles_buying_panel_model import ProgressionStylesBuyingPanelModel
from gui.impl.pub import ViewImpl
from gui.shared import EVENT_BUS_SCOPE, g_eventBus
from gui.shared.events import BattlePassEvent
from helpers import dependency
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared.utils import IHangarSpace

class VehiclePreviewBottomPanelStyleProgression(VehiclePreviewBottomPanelStyleProgressionMeta):

    def __init__(self):
        super(VehiclePreviewBottomPanelStyleProgression, self).__init__()
        self.__backAlias = None
        self.__backCallback = None
        self.__styleLevel = None
        return

    def setBackAlias(self, backAlias):
        self.__backAlias = backAlias

    def setBackCallback(self, backCallback):
        self.__backCallback = backCallback

    def setStyleLevel(self, styleLevel):
        self.__styleLevel = styleLevel
        self.__view.setStyleLevel(self.__styleLevel)

    def setAvailableLevel(self, availableLevel):
        self.__view.setAvailableLevel(availableLevel)

    def setCtx(self, ctx):
        self.__view.setCtx(ctx)

    def _makeInjectView(self):
        self.__view = ProgressionStylesBuyingPanelView(flags=ViewFlags.COMPONENT)
        return self.__view


class ProgressionStylesBuyingPanelView(ViewImpl):
    __slots__ = ('__styleLevel', '__availableLevel', '__ctx')
    __customizationService = dependency.descriptor(ICustomizationService)
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.lobby.vehicle_preview.buying_panel.VPProgressionStylesBuyingPanel())
        settings.flags = flags
        settings.model = ProgressionStylesBuyingPanelModel()
        self.__styleLevel = None
        self.__availableLevel = None
        self.__ctx = None
        super(ProgressionStylesBuyingPanelView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(ProgressionStylesBuyingPanelView, self).getViewModel()

    def setStyleLevel(self, styleLevel):
        self.__styleLevel = styleLevel

    def setAvailableLevel(self, availableLevel):
        self.__availableLevel = availableLevel

    def setCtx(self, ctx):
        self.__ctx = ctx

    def _initialize(self, *args, **kwargs):
        super(ProgressionStylesBuyingPanelView, self)._initialize(*args, **kwargs)
        self.viewModel.onChange += self.__onChange

    def _onLoading(self, *args, **kwargs):
        super(ProgressionStylesBuyingPanelView, self)._onLoading(*args, **kwargs)
        g_currentPreviewVehicle.onChangeStarted += self.__onVehicleChangeStarted
        g_currentPreviewVehicle.onChanged += self.__onVehicleChanged
        with self.getViewModel().transaction() as model:
            model.setCurrentLevel(1)
            model.setSelectedLevel(1)

    def _onLoaded(self, *args, **kwargs):
        currentLevel = self.__customizationService.getCurrentProgressionStyleLevel()
        with self.getViewModel().transaction() as model:
            model.setCurrentLevel(self.__availableLevel or 1)
            model.setSelectedLevel(currentLevel if self.__styleLevel is None else self.__styleLevel)
            model.setIsReady(True)
        if self.__styleLevel is not None:
            self.__customizationService.changeStyleProgressionLevelPreview(self.__styleLevel)
        style = self.__ctx.get('style') if self.__ctx else None
        if style and style.isProgressionRewindEnabled:
            model.setCurrentLevel(style.maxProgressionLevel)
            model.setSelectedLevel(style.maxProgressionLevel)
            model.setNumberOfBullets(style.maxProgressionLevel)
            model.setSwitcherType(SwitcherType.TEXT)
            model.setStyleID(style.id)
            self.__styleLevel = style.maxProgressionLevel
        model.setIsBulletsBeforeCurrentDisabled(False)
        return

    def _finalize(self):
        self.viewModel.onChange -= self.__onChange
        event = BattlePassEvent(BattlePassEvent.ON_PREVIEW_PROGRESSION_STYLE_CLOSE, ctx={'level': self.__styleLevel})
        g_eventBus.handleEvent(event, scope=EVENT_BUS_SCOPE.LOBBY)
        g_currentPreviewVehicle.onChangeStarted -= self.__onVehicleChangeStarted
        g_currentPreviewVehicle.onChanged -= self.__onVehicleChanged
        self.__ctx = None
        super(ProgressionStylesBuyingPanelView, self)._finalize()
        return

    def __onChange(self, *args):
        if args:
            level = args[0].get('selectedLevel')
            if level is not None:
                level = int(level)
                with self.viewModel.transaction() as tx:
                    tx.setSelectedLevel(level)
                self.__customizationService.changeStyleProgressionLevelPreview(level)
                self.__styleLevel = level
        return

    def __onVehicleChangeStarted(self):
        entity = self.__hangarSpace.getVehicleEntity()
        if entity and entity.appearance:
            entity.appearance.loadState.unsubscribe(self.__onVehicleLoadFinished, self.__onVehicleLoadStarted)

    def __onVehicleChanged(self):
        entity = self.__hangarSpace.getVehicleEntity()
        if entity and entity.appearance:
            entity.appearance.loadState.subscribe(self.__onVehicleLoadFinished, self.__onVehicleLoadStarted)

    def __onVehicleLoadStarted(self):
        pass

    def __onVehicleLoadFinished(self):
        if self.__styleLevel is not None:
            self.__customizationService.changeStyleProgressionLevelPreview(self.__styleLevel)
        return
