# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/armor_inspector_component.py
import typing
import logging
from functools import partial
import BigWorld
import CGF
import armor_inspector
from account_helpers.settings_core.settings_constants import GRAPHICS
from cgf_script.component_meta_class import registerComponent
from cgf_script.managers_registrator import autoregister, onAddedQuery, onRemovedQuery
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from cgf_common.cgf_helpers import getParentComponentByGameObject
if typing.TYPE_CHECKING:
    from gui.impl.lobby.vehicle_hub.sub_presenters.armor.config.models import TierModel
    MatInfo = typing.Tuple[int, float, float]
_logger = logging.getLogger(__name__)

@registerComponent
class ArmorInspectorComponent(object):
    domain = CGF.DomainOption.DomainClient

    def __init__(self):
        super(ArmorInspectorComponent, self).__init__()
        self.vehicleID = None
        return


@autoregister(presentInAllWorlds=False, category='Armor Inspector')
class ArmorInspectorManager(CGF.ComponentManager):
    _settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, *args):
        super(ArmorInspectorManager, self).__init__(*args)
        self._timers = {}

    def activate(self):
        self._settingsCore.onSettingsChanged += self._clientColorSettingsChanged
        self._setSettings()

    def deactivate(self):
        self._settingsCore.onSettingsChanged -= self._clientColorSettingsChanged
        self._stopTimer()

    @onAddedQuery(CGF.GameObject, ArmorInspectorComponent, BigWorld.CollisionComponent)
    def onAdded(self, gameObject, armorInspector, collision):
        from HangarVehicle import HangarVehicle
        from gui.impl.lobby.vehicle_hub.sub_presenters.armor.config import getConfig
        from gui.impl.lobby.vehicle_hub.sub_presenters.armor.utils import getAllMatInfos
        vehicle = getParentComponentByGameObject(gameObject, HangarVehicle)
        if vehicle is None:
            _logger.error('Invalid game object for ArmorInspectorComponent! Must be HangarVehicle.')
            return
        else:
            armorInspector.vehicleID = vehicle.id
            typeDescriptor = vehicle.typeDescriptor
            materials = getAllMatInfos(typeDescriptor)
            tierModel = getConfig().tierList.getTierModel(typeDescriptor.level)
            _logger.debug('Showing Armor inspector for entityID: %s', vehicle.id)
            self._stopTimer(vehicle.id)
            timerID = BigWorld.callback(0.5, partial(self._show, vehicle.id, collision, materials, tierModel))
            self._timers[vehicle.id] = timerID
            return

    def _show(self, tankID, collision, materials, tierModel):
        armor_inspector.show(self.spaceID, tankID, collision, materials, (tierModel.normalArmor.min, tierModel.normalArmor.max), (tierModel.spacedArmor.min, tierModel.spacedArmor.max))
        self._stopTimer(tankID)

    @onRemovedQuery(ArmorInspectorComponent)
    def onRemoved(self, component):
        if component.vehicleID is None:
            return
        else:
            _logger.debug('Hiding Armor inspector for entityID: %s', component.vehicleID)
            armor_inspector.hide(self.spaceID, component.vehicleID)
            self._stopTimer(component.vehicleID)
            return

    def _stopTimer(self, vehicleID=None):
        if vehicleID is None:
            for tid in self._timers.values():
                BigWorld.cancelCallback(tid)

            self._timers.clear()
        else:
            tid = self._timers.get(vehicleID)
            if tid is not None:
                BigWorld.cancelCallback(tid)
                del self._timers[vehicleID]
        return

    def _setSettings(self):
        from gui.impl.lobby.vehicle_hub.sub_presenters.armor.config import getConfig
        isColorBlind = self._settingsCore.getSetting(GRAPHICS.COLOR_BLIND)
        configModel = getConfig()
        aiR = R.images.gui.maps.icons.armor_inspector
        armor_inspector.setSettings(self.spaceID, configModel.blendingAlpha, backport.image(aiR.main_armor_cb() if isColorBlind else aiR.main_armor()), backport.image(aiR.spaced_armor_cb() if isColorBlind else aiR.spaced_armor()))

    def _clientColorSettingsChanged(self, diff):
        if GRAPHICS.COLOR_BLIND in diff:
            self._setSettings()
