# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/shared/tooltips/contexts.py
from gui.shared.tooltips import TOOLTIP_COMPONENT
from gui.shared.tooltips.contexts import ToolTipContext
from helpers import dependency
from items import vehicles
from skeletons.gui.game_control import IComp7Controller

class Comp7RoleSkillBattleContext(ToolTipContext):
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def __init__(self):
        super(Comp7RoleSkillBattleContext, self).__init__(TOOLTIP_COMPONENT.FULL_STATS)

    def buildItem(self, roleName):
        return self.__comp7Controller.getRoleEquipment(roleName)

    def getStartLevel(self, roleName):
        return self.__comp7Controller.getEquipmentStartLevel(roleName)


class Comp7RoleSkillLobbyContext(ToolTipContext):

    def __init__(self):
        super(Comp7RoleSkillLobbyContext, self).__init__(TOOLTIP_COMPONENT.HANGAR)

    def buildItem(self, equipmentName):
        cache = vehicles.g_cache
        equipmentID = cache.equipmentIDs().get(equipmentName)
        return cache.equipments().get(equipmentID) if equipmentID is not None else None
