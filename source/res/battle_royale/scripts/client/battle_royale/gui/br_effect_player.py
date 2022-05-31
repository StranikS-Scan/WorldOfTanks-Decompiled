# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/br_effect_player.py
import logging
import BigWorld
import CGF
import GenericComponents
from helpers import dependency
from battle_royale.gui.battle_control.controllers.progression_ctrl import IProgressionListener
from gui.battle_control.view_components import IViewComponentsCtrlListener
from helpers import time_utils
from skeletons.dynamic_objects_cache import IBattleDynamicObjectsCache
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)

class BRUpgradeEffectPlayer(IProgressionListener, IViewComponentsCtrlListener):
    __dynObjectsCache = dependency.descriptor(IBattleDynamicObjectsCache)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __UPGRADE_INVALIDATION_TIME = 3

    def __init__(self):
        super(BRUpgradeEffectPlayer, self).__init__()
        self.__effectConfig = None
        self.__upgradeStarted = {}
        return

    def detachedFromCtrl(self, ctrlID):
        self.__effectConfig = None
        return

    def setVehicleVisualChangingStarted(self, vehicleID):
        vehicle = BigWorld.entities.get(vehicleID)
        if vehicle is not None and vehicle.isStarted:
            self.__upgradeStarted[vehicleID] = time_utils.getServerUTCTime()
        return

    def setVehicleVisualChangingFinished(self, vehicleID):
        if vehicleID in self.__upgradeStarted:
            if time_utils.getServerUTCTime() - self.__upgradeStarted.pop(vehicleID) > self.__UPGRADE_INVALIDATION_TIME:
                _logger.warning('Upgrade finish invalidated for vehicle %s: too much time passed since start', vehicleID)
                return
            self.__playEffect(vehicleID)

    def __playEffect(self, vehicleID):
        vehicle = BigWorld.entities.get(vehicleID)
        if vehicle:
            config = self.__dynObjectsCache.getConfig(self.__sessionProvider.arenaVisitor.getArenaGuiType()).getVehicleUpgradeEffect().effectDescr
            gameObject = CGF.GameObject(vehicle.appearance.spaceID)
            gameObject.createComponent(GenericComponents.HierarchyComponent, vehicle.appearance.gameObject)
            gameObject.createComponent(GenericComponents.ParticleComponent, config.path, True, config.rate)
            gameObject.createComponent(GenericComponents.TransformComponent, config.offset)
            gameObject.activate()
            gameObject.transferOwnershipToWorld()
        else:
            _logger.warning('Unable to get vehicle by id %s', vehicleID)
