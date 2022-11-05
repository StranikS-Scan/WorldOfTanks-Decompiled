# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/helpers/tips.py
import random
from cgf_components.marker_component import IBattleSessionProvider
from fun_random.gui.feature.util.fun_mixins import FunSubModesWatcher
from fun_random.gui.feature.util.fun_wrappers import hasBattleSubMode
from gui.impl.gen import R
from helpers import dependency
from helpers.tips import TipsCriteria, TipData

class FunRandomTipsCriteria(TipsCriteria, FunSubModesWatcher):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    @hasBattleSubMode(defReturn=TipData(R.invalid(), R.invalid(), R.invalid()))
    def find(self):
        battleSubMode = self.getBattleSubMode(self.__sessionProvider.arenaVisitor)
        iconsRoot = battleSubMode.getIconsResRoot()
        tips = [ TipData(tipRes.title(), tipRes.description(), iconsRoot.tips.dyn(tipID)()) for tipID, tipRes in battleSubMode.getLocalsResRoot().tips.items() ]
        return random.choice(tips) if tips else TipData(R.invalid(), R.invalid(), R.invalid())

    def _getTipsValidator(self):
        return None
