# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/veh_skill_tree/dialogs/intro_page_view.py
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gui import GUI_SETTINGS
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.common.base_intro_view_model import BaseIntroViewModel
from gui.impl.gen.view_models.views.lobby.common.intro_slide_model import IntroSlideModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.shared.view_helpers.blur_manager import CachedBlur
from helpers import dependency
from skeletons.gui.shared import IItemsCache
_IMAGES = R.images.gui.maps.icons.skillTree.introPage
_TEXTS = R.strings.veh_skill_tree.intro

class IntroPageView(ViewImpl):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, layoutID, *args, **kwargs):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = BaseIntroViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(IntroPageView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(IntroPageView, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.destroyWindow),)

    def _onLoading(self):
        super(IntroPageView, self)._onLoading()
        with self.viewModel.transaction() as tx:
            slides = tx.getSlides()
            for slideName in GUI_SETTINGS.vehSkillTreeIntroSlides:
                slides.addViewModel(self.__createSlideModel(slideName))

            tx.setButtonLabel(_TEXTS.button())

    @staticmethod
    def __createSlideModel(slideName):
        slide = IntroSlideModel()
        slide.setIcon(_IMAGES.dyn(slideName)())
        slide.setTitle(_TEXTS.dyn(slideName).title())
        slide.setDescription(backport.text(_TEXTS.dyn(slideName).description()))
        return slide


class IntroPageWindow(LobbyNotificationWindow):

    def __init__(self, parent=None):
        super(IntroPageWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=IntroPageView(R.views.mono.lobby.veh_skill_tree.intro_page()), parent=parent, layer=WindowLayer.TOP_WINDOW)
        self.__blur = CachedBlur(enabled=True, ownLayer=WindowLayer.WINDOW, uiBlurRadius=50)

    def _finalize(self):
        self.__blur.fini()
        super(IntroPageWindow, self)._finalize()
