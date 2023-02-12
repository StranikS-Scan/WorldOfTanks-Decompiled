# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/control/bootcamp/lobby/context.py
from tutorial.control import context
from helpers import dependency
from skeletons.gui.game_control import IBootcampController

class BootcampLobbyStartReqs(context.StartReqs):

    def isEnabled(self):
        return self.bootcampController.isInBootcamp()

    def prepare(self, ctx):
        pass

    def process(self, descriptor, ctx):
        return True


class BootcampBonusesRequester(context.BonusesRequester):
    bootcampController = dependency.descriptor(IBootcampController)

    def __init__(self):
        lessonNum = self.bootcampController.getLessonNum()
        wonBattlesMask = (1 << lessonNum) - 1
        super(BootcampBonusesRequester, self).__init__(completed=wonBattlesMask)

    def setCompleted(self, _):
        pass

    def request(self, _=None):
        pass
