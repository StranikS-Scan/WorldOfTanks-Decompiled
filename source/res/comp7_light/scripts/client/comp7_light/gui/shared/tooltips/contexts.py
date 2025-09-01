# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/shared/tooltips/contexts.py
from gui.shared.tooltips import TOOLTIP_COMPONENT
from gui.shared.tooltips.contexts import ToolTipContext
from helpers import dependency
from items import vehicles
from skeletons.gui.game_control import IComp7LightController

class Comp7LightRoleSkillBattleContext(ToolTipContext):
    __comp7LightController = dependency.descriptor(IComp7LightController)

    def __init__(self):
        super(Comp7LightRoleSkillBattleContext, self).__init__(TOOLTIP_COMPONENT.FULL_STATS)

    def buildItem(self, roleName):
        return self.__comp7LightController.getRoleEquipment(roleName)

    def getStartLevel(self, roleName):
        return self.__comp7LightController.getEquipmentStartLevel(roleName)


class Comp7LightRoleSkillLobbyContext(ToolTipContext):

    def __init__(self):
        super(Comp7LightRoleSkillLobbyContext, self).__init__(TOOLTIP_COMPONENT.HANGAR)

    def buildItem(self, equipmentName):
        cache = vehicles.g_cache
        equipmentID = cache.equipmentIDs().get(equipmentName)
        return cache.equipments().get(equipmentID) if equipmentID is not None else None
