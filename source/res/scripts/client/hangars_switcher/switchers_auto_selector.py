# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/hangars_switcher/switchers_auto_selector.py
from helpers import dependency
from skeletons.hangars_switcher import ISwitchersAutoSelector
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.hangars_switcher import IHangarsSwitchManager
from hangars_switcher.reload_spaces_switcher import ReloadSpacesSwitcher
from hangars_switcher.hybrid_one_space_switcher import HybridOneSpaceSwitcher
from hangars_switcher.nothing_todo_switcher import NothingToDoSwitcher

class SwitchersAutoSelector(ISwitchersAutoSelector):
    hangarSpace = dependency.descriptor(IHangarSpace)
    hangarsSwitchManager = dependency.descriptor(IHangarsSwitchManager)

    def __init__(self):
        super(SwitchersAutoSelector, self).__init__()
        reloadSpacesSwitcher = ReloadSpacesSwitcher()
        hybridOneSpaceSwitcher = HybridOneSpaceSwitcher()
        self.__switchers = {'spaces/h20_wot_bday': reloadSpacesSwitcher,
         'spaces/h26_battle_royale': reloadSpacesSwitcher,
         'spaces/h20_wot_bday_h26_br': hybridOneSpaceSwitcher}

    def init(self):
        self.hangarSpace.onSpaceCreating += self.__onHangarSpaceCreating

    def destroy(self):
        self.hangarSpace.onSpaceCreating -= self.__onHangarSpaceCreating

    def __onHangarSpaceCreating(self):
        if self.hangarSpace.spacePath in self.__switchers:
            switcher = self.__switchers[self.hangarSpace.spacePath]
        else:
            switcher = NothingToDoSwitcher()
        self.hangarsSwitchManager.registerHangarsSwitcher(switcher)
