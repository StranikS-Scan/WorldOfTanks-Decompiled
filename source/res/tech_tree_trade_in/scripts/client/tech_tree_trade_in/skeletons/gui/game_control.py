# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tech_tree_trade_in/scripts/client/tech_tree_trade_in/skeletons/gui/game_control.py
from enum import Enum
import typing
from collections import namedtuple
from skeletons.gui.game_control import IGameController
from tech_tree_trade_in_common.helpers import Token
if typing.TYPE_CHECKING:
    from typing import Callable, Generator, Optional
    T_PROCESSOR_CALLBACK = Callable[[bool], None]
TechTreeBranch = namedtuple('TechTreeBranch', ['branchId', 'vehCDs'])

class BranchType(Enum):
    BRANCHES_TO_TRADE = 'branchesToTrade'
    BRANCHES_TO_RECEIVE = 'branchesToReceive'


class GuiSettingsTradeInUrlName(Enum):
    VIDEO = 'introVideo'
    INFO_PAGE = 'infoPage'


class ITechTreeTradeInController(IGameController):
    onSettingsChanged = None
    onEntryPointUpdated = None
    onPlayerTradeInStatusChanged = None

    @property
    def isTechTreeTradeInEntryPointEnabled(self):
        raise NotImplementedError

    def getBranchById(self, branchId, branchTypeKey):
        raise NotImplementedError

    def getBranchesToTradeSortedForNation(self):
        return NotImplementedError

    def getBranchesToReceiveSortedForNation(self):
        raise NotImplementedError

    def getConfig(self):
        raise NotImplementedError

    def getEndTime(self):
        raise NotImplementedError

    def getTradeInToken(self):
        raise NotImplementedError

    @staticmethod
    def getTradeInURL(urlName):
        raise NotImplementedError

    def isEnabled(self):
        raise NotImplementedError

    def isTradeInAvailableForPlayer(self):
        raise NotImplementedError

    def requestTradeIn(self, branchToTradeID, branchToReceiveID, multiPrice, callback=None):
        raise NotImplementedError

    def requestTradeInDryRun(self, branchToTradeID, branchToReceiveID, callback):
        raise NotImplementedError

    def showTechTreeTradeInView(self):
        raise NotImplementedError

    def showOnboardingIntroVideo(self):
        raise NotImplementedError
