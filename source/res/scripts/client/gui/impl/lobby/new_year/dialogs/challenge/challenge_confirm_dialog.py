# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/dialogs/challenge/challenge_confirm_dialog.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.dialogs.challenge.challenge_confirm_dialog_model import ChallengeConfirmDialogModel, DialogViews
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogBaseView
from gui.impl.pub.dialog_window import DialogButtons

class ChallengeConfirmDialogView(FullScreenDialogBaseView):
    __slots__ = ('__presenters', '__presenter', '__isInProcess')

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.dialogs.challenge.ChallengeConfirmDialog())
        settings.args = args
        settings.kwargs = kwargs
        settings.model = ChallengeConfirmDialogModel()
        self.__presenter = None
        self.__presenters = {DialogViews.TASKSWITCH: self.__loadTaskSwitchPresenter,
         DialogViews.DISCOUNT: self.__loadDiscountPresenter}
        self.__isInProcess = False
        super(ChallengeConfirmDialogView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(ChallengeConfirmDialogView, self).getViewModel()

    def _finalize(self):
        if self.__presenter:
            self.__presenter.finalize()
            self.__presenter = None
        super(ChallengeConfirmDialogView, self)._finalize()
        return

    def _getEvents(self):
        events = super(ChallengeConfirmDialogView, self)._getEvents()
        return events + ((self.viewModel.onClose, self.__onClose),)

    def _onLoading(self, viewType, *args, **kwargs):
        super(ChallengeConfirmDialogView, self)._onLoading(args, kwargs)
        self.__presenter = self.__presenters.get(viewType)()
        if self.__presenter:
            self.__presenter.initialize(*args, **kwargs)
            self.viewModel.setCurrentViewID(self.__presenter.layoutID)

    def __loadTaskSwitchPresenter(self):
        from gui.impl.lobby.new_year.dialogs.challenge.challenge_task_switch import ChallengeTaskSwitch
        return ChallengeTaskSwitch(self.viewModel.challengeTaskSwitchModel, self)

    def __loadDiscountPresenter(self):
        from gui.impl.lobby.new_year.dialogs.challenge.challenge_discount import ChallengeDiscount
        return ChallengeDiscount(self.viewModel.challengeDiscountModel, self)

    def __onClose(self):
        if self.__isInProcess:
            return
        self.onCancel()

    def onRequestProcessChange(self, isInProcess):
        self.__isInProcess = isInProcess

    def onAccept(self):
        self._setResult(DialogButtons.SUBMIT)

    def onCancel(self):
        self._setResult(DialogButtons.CANCEL)
