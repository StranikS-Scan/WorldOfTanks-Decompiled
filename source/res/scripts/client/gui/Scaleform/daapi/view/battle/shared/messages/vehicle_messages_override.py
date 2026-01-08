# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/messages/vehicle_messages_override.py
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.game_control import IBootcampController
from constants import ARENA_GUI_TYPE

class VehicleMessageOverride(object):
    __slots__ = ('__usualObject',)
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    bootcampController = dependency.descriptor(IBootcampController)

    def __init__(self, usualObject):
        self.__usualObject = usualObject

    def __call__(self):
        if self.bootcampController.isInBootcamp():
            from gui.Scaleform.daapi.view.bootcamp.BCVehicleMessages import BCVehicleMessages
            return BCVehicleMessages
        if self.sessionProvider.arenaVisitor.getArenaGuiType() in ARENA_GUI_TYPE.EPIC_RANGE:
            from gui.Scaleform.daapi.view.battle.epic.messages import EpicVehicleMessages
            return EpicVehicleMessages
        return self.__usualObject
