# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/minimap/interfaces.py
from __future__ import absolute_import
import typing
from abc import abstractmethod
if typing.TYPE_CHECKING:
    from account_helpers.settings_core.settings_constants import GAME
    from aih_constants import CTRL_MODE_NAME

class IMinimapPlugin(typing.Protocol):

    @abstractmethod
    def applyNewSize(self, sizeIndex):
        raise NotImplementedError

    @abstractmethod
    def updateControlMode(self, mode, vehicleID):
        raise NotImplementedError

    @abstractmethod
    def initControlMode(self, mode, available):
        raise NotImplementedError

    @abstractmethod
    def updateSettings(self, diff):
        raise NotImplementedError

    @abstractmethod
    def setSettings(self):
        raise NotImplementedError
