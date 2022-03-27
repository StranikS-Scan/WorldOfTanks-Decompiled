# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/commander/spawn_ctrl/interfaces.py
import typing
from abc import ABCMeta
from gui.battle_control.controllers.spawn_ctrl import ISpawnListener
if typing.TYPE_CHECKING:
    from typing import List, Optional
    from gui.battle_control.controllers.commander.spawn_ctrl.common import ChosenPointData

class IRTSSpawnListener(ISpawnListener):

    def onEntitySelected(self):
        raise NotImplementedError

    def updatePointsList(self):
        raise NotImplementedError


class ISpawnEntity(object):

    def getID(self):
        raise NotImplementedError

    def getType(self):
        raise NotImplementedError

    @property
    def isVehicle(self):
        raise NotImplementedError

    @property
    def isSupply(self):
        raise NotImplementedError

    @property
    def isSettled(self):
        raise NotImplementedError

    @property
    def chosenPointData(self):
        raise NotImplementedError

    @chosenPointData.setter
    def chosenPointData(self, value):
        raise NotImplementedError


class ISupplyContainerEntity(ISpawnEntity):
    __metaclass__ = ABCMeta

    @property
    def settledCount(self):
        raise NotImplementedError

    @property
    def supplies(self):
        raise NotImplementedError

    def addSupply(self, entityID):
        raise NotImplementedError

    def selectSupply(self, entity):
        raise NotImplementedError
