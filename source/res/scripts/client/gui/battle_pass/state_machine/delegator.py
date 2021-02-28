# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_pass/state_machine/delegator.py
import typing
from battle_pass_common import BattlePassRewardReason as BPReason
from frameworks.state_machine import StringEvent, StateEvent
from gui.battle_pass.state_machine.state_machine_helpers import separateRewards, getStylesToChooseUntilChapter
from gui.battle_pass.state_machine.states import StateMachineEventID
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.battle_pass.state_machine.machine import BattlePassStateMachine

class BattlePassRewardLogic(object):
    __slots__ = ('__machine', '__startAfterTurningOnMachine')
    __battlePassController = dependency.descriptor(IBattlePassController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, machine):
        super(BattlePassRewardLogic, self).__init__()
        self.__machine = machine
        self.__startAfterTurningOnMachine = False

    def start(self):
        if self.__machine.isRunning():
            return
        self.__machine.configure()
        self.__machine.start()
        if self.__startAfterTurningOnMachine:
            self.postStateEvent()
            self.__startAfterTurningOnMachine = False

    def stop(self):
        self.__machine.stop()
        self.__startAfterTurningOnMachine = False

    def startRewardFlow(self, rewards, data):
        newLevel = data.get('newLevel', 0) if data is not None else 0
        reason = data.get('reason', BPReason.DEFAULT) if data is not None else BPReason.DEFAULT
        if self.__battlePassController.isFinalLevel(newLevel) and reason not in (BPReason.PURCHASE_BATTLE_PASS, BPReason.PURCHASE_BATTLE_PASS_MULTIPLE):
            chapter = self.__battlePassController.getChapterByLevel(newLevel)
            stylesToChoose = getStylesToChooseUntilChapter(chapter)
        else:
            stylesToChoose = []
        rewardsToChoose, defaultRewards, chosenStyle = separateRewards(rewards, battlePass=self.__battlePassController)
        self.__machine.saveRewards(rewardsToChoose, stylesToChoose, defaultRewards, chosenStyle, data)
        if not self.__machine.isRunning():
            self.__startAfterTurningOnMachine = True
        else:
            self.postStateEvent()
        return

    def startManualFlow(self, rewardsToChoose, stylesToChoose):
        self.__machine.saveRewards(rewardsToChoose, stylesToChoose, None, None, None)
        self.__machine.setManualFlow()
        if not self.__machine.isRunning():
            self.__startAfterTurningOnMachine = True
        else:
            self.postStateEvent()
        return

    def hasActiveFlow(self):
        return self.__machine.hasActiveFlow()

    def hasRewardToChoose(self):
        return self.__machine.hasRewardToChoose()

    def getNextRewardToChoose(self):
        return self.__machine.getNextRewardToChoose()

    def removeRewardToChoose(self, tokenID, isTaken):
        self.__machine.removeRewardToChoose(tokenID, isTaken)

    def addRewards(self, rewards):
        self.__machine.addRewards(rewards)

    def getChosenStyleChapter(self):
        self.__machine.getChosenStyleChapter()

    def markStyleChosen(self, chapter):
        self.__machine.markStyleChosen(chapter)

    def addStyleToChoose(self, chapter):
        self.__machine.addStyleToChoose(chapter)

    def postPreviewOpen(self):
        self.postStringEvent(StateMachineEventID.OPEN_PREVIEW)

    def postClosePreview(self):
        self.postStringEvent(StateMachineEventID.CLOSE_PREVIEW)

    def postStringEvent(self, eventID, **kwargs):
        if self.__machine.isRunning():
            self.__machine.post(StringEvent(eventID, **kwargs))

    def postStateEvent(self, **kwargs):
        if self.__machine.isRunning():
            self.__machine.post(StateEvent(**kwargs))
