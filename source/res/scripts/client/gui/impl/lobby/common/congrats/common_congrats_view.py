# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/common/congrats/common_congrats_view.py
import logging
from frameworks.wulf import ViewSettings, WindowFlags
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.lobby.common.congrats.common_congrats_view_model import CommonCongratsViewModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.shared.view_helpers.blur_manager import CachedBlur
_logger = logging.getLogger(__name__)

class _CommonCongratsView(ViewImpl):

    def __init__(self, context):
        settings = ViewSettings(R.views.lobby.common.congrats.common_congrats_view.CommonCongratsView())
        settings.model = CommonCongratsViewModel()
        super(_CommonCongratsView, self).__init__(settings)
        self.__ctx = context

    @property
    def viewModel(self):
        return super(_CommonCongratsView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(_CommonCongratsView, self)._initialize()
        self.__updateVM()
        self.__addListeners()
        self._blur = CachedBlur(enabled=True)

    def _finalize(self):
        self._blur.fini()
        self.__removeListeners()
        super(_CommonCongratsView, self)._finalize()

    def __updateVM(self):
        with self.viewModel.transaction() as vm:
            vm.setBackground(self.__ctx.background)
            vm.setTitle(self.__ctx.title)
            vm.setDescription(self.__ctx.description)
            vm.setImage(self.__ctx.image)
            vm.setImageAlt(self.__ctx.imageAlt)
            vm.setConfirmLbl(self.__ctx.confirmLabel)
            vm.setBackLbl(self.__ctx.backLabel)

    def __addListeners(self):
        self.viewModel.onConfirmClick += self.__onConfirm
        self.viewModel.onBackClick += self.__onBack
        self.viewModel.onCloseClick += self.__onClose

    def __removeListeners(self):
        self.viewModel.onCloseClick -= self.__onClose
        self.viewModel.onBackClick -= self.__onBack
        self.viewModel.onConfirmClick -= self.__onConfirm

    def __onConfirm(self):
        self.__destroyWindow()
        self.__ctx.onConfirm()

    def __onBack(self):
        self.__destroyWindow()
        self.__ctx.onBack()

    def __onClose(self):
        self.__destroyWindow()
        self.__ctx.onConfirm()

    def __destroyWindow(self):
        self.viewModel.setNeedReset(True)
        self.destroyWindow()


class CongratsWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, context):
        flags = WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN
        super(CongratsWindow, self).__init__(flags, content=_CommonCongratsView(context))
