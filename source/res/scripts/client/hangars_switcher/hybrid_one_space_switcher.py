# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/hangars_switcher/hybrid_one_space_switcher.py
from helpers import dependency
from skeletons.hangars_switcher import IHangarsSwitcher
from skeletons.hangars_switcher import IHangarPlaceManager

class HybridOneSpaceSwitcher(IHangarsSwitcher):
    hangarPlaceMgr = dependency.descriptor(IHangarPlaceManager)

    def switchToHangar(self, hangarName):
        self.hangarPlaceMgr.switchPlaceTo(hangarName)
