# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/dialogs/challenge/replacement_dialog.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.dialogs.challenge.replacement_dialog_model import ReplacementDialogModel, TaskSwitchType
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogBaseView
from gui.impl.pub.dialog_window import DialogButtons
from items.components.ny_constants import CelebrityQuestTokenParts, CelebrityBattleQuestTypes
from new_year.celebrity.celebrity_quests_helpers import getRerollsCount

class ReplacementDialogView(FullScreenDialogBaseView):
    __MODEL_TYPE = {'_'.join((CelebrityQuestTokenParts.TYPE, CelebrityBattleQuestTypes.SKILL)): TaskSwitchType.SKILL.value,
     '_'.join((CelebrityQuestTokenParts.TYPE, CelebrityBattleQuestTypes.DILIGENCE)): TaskSwitchType.DILIGENCE.value}
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.dialogs.challenge.ReplacementDialog())
        settings.args = args
        settings.kwargs = kwargs
        settings.model = ReplacementDialogModel()
        super(ReplacementDialogView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ReplacementDialogView, self).getViewModel()

    def _onLoading(self, questID, *args, **kwargs):
        super(ReplacementDialogView, self)._onLoading(*args, **kwargs)
        questType = CelebrityQuestTokenParts.getTypeFromFullQuestID(questID)
        with self.viewModel.transaction() as tx:
            tx.setTaskSwitchType(self.__MODEL_TYPE.get(questType, TaskSwitchType.SKILL.value))
            tx.setAvailableReplacements(getRerollsCount())

    def _getEvents(self):
        return ((self.viewModel.onAccept, self._onAccept), (self.viewModel.onCancel, self._onCancel))

    def _onAccept(self):
        self._setResult(DialogButtons.SUBMIT)

    def _onCancel(self):
        self._setResult(DialogButtons.CANCEL)
