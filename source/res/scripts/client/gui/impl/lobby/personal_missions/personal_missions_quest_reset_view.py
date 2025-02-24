# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_missions/personal_missions_quest_reset_view.py
from functools import partial
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.Waiting import Waiting
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.personal_missions.personal_missions_quest_reset_view_model import PersonalMissionsQuestResetViewModel
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogBaseView
from gui.impl.pub.dialog_window import DialogButtons
from gui.shared.view_helpers.blur_manager import CachedBlur
from helpers import dependency
from skeletons.gui.game_control import IPersonalMissionsController

class PersonalMissionsQuestResetView(FullScreenDialogBaseView):
    __slots__ = ('questId', '__blur')
    __personalMissionsController = dependency.descriptor(IPersonalMissionsController)

    def __init__(self, questId):
        settings = ViewSettings(R.views.lobby.personal_missions.PersonalMissionsQuestResetView())
        settings.flags = ViewFlags.OLD_STYLE_VIEW
        settings.model = PersonalMissionsQuestResetViewModel()
        self.questId = questId
        self.__blur = None
        super(PersonalMissionsQuestResetView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(PersonalMissionsQuestResetView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(PersonalMissionsQuestResetView, self)._onLoading(*args, **kwargs)
        if self.questId is None:
            self.__onClose()
            return
        else:
            self.__updateData()
            Waiting.suspend(lockerID=id(self))
            window = self.getParentWindow()
            self.__blur = CachedBlur(enabled=True, ownLayer=window.layer - 1)
            return

    def _finalize(self):
        if self.__blur is not None:
            self.__blur.fini()
        super(PersonalMissionsQuestResetView, self)._finalize()
        return

    def _getEvents(self):
        return ((self.viewModel.onConfirm, partial(self._setResult, DialogButtons.SUBMIT)), (self.viewModel.onClose, partial(self._setResult, DialogButtons.CANCEL)))

    def __updateData(self, *_):
        with self.viewModel.transaction() as vm:
            quest = self.__personalMissionsController.getQuest(self.questId)
            vm.setQuestName(quest.getUserName())
