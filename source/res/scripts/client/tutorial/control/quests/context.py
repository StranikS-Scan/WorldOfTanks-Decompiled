# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/control/quests/context.py
from tutorial.control import game_vars
from tutorial.control.context import StartReqs

class QuestsStartReqs(StartReqs):

    def __validateTutorialsCompleted(self, ctx, descriptor):
        cache = ctx.cache
        self._areAllBonusesReceived = descriptor.areAllBonusesReceived(ctx.bonusCompleted)
        if not self._areAllBonusesReceived:
            return False
        else:
            if cache.wasReset():
                cache.setRefused(True)
            return True

    def prepare(self, ctx):
        ctx.bonusCompleted = game_vars.getTutorialsCompleted()

    def process(self, descriptor, ctx):
        return not self.__validateTutorialsCompleted(ctx, descriptor)
