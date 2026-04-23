# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/customization/progression_styles/onboarding_view.py
from functools import partial
from CurrentVehicle import g_currentVehicle
from frameworks.wulf import ViewSettings, WindowFlags
from gui.customization.shared import chooseMode
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.customization.progression_styles.onboarding_view_model import OnboardingViewModel
from gui.impl.lobby.customization.shared import CustomizationTabs
from gui.impl.lobby.customization.sound_constants import SOUNDS
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.shared.view_helpers.blur_manager import CachedBlur
from helpers import dependency
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache

@dependency.replace_none_kwargs(service=ICustomizationService, itemsCache=IItemsCache)
def _onCustomizationLoadedCallback(styleCD, service=None, itemsCache=None):
    if not styleCD:
        return
    ctx = service.getCtx()
    ctx.changeTab(CustomizationTabs.STYLED_3D if itemsCache.items.getItemByCD(styleCD).is3D else CustomizationTabs.STYLED_2D, styleCD)
    service.stopHighlighter()
    if ctx.mode.isRegion:
        service.startHighlighter(chooseMode(ctx.mode.slotType, ctx.modeId, g_currentVehicle.item))
    ctx.selectItem(styleCD)


class OnboardingView(ViewImpl):
    __slots__ = ('__isFirstRun', '__styleCD', '__ctx')
    __customizationService = dependency.descriptor(ICustomizationService)

    def __init__(self, ctx, layoutID):
        settings = ViewSettings(layoutID)
        settings.model = OnboardingViewModel()
        self.__isFirstRun = ctx.get('isFirstRun')
        self.__styleCD = ctx.get('styleCD')
        super(OnboardingView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(OnboardingView, self).getViewModel()

    def _onLoading(self):
        super(OnboardingView, self)._onLoading()
        self.viewModel.setIsFirstShow(self.__isFirstRun)
        self.soundManager.setState(SOUNDS.STATE_STYLEINFO, SOUNDS.STATE_STYLEINFO_SHOW)
        self.soundManager.setRTPC(SOUNDS.RTPC_STYLEINFO, 1)
        self.__ctx = self.__customizationService.getCtx()

    def _getEvents(self):
        return ((self.viewModel.onGotoStyle, self.__onGotoStyle), (self.viewModel.onClose, self.__onClose))

    def _initialize(self):
        self.__ctx.events.onOnboardingView(True)
        super(OnboardingView, self)._initialize()

    def _finalize(self):
        self.__ctx.events.onOnboardingView(False)
        super(OnboardingView, self)._finalize()

    def __onGotoStyle(self):
        customizationCallback = partial(_onCustomizationLoadedCallback, styleCD=self.__styleCD)
        if self.__customizationService.getCtx() is None:
            self.__customizationService.showCustomization(callback=customizationCallback)
        else:
            customizationCallback()
        self.destroyWindow()
        return

    def __onClose(self):
        self.soundManager.setState(SOUNDS.STATE_STYLEINFO, SOUNDS.STATE_STYLEINFO_HIDE)
        self.soundManager.setRTPC(SOUNDS.RTPC_STYLEINFO, 0)
        self.destroyWindow()


class OnboardingWindow(LobbyWindow):
    __slots__ = ('__blur',)

    def __init__(self, ctx):
        super(OnboardingWindow, self).__init__(content=OnboardingView(ctx, R.views.lobby.customization.progression_styles.OnboardingView()), wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN)
        self.__blur = CachedBlur(enabled=True, ownLayer=self.layer)

    def _finalize(self):
        self.__blur.fini()
        super(OnboardingWindow, self)._finalize()
