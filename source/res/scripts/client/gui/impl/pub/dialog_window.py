# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/pub/dialog_window.py
import logging
from collections import namedtuple
from gui.Scaleform.genConsts.APP_CONTAINERS_NAMES import APP_CONTAINERS_NAMES
from helpers import dependency
from shared_utils import CONST_CONTAINER
from async import async, await, AsyncEvent, AsyncReturn, AsyncScope, BrokenPromiseError
from frameworks.wulf import ViewFlags, WindowSettings
from frameworks.wulf import WindowFlags, Window
from gui.impl.gen import R
from gui.impl.gen.view_models.ui_kit.dialog_button_model import DialogButtonModel
from gui.impl.gen.view_models.windows.dialog_window_model import DialogWindowModel
from gui.impl.pub.view_impl import ViewImpl
from gui.impl.wrappers.background_blur import WGUIBackgroundBlurSupportImpl
from skeletons.gui.impl import IGuiLoader
_logger = logging.getLogger(__name__)
DialogResult = namedtuple('DialogResult', ('result', 'data'))

class DialogButtons(CONST_CONTAINER):
    SUBMIT = DialogButtonModel.BTN_SUBMIT
    CANCEL = DialogButtonModel.BTN_CANCEL
    PURCHASE = DialogButtonModel.BTN_PURCHASE
    RESEARCH = DialogButtonModel.BTN_RESEARCH
    ALL = (SUBMIT,
     CANCEL,
     PURCHASE,
     RESEARCH)


class DialogLayer(CONST_CONTAINER):
    WINDOW = WindowFlags.WINDOW
    TOP_WINDOW = WindowFlags.DIALOG
    OVERLAY = WindowFlags.OVERLAY


class DialogContent(ViewImpl):
    __slots__ = ()

    def __init__(self, layoutID, viewModelClazz, *args, **kwargs):
        super(DialogContent, self).__init__(layoutID, ViewFlags.VIEW, viewModelClazz, *args, **kwargs)


class DialogWindow(Window):
    gui = dependency.descriptor(IGuiLoader)
    __slots__ = ('__blur', '__scope', '__event', '__result')

    def __init__(self, content=None, bottomContent=None, parent=None, balanceContent=None, enableBlur=True, enableBlur3dScene=True, layer=DialogLayer.TOP_WINDOW, decorator=None):
        if content is not None:
            pass
        settings = WindowSettings()
        settings.flags = layer
        settings.decorator = decorator or ViewImpl(R.views.common.dialog_view.dialog_window.DialogWindow(), ViewFlags.WINDOW_DECORATOR, DialogWindowModel)
        settings.content = content
        settings.parent = parent
        super(DialogWindow, self).__init__(settings)
        if bottomContent is not None:
            self._setBottomContent(bottomContent)
        self.__scope = AsyncScope()
        self.__event = AsyncEvent(scope=self.__scope)
        self.__result = DialogButtons.CANCEL
        self.__blur = None
        if enableBlur:
            self.__blur = WGUIBackgroundBlurSupportImpl(blur3dScene=enableBlur3dScene)
            blurLayers = [APP_CONTAINERS_NAMES.VIEWS, APP_CONTAINERS_NAMES.SUBVIEW, APP_CONTAINERS_NAMES.BROWSER]
            if layer > DialogLayer.WINDOW:
                blurLayers.append(APP_CONTAINERS_NAMES.WINDOWS)
            self.__blur.enable(APP_CONTAINERS_NAMES.DIALOGS, blurLayers)
        if balanceContent is not None:
            self.viewModel.setBalanceContent(balanceContent)
        return

    @async
    def wait(self):
        try:
            yield await(self.__event.wait())
        except BrokenPromiseError:
            _logger.debug('%s has been destroyed without user decision', self)

        raise AsyncReturn(DialogResult(self.__result, self._getResultData()))

    @property
    def viewModel(self):
        return self._getDecoratorViewModel()

    @property
    def contentViewModel(self):
        content = self.content
        return content.getViewModel() if content is not None else None

    @property
    def bottomContentViewModel(self):
        return self.viewModel.getBottomContent().getViewModel()

    def setParentWindowState(self, state, forceSetAllChain=False):
        if self.viewModel.getIsAnimatedState():
            parentWindow = self.viewModel.getParentWindow()
            DialogWindow(parentWindow).viewModel.setCurrentState(state)
            if forceSetAllChain:
                DialogWindow(parentWindow).setParentWindowState(state, forceSetAllChain)

    def _initialize(self):
        super(DialogWindow, self)._initialize()
        self.viewModel.onClosed += self._onClosed
        self.viewModel.buttons.onUserItemClicked += self._onButtonClick

    def _finalize(self):
        self.viewModel.onClosed -= self._onClosed
        self.viewModel.buttons.onUserItemClicked -= self._onButtonClick
        super(DialogWindow, self)._finalize()
        self.__scope.destroy()
        if self.__blur is not None:
            self.__blur.disable()
        return

    def _onClosed(self, _=None):
        self.destroy()

    def _removeAllButtons(self):
        self.viewModel.buttons.getItems().clear()

    def _addButton(self, name, label, isFocused=False, invalidateAll=False, isEnabled=True, soundDown=None):
        button = DialogButtonModel()
        button.setName(name)
        button.setLabel(label)
        button.setDoSetFocus(isFocused)
        button.setIsEnabled(isEnabled)
        if soundDown is not None:
            button.setSoundDown(soundDown)
        self.viewModel.buttons.addViewModel(button, isSelected=isFocused)
        if invalidateAll:
            self.viewModel.buttons.invalidate()
        return

    def _getButton(self, name):
        for item in self.viewModel.buttons.getItems():
            if name == item.getName():
                return item

        return None

    def _onButtonClick(self, item):
        if item.getIsEnabled():
            self.__result = item.getName()
            self.__event.set()

    def _setBackgroundImage(self, value):
        self.viewModel.setBackgroundImage(value)

    def _setBottomContent(self, value):
        self.viewModel.setBottomContent(value)

    def _setIconHighlight(self, value):
        self.viewModel.setIconHighlight(value)

    def _setAnimationHighlight(self, value):
        self.viewModel.setAnimationHighlight(value)

    def _setPreset(self, value):
        self.viewModel.setPreset(value)

    def _serShowSoundId(self, value):
        self.viewModel.setShowSoundId(value)

    def _setButtonEnabled(self, buttonName, value):
        button = self._getButton(buttonName)
        if button is not None:
            button.setIsEnabled(value)
        return

    def _getResultData(self):
        return None
