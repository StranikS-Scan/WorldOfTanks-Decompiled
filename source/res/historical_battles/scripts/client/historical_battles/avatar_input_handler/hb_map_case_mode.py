# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/avatar_input_handler/hb_map_case_mode.py
import logging
import BigWorld
import AvatarInputHandler.MapCaseMode as BaseMapCaseMode
from helpers import dependency
from items import vehicles
from skeletons.dynamic_objects_cache import IBattleDynamicObjectsCache
logger = logging.getLogger(__name__)

class _HBMapCaseMixin(object):
    __dynamicObjectsCache = dependency.descriptor(IBattleDynamicObjectsCache)

    def enable(self, **args):
        super(_HBMapCaseMixin, self).enable(**args)
        equipmentID = args.get('equipmentID', None)
        self.__showMaxRadiusCircle(equipmentID)
        return

    def disable(self):
        super(_HBMapCaseMixin, self).disable()
        self.__hideMaxRadiusCircle()

    def __showMaxRadiusCircle(self, equipmentID):
        if equipmentID is not None:
            equipment = vehicles.g_cache.equipments()[equipmentID] if equipmentID else None
            maxApplyRadius = getattr(equipment, 'maxApplyRadius', None)
            player = BigWorld.player()
            if not (maxApplyRadius and player):
                return
            vehicle = player.getVehicleAttached()
            dynamicObjects = self.__dynamicObjectsCache.getConfig(player.arenaGuiType)
            if not (vehicle and dynamicObjects):
                return
            circleVisualSettings = dynamicObjects.getCircleRestrictionEffect()
            if circleVisualSettings:
                vehicle.appearance.showTerrainCircle(maxApplyRadius, circleVisualSettings)
        return

    def __hideMaxRadiusCircle(self):
        vehicle = BigWorld.player().getVehicleAttached()
        if vehicle and vehicle.appearance.isTerrainCircleVisible():
            vehicle.appearance.hideTerrainCircle()


class _ArtilleryStrikeHBSelector(BaseMapCaseMode._ArcadeBomberStrikeSelector):
    pass


class _ArtilleryMortarHBSelector(BaseMapCaseMode._ArcadeBomberStrikeSelector):
    pass


class _ArtilleryRocketHBSelector(BaseMapCaseMode._ArcadeBomberStrikeSelector):
    pass


class _BomberHBSelector(BaseMapCaseMode._ArcadeBomberStrikeSelector):
    pass


class _AttackPlaneHBSelector(BaseMapCaseMode._DirectionalAreaStrikeSelector):
    pass


class _MinefieldHBSelector(BaseMapCaseMode._ArcadeFLMinesSelector):
    pass


class _ReconPlaneHBSelector(BaseMapCaseMode._DirectionalAreaStrikeSelector):
    pass


class HBMapCaseControlMode(_HBMapCaseMixin, BaseMapCaseMode.MapCaseControlMode):
    pass
