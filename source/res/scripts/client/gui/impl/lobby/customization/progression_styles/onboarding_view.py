# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/customization/progression_styles/onboarding_view.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import IS_CUSTOMIZATION_INTRO_VIEWED
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from functools import partial
from gui.customization.constants import CustomizationModes
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.customization.progression_styles.onboarding_view_model import OnboardingViewModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.Scaleform.daapi.view.lobby.customization.shared import CustomizationTabs
from gui.shared.view_helpers.blur_manager import CachedBlur
from helpers import dependency
from skeletons.gui.customization import ICustomizationService

@dependency.replace_none_kwargs(service=ICustomizationService)
def _onCustomizationLoadedCallback(styleCD, service=None):
    if not styleCD:
        return
    ctx = service.getCtx()
    ctx.changeMode(CustomizationModes.STYLED, CustomizationTabs.STYLES)
    ctx.selectItem(styleCD)


class OnboardingView(ViewImpl):
    __slots__ = ('__isFirstRun', '__styleCD')
    __customizationService = dependency.descriptor(ICustomizationService)

    def __init__(self, ctx, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = OnboardingViewModel()
        self.__isFirstRun = ctx.get('isFirstRun')
        self.__styleCD = ctx.get('styleCD')
        super(OnboardingView, self).__init__(settings)

    def _initialize(self, *args, **kwargs):
        super(OnboardingView, self)._initialize(*args, **kwargs)
        self.__addListeners()

    def _finalize(self):
        super(OnboardingView, self)._finalize()
        self.__removeListeners()

    def _onLoading(self):
        super(OnboardingView, self)._onLoading()
        self.viewModel.setIsFirstShow(self.__isFirstRun)
        isFirstOpen = not AccountSettings.getSettings(IS_CUSTOMIZATION_INTRO_VIEWED)
        if isFirstOpen:
            AccountSettings.setSettings(IS_CUSTOMIZATION_INTRO_VIEWED, True)

    def __addListeners(self):
        model = self.viewModel
        model.onClose += self.__onClose
        model.onGotoStyle += self.__onGotoStyle

    def __removeListeners(self):
        model = self.viewModel
        model.onClose -= self.__onClose
        model.onGotoStyle -= self.__onGotoStyle

    def __onClose(self):
        self.destroyWindow()

    def __onGotoStyle(self):
        customizationCallback = partial(_onCustomizationLoadedCallback, styleCD=self.__styleCD)
        if self.__customizationService.getCtx() is None:
            self.__customizationService.showCustomization(callback=customizationCallback)
        else:
            customizationCallback()
        self.destroyWindow()
        return

    @property
    def viewModel(self):
        return super(OnboardingView, self).getViewModel()


class OnboardingWindow(LobbyWindow):
    __slots__ = ('__blur',)

    def __init__(self, ctx, parent):
        super(OnboardingWindow, self).__init__(content=OnboardingView(ctx, R.views.lobby.customization.progression_styles.OnboardingView()), wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, decorator=None, parent=parent)
        self.__blur = CachedBlur(enabled=True, ownLayer=self.layer)
        return

    def _finalize(self):
        self.__blur.fini()
        super(OnboardingWindow, self)._finalize()
