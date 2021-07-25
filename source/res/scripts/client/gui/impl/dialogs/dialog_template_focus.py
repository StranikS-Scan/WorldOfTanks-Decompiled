# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/dialogs/dialog_template_focus.py
import typing
from gui.impl.gen.view_models.views.dialogs.dialog_base_focus_view_model import DialogBaseFocusViewModel
from gui.impl.gen.view_models.views.dialogs.dialog_focus_view_model import DialogFocusViewModel
from gui.impl.pub import ViewImpl
if typing.TYPE_CHECKING:
    from typing import List, Optional, Union, Dict
    from gui.impl.gen.view_models.views.dialogs.dialog_template_view_model import DialogTemplateViewModel

def clampFocusIndex(value, topLimit):
    return -1 if not -1 < value < topLimit else value


class BaseFocusPresenter(ViewImpl):
    __slots__ = ()
    focusElementCount = 0

    def __init__(self, settings, *args, **kwargs):
        msg = 'Model must be an instance of DialogBaseFocusViewModel'
        super(BaseFocusPresenter, self).__init__(settings, *args, **kwargs)

    def updateFocusIndex(self, value):
        viewModel = self.getViewModel()
        viewModel.setFocusedIndex(value)
        return value != -1


class ButtonFocusingHandler(object):
    __slots__ = ('__dialogTemplateViewModel',)

    def __init__(self, dialogTemplateViewModel):
        super(ButtonFocusingHandler, self).__init__()
        self.__dialogTemplateViewModel = dialogTemplateViewModel

    def updateFocusIndex(self, value):
        if value != -1:
            button = self.__dialogTemplateViewModel.getButtons()[value]
            if button.getIsDisabled():
                value = -1
        self.__dialogTemplateViewModel.focus.setFocusedIndex(value)
        return value != -1

    def dispose(self):
        self.__dialogTemplateViewModel = None
        return

    @property
    def focusElementCount(self):
        return len(self.__dialogTemplateViewModel.getButtons())


class DialogTemplateFocusingSystem(object):
    __slots__ = ('__dialogTemplateViewModel', '__presenters', '__currentFocusIndex', '__buttonFocusing', '__indexShifting', '__maxIndex', '__isStarted')

    def __init__(self, dialogTemplateViewModel):
        super(DialogTemplateFocusingSystem, self).__init__()
        self.__dialogTemplateViewModel = dialogTemplateViewModel
        self.__presenters = []
        self.__currentFocusIndex = DialogFocusViewModel.DEFAULT_FOCUSED_INDEX
        self.__buttonFocusing = None
        self.__indexShifting = {}
        self.__maxIndex = -1
        self.__isStarted = False
        self.__buttonFocusing = ButtonFocusingHandler(self.__dialogTemplateViewModel)
        self.addFocusPresenter(self.__buttonFocusing)
        return

    def start(self):
        self.__dialogTemplateViewModel.focus.onTabPressed += self.__tabPressHandler
        count = 0
        for presenter in self.__presenters:
            self.__indexShifting[presenter] = count
            count += presenter.focusElementCount

        self.__maxIndex = count - 1
        self.__isStarted = True
        self.setFocusingIndex(self.__currentFocusIndex)

    def dispose(self):
        self.__dialogTemplateViewModel.focus.onTabPressed -= self.__tabPressHandler
        self.__dialogTemplateViewModel = None
        self.__presenters = None
        self.__indexShifting = None
        self.__buttonFocusing.dispose()
        self.__buttonFocusing = None
        return

    def addFocusPresenter(self, presenter):
        self.__presenters.append(presenter)

    def setFocusingIndex(self, value):
        if not self.__isStarted:
            self.__currentFocusIndex = value
            return
        value = max(-1, min(value, self.__maxIndex))
        self.__currentFocusIndex = value
        for presenter in self.__presenters:
            self.__setFocus(presenter, value)

    def __setFocus(self, presenter, globalIndex):
        localFocusIndex = clampFocusIndex(globalIndex - self.__indexShifting[presenter], presenter.focusElementCount)
        wasFocused = presenter.updateFocusIndex(localFocusIndex)
        return localFocusIndex != -1 and wasFocused

    def __tabPressHandler(self, args):
        isShiftPressed = args.get('shift', False)
        prevFocusIndex = self.__currentFocusIndex
        hasFocused = self.__next(isShiftPressed)
        while not hasFocused and prevFocusIndex != self.__currentFocusIndex:
            hasFocused = self.__next(isShiftPressed)

    def __next(self, backwards):
        self.__currentFocusIndex = (self.__currentFocusIndex - (int(backwards) * 2 - 1)) % (self.__maxIndex + 1)
        hasFocusedItem = False
        for presenter in self.__presenters:
            hasFocusedItem |= self.__setFocus(presenter, self.__currentFocusIndex)

        return hasFocusedItem
