# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/formatters/windows.py
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext

class SwitchPeripheryCtx(object):

    def __init__(self, isForbidden=True):
        super(SwitchPeripheryCtx, self).__init__()
        self.__isForbidden = isForbidden

    def getHeader(self):
        raise NotImplementedError

    def getDescription(self):
        raise NotImplementedError

    def getSelectServerLabel(self):
        raise NotImplementedError

    def getApplySwitchLabel(self):
        raise NotImplementedError

    def getExtraChainSteps(self):
        raise NotImplementedError

    def getUpdateTime(self):
        pass

    def isPeripheryAvailable(self, peripheryID):
        return peripheryID not in self._getForbiddenPeripherieIDs() if self.__isForbidden else peripheryID in self._getAllowedPeripherieIDs()

    def _getForbiddenPeripherieIDs(self):
        raise NotImplementedError

    def _getAllowedPeripherieIDs(self):
        raise NotImplementedError


class SwitchPeripheryFortCtx(SwitchPeripheryCtx):
    lobbyContext = dependency.descriptor(ILobbyContext)

    def getHeader(self):
        return backport.msgid(R.strings.prebattle.switchPeripheryWindow.fort.header())

    def getDescription(self):
        return backport.msgid(R.strings.prebattle.switchPeripheryWindow.fort.description())

    def getSelectServerLabel(self):
        return backport.msgid(R.strings.prebattle.switchPeripheryWindow.fort.selectServerLabel())

    def getApplySwitchLabel(self):
        return backport.msgid(R.strings.prebattle.switchPeripheryWindow.fort.applySwitchLabel())

    def getExtraChainSteps(self):
        return None

    def _getForbiddenPeripherieIDs(self):
        return self.lobbyContext.getServerSettings().getForbiddenSortiePeripheryIDs()
