# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/widgets/witches_widget.py
from halloween.gui.impl.gen.view_models.views.lobby.common.phase_item_model import PhaseStatus
from halloween.gui.impl.gen.view_models.views.lobby.common.witch_item_model import WitchItemModel
from halloween.gui.impl.gen.view_models.views.lobby.witches_model import WitchesModel
from halloween.gui.impl.lobby.base_event_view import isNewOutro
from halloween.hw_constants import PhaseType, QuestType, EVENT_ABILITY_QUEST_PREFIX
from skeletons.gui.game_control import IHalloweenController
from helpers import dependency

class WitchesWidget(object):
    __slots__ = ('__viewModel', '__type')
    _hwController = dependency.descriptor(IHalloweenController)

    def __init__(self, viewModel, parentView):
        self.__viewModel = viewModel
        self.__type = parentView
        super(WitchesWidget, self).__init__()

    @property
    def viewModel(self):
        return self.__viewModel

    def onLoading(self):
        self.updateAll()

    def updateAll(self):
        self.viewModel.setType(self.__type)
        witches = self.viewModel.getWitches()
        phases = self._hwController.phases.getPhasesByType(phaseType=PhaseType.REGULAR)
        witches.clear()
        for phase in phases:
            witch = WitchItemModel()
            witch.setStartDate(phase.getStartTime())
            witch.setEndDate(phase.getFinishTime())
            witch.setPhase(phase.phaseIndex)
            witch.setIsNew(isNewOutro(phase))
            quests = phase.getQuestsByType(QuestType.HALLOWEEN)
            isQuestsCompleted = False
            for quest in quests:
                questId = quest.getQuestId()
                if EVENT_ABILITY_QUEST_PREFIX in questId:
                    if phase.isActive():
                        info = quest.getProgressInfo()
                        witch.setAmount(info['totalProgress'])
                        witch.setProgress(info['currentProgress'])
                    isQuestsCompleted = quest.isCompleted()

            if phase.isActive():
                witch.setStatus(PhaseStatus.ACTIVE)
            if phase.isLock():
                witch.setStatus(PhaseStatus.LOCKED)
            if phase.isOutOfDate() and not isQuestsCompleted:
                witch.setStatus(PhaseStatus.OVERDUE)
            if isQuestsCompleted:
                witch.setStatus(PhaseStatus.COMPLETED)
            witches.addViewModel(witch)

        witches.invalidate()

    def updateNew(self):
        witches = self.viewModel.getWitches()
        for witch in witches:
            phaseIndex = int(witch.getPhase())
            phase = self._hwController.phases.getPhaseByIndex(phaseIndex)
            witch.setIsNew(isNewOutro(phase))

        witches.invalidate()

    def finalize(self):
        self.__viewModel = None
        return
