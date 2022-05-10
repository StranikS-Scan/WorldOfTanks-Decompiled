# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/views/intro_view.py
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_intro_view_model import BattlePassIntroViewModel
from gui.impl.gen.view_models.views.lobby.common.intro_slide_model import IntroSlideModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.shared.event_dispatcher import showBrowserOverlayView
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IBattleRoyaleController
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import ViewEventType

class IntroView(ViewImpl):
    __settingsCore = dependency.descriptor(ISettingsCore)
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)

    def __init__(self):
        settings = ViewSettings(R.views.battle_royale.lobby.views.IntroView())
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = BattlePassIntroViewModel()
        self.__urlIntroVideo = self.__battleRoyaleController.getIntroVideoURL()
        self.__isPageWasShow = False
        super(IntroView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(IntroView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(IntroView, self)._onLoading(*args, **kwargs)
        self.viewModel.onClose += self.__onClose
        self.viewModel.onVideo += self.__onVideo
        self.__battleRoyaleController.onSpaceUpdated += self.__onSpaceUpdated
        g_eventBus.addListener(ViewEventType.LOAD_VIEW, self.__handleLoadView, scope=EVENT_BUS_SCOPE.LOBBY)
        self.__updateViewModel()

    def _finalize(self):
        self.viewModel.onClose -= self.__onClose
        self.viewModel.onVideo -= self.__onVideo
        self.__battleRoyaleController.onSpaceUpdated -= self.__onSpaceUpdated
        g_eventBus.removeListener(ViewEventType.LOAD_VIEW, self.__handleLoadView, scope=EVENT_BUS_SCOPE.LOBBY)
        super(IntroView, self)._finalize()

    def __handleLoadView(self, event):
        if event.alias == VIEW_ALIAS.LOBBY_HANGAR:
            self.__onClose()

    def __onClose(self):
        self.destroyWindow()

    def __onVideo(self):
        showBrowserOverlayView(self.__urlIntroVideo, VIEW_ALIAS.BROWSER_OVERLAY)

    def __onSpaceUpdated(self):
        if not self.__isPageWasShow:
            self.__isPageWasShow = True
            self.__onVideo()
        else:
            self.__onClose()

    def __updateViewModel(self):
        texts = R.strings.battle_royale.intro
        images = R.images.battle_royale.gui.maps.intro
        with self.viewModel.transaction() as tx:
            tx.setTitle(texts.title())
            tx.setAbout(texts.aboutButton())
            tx.setButtonLabel(texts.button())
            slides = tx.getSlides()
            slides.addViewModel(self.__createSlideModel(images.tanks(), texts.slide1.title(), backport.text(texts.slide1.text())))
            slides.addViewModel(self.__createSlideModel(images.rent(), texts.slide2.title(), backport.text(texts.slide2.text())))
            slides.addViewModel(self.__createSlideModel(images.mining(), texts.slide3.title(), backport.text(texts.slide3.text())))
            slides.addViewModel(self.__createSlideModel(images.map(), texts.slide4.title(), backport.text(texts.slide4.text())))

    @staticmethod
    def __createSlideModel(icon, title, description):
        slide = IntroSlideModel()
        slide.setIcon(icon)
        slide.setTitle(title)
        slide.setDescription(description)
        return slide


class IntroWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, ctx, parent):
        super(IntroWindow, self).__init__(content=IntroView(), wndFlags=WindowFlags.WINDOW, decorator=None, parent=parent)
        return
