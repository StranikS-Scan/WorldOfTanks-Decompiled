# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/dialogs/challenge/challenge_task_switch.py
from frameworks.wulf.view.submodel_presenter import SubModelPresenter
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.dialogs.challenge.sub_views.challenge_task_switch_model import ChallengeTaskSwitchModel, TaskSwitchType
from gui.shared.utils import decorators
from items.components.ny_constants import CelebrityBattleQuestTypes, CelebrityQuestTokenParts
from new_year.celebrity.celebrity_quests_helpers import getRerollsCount
from new_year.ny_processor import RerollCelebrityQuestProcessor

class ChallengeTaskSwitch(SubModelPresenter):
    __MODEL_TYPE = {'_'.join((CelebrityQuestTokenParts.TYPE, CelebrityBattleQuestTypes.SKILL)): TaskSwitchType.SKILL.value,
     '_'.join((CelebrityQuestTokenParts.TYPE, CelebrityBattleQuestTypes.DILIGENCE)): TaskSwitchType.DILIGENCE.value}

    def __init__(self, viewModel, parentView):
        super(ChallengeTaskSwitch, self).__init__(viewModel, parentView)
        self.__questID = ''

    @property
    def layoutID(self):
        return R.views.lobby.new_year.dialogs.challenge.sub_views.ChallengeTaskSwitch()

    @property
    def viewModel(self):
        return self.getViewModel()

    def initialize(self, questID, *args, **kwargs):
        super(ChallengeTaskSwitch, self).initialize(*args, **kwargs)
        self.__questID = str(questID)
        questType = CelebrityQuestTokenParts.getTypeFromFullQuestID(questID)
        with self.viewModel.transaction() as tx:
            tx.setTaskSwitchType(self.__MODEL_TYPE.get(questType, TaskSwitchType.SKILL.value))
            tx.setAvailableSwitches(getRerollsCount())

    def _getEvents(self):
        events = super(ChallengeTaskSwitch, self)._getEvents()
        return events + ((self.viewModel.onAccept, self.__onAccept), (self.viewModel.onCancel, self.parentView.onCancel))

    @decorators.adisp_process('updating')
    def __onAccept(self):
        self.parentView.onRequestProcessChange(True)
        result = yield RerollCelebrityQuestProcessor(self.__questID).request()
        if result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType, priority=result.msgPriority)
        if result.success:
            self.parentView.onAccept()
        else:
            clientErrKey = result.auxData.get('clientErrKey')
            if not clientErrKey:
                clientErrKey = 'server'
            errorStr = backport.text(R.strings.ny.challenge.dialogs.switch.err.dyn(clientErrKey)())
            self.viewModel.setErrorMessage(errorStr)
        self.parentView.onRequestProcessChange(False)
