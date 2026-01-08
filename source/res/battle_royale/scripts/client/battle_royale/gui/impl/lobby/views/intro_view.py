# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/views/intro_view.py
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.common.battle_royale.br_helpers import currentHangarIsBattleRoyale
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.common.intro_slide_model import IntroSlideModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.prb_control.entities.listener import IGlobalListener
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController, IHangarSpaceSwitchController
from battle_royale.gui.impl.gen.view_models.views.lobby.views.intro_view_model import IntroViewModel

class IntroView(ViewImpl, IGlobalListener):
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)
    __spaceSwitchController = dependency.descriptor(IHangarSpaceSwitchController)

    def __init__(self):
        settings = ViewSettings(R.views.battle_royale.lobby.views.IntroView())
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = IntroViewModel()
        self.__isPageWasShow = False
        super(IntroView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(IntroView, self).getViewModel()

    def onPrbEntitySwitched(self):
        if not self.__battleRoyaleController.isBattleRoyaleMode():
            self.destroyWindow()

    def _onLoading(self, *args, **kwargs):
        super(IntroView, self)._onLoading(*args, **kwargs)
        self.viewModel.onClose += self.__onClose
        self.viewModel.onVideo += self.__onVideo
        if currentHangarIsBattleRoyale():
            self.__onSpaceUpdated()
        else:
            self.__spaceSwitchController.onSpaceUpdated += self.__onSpaceUpdated
        lsm = getLobbyStateMachine()
        if lsm is not None:
            lsm.onVisibleRouteChanged += self.__onVisibleRouteChanged
        self.startGlobalListening()
        self.__updateViewModel()
        return

    def _finalize(self):
        self.viewModel.onClose -= self.__onClose
        self.viewModel.onVideo -= self.__onVideo
        self.__spaceSwitchController.onSpaceUpdated -= self.__onSpaceUpdated
        self.stopGlobalListening()
        lsm = getLobbyStateMachine()
        if lsm is not None:
            lsm.onVisibleRouteChanged -= self.__onVisibleRouteChanged
        super(IntroView, self)._finalize()
        return

    def __onVisibleRouteChanged(self, routeInfo):
        from gui.lobby_state_machine.states import isHangarState
        if isHangarState(routeInfo.state):
            self.__onClose()

    def __onClose(self):
        self.destroyWindow()

    def __onVideo(self):
        self.__battleRoyaleController.showIntroVideo(VIEW_ALIAS.BROWSER_OVERLAY, force=True)

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
