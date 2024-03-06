# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/prebattle_hints/controller.py
import typing
if typing.TYPE_CHECKING:
    from hints_common.prebattle.schemas import BaseHintModel

class IPrebattleHintsController(object):

    def fini(self):
        raise NotImplementedError

    def isEnabled(self):
        raise NotImplementedError

    def isEnabledForCurrentBattleSession(self):
        raise NotImplementedError

    def addControlStrategy(self, arenaBonusType, strategy):
        raise NotImplementedError

    def removeControlStrategy(self, arenaBonusType):
        raise NotImplementedError

    def onShowHintsWindowSuccess(self, hint):
        raise NotImplementedError


class IPrebattleHintsControlStrategy(object):

    def hasHintToShow(self, arenaBonusType):
        raise NotImplementedError

    def getHintToShow(self, arenaBonusType):
        raise NotImplementedError

    def onShowHintsWindowSuccess(self, hint):
        raise NotImplementedError
