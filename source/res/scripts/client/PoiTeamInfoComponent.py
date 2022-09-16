# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/PoiTeamInfoComponent.py
import logging
import typing
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from script_component.ScriptComponent import ScriptComponent
from helpers import dependency
from items import vehicles
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from gui.battle_control.arena_info.interfaces import IPointsOfInterestController
_logger = logging.getLogger(__name__)

class PoiTeamInfoComponent(ScriptComponent):
    REQUIRED_BONUS_CAP = ARENA_BONUS_TYPE_CAPS.POINTS_OF_INTEREST

    def __init__(self):
        super(PoiTeamInfoComponent, self).__init__()
        self.__sessionProvider = dependency.instance(IBattleSessionProvider)

    def onEnterWorld(self, _):
        _logger.debug('PoiTeamInfoComponent.onEnterWorld. TeamID=%s', self.entity.teamID)

    def onLeaveWorld(self):
        _logger.debug('PoiTeamInfoComponent.onLeaveWorld. TeamID=%s', self.entity.teamID)

    def onPoiEquipmentUsed(self, vehicleID, equipmentID):
        equipment = vehicles.g_cache.equipments().get(equipmentID)
        if equipment is None:
            _logger.error('Equipment %s does not exist', equipmentID)
            return
        else:
            poiCtrl = self.__sessionProvider.dynamic.pointsOfInterest
            if poiCtrl is not None:
                poiCtrl.onPoiEquipmentUsed(equipment, vehicleID)
            return

    def onPoiCaptured(self, poiID, vehicleID):
        poiCtrl = self.__sessionProvider.dynamic.pointsOfInterest
        if poiCtrl is not None:
            poiCtrl.onPoiCaptured(poiID, vehicleID)
        return
