# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/dialogs/dialog_template.py
import typing
from frameworks.wulf import ViewSettings, ViewStatus
from gui.impl.dialogs.dialog_template_focus import BaseFocusPresenter, DialogTemplateFocusingSystem
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.dialog_template_place_holder_view_model import DialogTemplatePlaceHolderViewModel
from gui.impl.gen.view_models.views.dialogs.dialog_template_view_model import DialogTemplateViewModel
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogBaseView
from gui.impl.pub.dialog_window import DialogButtons
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
if typing.TYPE_CHECKING:
    from typing import List, Dict, Optional
    from frameworks.wulf import View
    from gui.impl.dialogs.dialog_template_button import ButtonPresenter

class DialogTemplateView(FullScreenDialogBaseView):
    __slots__ = ('_subViews', '__buttonPresenters', '__uniqueID', '__focusingSystem')
    __appLoader = dependency.descriptor(IAppLoader)
    LAYOUT_ID = R.views.dialogs.DefaultDialog()

    def __init__(self, layoutID=None, uniqueID=None, *args, **kwargs):
        settings = ViewSettings(layoutID or self.LAYOUT_ID)
        model = settings.model = DialogTemplateViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(DialogTemplateView, self).__init__(settings, *args, **kwargs)
        self._subViews = []
        self.__buttonPresenters = {}
        self.__uniqueID = uniqueID
        self.__focusingSystem = DialogTemplateFocusingSystem(model)
        self.__appLoader.getApp().gameInputManager.addEscapeListener(self._closeClickHandler)

    @property
    def uniqueID(self):
        return self.__uniqueID

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.dialogs.common.DialogTemplateGenericTooltip():
            buttonID = event.getArgument('buttonID')
            tooltipFactory = self.__buttonPresenters[buttonID].tooltipFactory
            if tooltipFactory:
                return tooltipFactory()
        return super(DialogTemplateView, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(DialogTemplateView, self)._onLoading(*args, **kwargs)
        self.viewModel.onButtonClicked += self._buttonClickHandler
        self.viewModel.onCloseClicked += self._closeClickHandler
        placeHolderList = self.viewModel.getPlaceHolders()
        for placeHolder, resourceID, presenter in self._subViews:
            placeHolderVM = DialogTemplatePlaceHolderViewModel()
            placeHolderVM.setPlaceHolder(placeHolder)
            placeHolderVM.setResourceID(resourceID)
            placeHolderList.addViewModel(placeHolderVM)
            if isinstance(presenter, BaseFocusPresenter):
                self.__focusingSystem.addFocusPresenter(presenter)

        for presenter in self.__buttonPresenters.values():
            presenter.initialize()

        self.__focusingSystem.start()

    def _onLoaded(self, *args, **kwargs):
        super(DialogTemplateView, self)._onLoaded(*args, **kwargs)
        self.__appLoader.getApp().gameInputManager.removeEscapeListener(self._closeClickHandler)
        for _, resourceID, view in self._subViews:
            self.setChildView(resourceID, view)

    def _finalize(self):
        for presenter in self.__buttonPresenters.values():
            presenter.dispose()

        self.__buttonPresenters.clear()
        self.__focusingSystem.dispose()
        gameInputManager = self.__appLoader.getApp().gameInputManager
        if gameInputManager:
            gameInputManager.removeEscapeListener(self._closeClickHandler)
        self.viewModel.onButtonClicked -= self._buttonClickHandler
        self.viewModel.onCloseClicked -= self._closeClickHandler
        super(DialogTemplateView, self)._finalize()

    def _closeClickHandler(self, _=None):
        self._setResult(DialogButtons.CANCEL)

    def _buttonClickHandler(self, args):
        self._setResult(args.get('buttonID'))

    def addButton(self, buttonPresenter):
        buttonID = buttonPresenter.buttonID
        msg = 'there is already registered button with the given buttonID: ' + buttonID
        buttons = self.viewModel.getButtons()
        buttons.addViewModel(buttonPresenter.viewModel)
        self.__buttonPresenters[buttonID] = buttonPresenter

    def getButton(self, buttonID):
        return self.__buttonPresenters.get(buttonID)

    def setSubView(self, placeHolderName, view):
        msg = 'You must specify all sub-views before template has been loaded'
        self._subViews.append((placeHolderName, view.layoutID, view))

    def getSubView(self, placeHolderName):
        return next((subView for placeHolder, _, subView in self._subViews if placeHolder == placeHolderName), None)

    def setBackgroundImagePath(self, resourceID):
        self.viewModel.setBackground(resourceID)

    def removeBackgroundDimmer(self):
        self.viewModel.setIsBackgroundDimmed(False)

    def setFocusedIndex(self, value):
        self.__focusingSystem.setFocusingIndex(value)
