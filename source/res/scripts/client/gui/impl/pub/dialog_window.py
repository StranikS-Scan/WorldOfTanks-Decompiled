# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/pub/dialog_window.py
import logging
from collections import namedtuple
from async import async, await, AsyncEvent, AsyncReturn, AsyncScope, BrokenPromiseError
from frameworks.wulf import ViewFlags, WindowSettings, ViewSettings
from frameworks.wulf import WindowFlags, Window
from gui.shared.view_helpers.blur_manager import CachedBlur
from gui.impl.gen import R
from gui.impl.gen.view_models.ui_kit.dialog_button_model import DialogButtonModel
from gui.impl.gen.view_models.windows.dialog_window_model import DialogWindowModel
from gui.impl.pub.view_impl import ViewImpl
from helpers import dependency
from shared_utils import CONST_CONTAINER
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
    ACCEPT_BUTTONS = (SUBMIT, PURCHASE, RESEARCH)


class DialogFlags(CONST_CONTAINER):
    WINDOW = WindowFlags.WINDOW
    TOP_WINDOW = WindowFlags.DIALOG
    TOP_FULLSCREEN_WINDOW = WindowFlags.DIALOG | WindowFlags.WINDOW_FULLSCREEN


class DialogContent(ViewImpl):
    __slots__ = ()


class DialogDecorator(ViewImpl):
    __slots__ = ()

    def __init__(self, balanceContent=None, bottomContent=None):
        settings = ViewSettings(R.views.common.dialog_view.dialog_window.DialogWindow())
        settings.flags = ViewFlags.WINDOW_DECORATOR
        settings.model = DialogWindowModel()
        settings.args = (balanceContent, bottomContent)
        super(DialogDecorator, self).__init__(settings)

    @property
    def balanceContent(self):
        return self.getChildView(R.dynamic_ids.dialog_window.balance_content())

    @property
    def bottomContent(self):
        return self.getChildView(R.dynamic_ids.dialog_window.bottom_content())

    def _onLoading(self, balanceContent, bottomContent):
        hasBalance = False
        hasBottomContent = False
        if balanceContent is not None:
            hasBalance = True
            self.setChildView(R.dynamic_ids.dialog_window.balance_content(), balanceContent)
        if bottomContent is not None:
            hasBottomContent = True
            self.setChildView(R.dynamic_ids.dialog_window.bottom_content(), bottomContent)
        with self.getViewModel().transaction() as tx:
            tx.setHasBalance(hasBalance)
            tx.setHasBottomContent(hasBottomContent)
        return


class DialogWindow(Window):
    gui = dependency.descriptor(IGuiLoader)
    __slots__ = ('__blur', '__scope', '__event', '__result')

    def __init__(self, content=None, bottomContent=None, parent=None, balanceContent=None, enableBlur=True, flags=DialogFlags.TOP_WINDOW):
        if content is not None:
            pass
        settings = WindowSettings()
        settings.flags = flags
        settings.decorator = DialogDecorator(balanceContent, bottomContent)
        settings.content = content
        settings.parent = parent
        super(DialogWindow, self).__init__(settings)
        self.__scope = AsyncScope()
        self.__event = AsyncEvent(scope=self.__scope)
        self.__result = DialogButtons.CANCEL
        self.__blur = CachedBlur(enabled=enableBlur, ownLayer=self.layer, blurAnimRepeatCount=4)
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
        if self.decorator is not None:
            view = self.decorator.bottomContent
            if view is not None:
                return view.getViewModel()
        return

    def _initialize(self):
        super(DialogWindow, self)._initialize()
        self.viewModel.onClosed += self._onClosed
        self.viewModel.buttons.onUserItemClicked += self._onButtonClick

    def _finalize(self):
        self.viewModel.onClosed -= self._onClosed
        self.viewModel.buttons.onUserItemClicked -= self._onButtonClick
        super(DialogWindow, self)._finalize()
        self.__scope.destroy()
        self.__blur.fini()

    def _onClosed(self, _=None):
        self.destroy()

    def _removeAllButtons(self):
        self.viewModel.buttons.getItems().clear()

    def _addButton(self, name, label=R.invalid(), isFocused=False, invalidateAll=False, isEnabled=True, soundDown=None, rawLabel='', tooltipHeader=R.invalid(), tooltipBody=R.invalid()):
        button = DialogButtonModel()
        button.setName(name)
        if rawLabel:
            button.setRawLabel(rawLabel)
        else:
            button.setLabel(label)
        button.setDoSetFocus(isFocused)
        button.setIsEnabled(isEnabled)
        if soundDown is not None:
            button.setSoundDown(soundDown)
        button.setTooltipHeader(tooltipHeader)
        button.setTooltipBody(tooltipBody)
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

    def _setIconHighlight(self, value):
        self.viewModel.setIconHighlight(value)

    def _setAnimationHighlight(self, value):
        self.viewModel.setAnimationHighlight(value)

    def _setPreset(self, value):
        self.viewModel.setPreset(value)

    def _setShowSoundId(self, value):
        self.viewModel.setShowSoundId(value)

    def _setButtonEnabled(self, buttonName, value):
        button = self._getButton(buttonName)
        if button is not None:
            button.setIsEnabled(value)
        return

    def _getResultData(self):
        return None


class DialogViewMixin(object):
    __slots__ = ('__scope', '__event', '__result')

    def __init__(self, *args, **kwargs):
        super(DialogViewMixin, self).__init__(*args, **kwargs)
        self.__scope = AsyncScope()
        self.__event = AsyncEvent(scope=self.__scope)
        self.__result = DialogButtons.CANCEL

    @async
    def wait(self):
        try:
            yield await(self.__event.wait())
        except BrokenPromiseError:
            _logger.debug('%s has been destroyed without user decision', self)

        raise AsyncReturn(DialogResult(self.__result, self._getAdditionalData()))

    def _sendDialogResult(self, result):
        self.__result = result
        self.__event.set()

    def _getAdditionalData(self):
        return None

    def _dispose(self):
        super(DialogViewMixin, self)._dispose()
        self.__scope.destroy()
