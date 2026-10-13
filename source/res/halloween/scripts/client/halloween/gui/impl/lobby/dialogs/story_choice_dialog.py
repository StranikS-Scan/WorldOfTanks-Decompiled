# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/dialogs/story_choice_dialog.py
from __future__ import absolute_import
from PlayerEvents import g_playerEvents
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogBaseView
from gui.impl.pub.dialog_window import DialogButtons
from halloween.gui.impl.gen.view_models.views.lobby.dialogs.story_choice_dialog_model import StoryChoiceDialogModel

class StoryChoiceDialog(FullScreenDialogBaseView):

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.halloween.mono.lobby.dialogs.story_choice_confirm(), model=StoryChoiceDialogModel(), args=args, kwargs=kwargs)
        super(StoryChoiceDialog, self).__init__(settings, *args, **kwargs)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onSubmitClick, self._onSubmitClick),
         (self.viewModel.onCloseClick, self._onCloseClick),
         (self.viewModel.onCancelClick, self._onCancelClick),
         (g_playerEvents.onAccountBecomeNonPlayer, self.destroyWindow))

    def _onLoading(self, *args, **kwargs):
        super(StoryChoiceDialog, self)._onLoading(*args, **kwargs)
        choice = kwargs.get('choice', '')
        if choice:
            self.viewModel.setChoice(choice)

    def _onSubmitClick(self):
        self._setResult(DialogButtons.SUBMIT)

    def _onCancelClick(self):
        self._setResult(DialogButtons.CANCEL)

    def _onCloseClick(self):
        self._setResult(DialogButtons.CANCEL)
