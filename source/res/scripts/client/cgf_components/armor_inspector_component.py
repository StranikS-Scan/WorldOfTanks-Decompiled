# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/armor_inspector_component.py
import typing
import logging
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
    MatInfo = typing.Tuple[int, float, float, int]
_logger = logging.getLogger(__name__)

@registerComponent
class ArmorInspectorComponent(object):
    domain = CGF.DomainOption.DomainClient

    def __init__(self):
        super(ArmorInspectorComponent, self).__init__()
        self.vehicleID = None
        self.fadeOnRemove = False
        self.showProbability = False
        return


@autoregister(presentInAllWorlds=False, category='Armor Inspector')
class ArmorInspectorManager(CGF.ComponentManager):
    _settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        super(ArmorInspectorManager, self).__init__()
        self._appearanceListeners = {}

    def activate(self):
        self._settingsCore.onSettingsChanged += self._clientColorSettingsChanged
        self._setSettings()

    def deactivate(self):
        self._settingsCore.onSettingsChanged -= self._clientColorSettingsChanged

    @onAddedQuery(CGF.GameObject, ArmorInspectorComponent)
    def onAdded(self, gameObject, armorInspector):
        from HangarVehicle import HangarVehicle
        from gui.impl.lobby.vehicle_hub.sub_presenters.armor.config import getConfig
        from gui.impl.lobby.vehicle_hub.sub_presenters.armor.utils import getAllMatInfos
        vehicle = getParentComponentByGameObject(gameObject, HangarVehicle)
        if vehicle is None:
            _logger.error('Invalid game object for ArmorInspectorComponent! Must be HangarVehicle.')
            return
        else:
            armorInspector.vehicleID = vehicle.id
            materials = getAllMatInfos(vehicle)
            tierModel = getConfig().tierList.getTierModel(vehicle.typeDescriptor.level)
            _logger.debug('Showing Armor inspector for entityID: %s', vehicle.id)
            self._show(vehicle.id, gameObject, materials, tierModel, armorInspector.showProbability, True)
            self._registerAttachmentsUpdates(armorInspector, gameObject, tierModel)
            return

    def _show(self, tankID, gameObject, materials, tierModel, showProbability, withFade):
        armor_inspector.show(self.spaceID, tankID, gameObject, materials, (tierModel.normalArmor.min, tierModel.normalArmor.max), (tierModel.spacedArmor.min, tierModel.spacedArmor.max), showProbability, withFade)

    @onRemovedQuery(CGF.GameObject, ArmorInspectorComponent)
    def onRemoved(self, gameObject, component):
        if component.vehicleID is None:
            return
        else:
            _logger.debug('Hiding Armor inspector for entityID: %s', component.vehicleID)
            self._unregisterAttachmentsUpdates(component)
            armor_inspector.hide(self.spaceID, component.vehicleID, component.fadeOnRemove)
            return

    def _setSettings(self):
        from gui.impl.lobby.vehicle_hub.sub_presenters.armor.config import getConfig
        isColorBlind = self._settingsCore.getSetting(GRAPHICS.COLOR_BLIND)
        configModel = getConfig()
        aiR = R.images.gui.maps.icons.armor_inspector
        actualColorList = configModel.getActualColorList(isColorBlind)
        armor_inspector.setSettings(self.spaceID, configModel.blendingAlpha, backport.image(aiR.main_armor_cb() if isColorBlind else aiR.main_armor()), backport.image(aiR.spaced_armor_cb() if isColorBlind else aiR.spaced_armor()), backport.image(aiR.penetration_chance_cdf_cb() if isColorBlind else aiR.penetration_chance_cdf()), actualColorList.ricochet, actualColorList.noDamage)

    def _clientColorSettingsChanged(self, diff):
        if GRAPHICS.COLOR_BLIND in diff:
            self._setSettings()

    def _registerAttachmentsUpdates(self, armorInspector, gameObject, tierModel):
        from HangarVehicle import HangarVehicle
        from gui.impl.lobby.vehicle_hub.sub_presenters.armor.utils import getAllMatInfos
        vehicle = getParentComponentByGameObject(gameObject, HangarVehicle)
        if vehicle is None:
            return
        else:

            def _onAttachmentsUpdated():
                materials = getAllMatInfos(vehicle)
                self._show(vehicle.id, gameObject, materials, tierModel, armorInspector.showProbability, False)

            appearance = vehicle.appearance
            appearance.onAttachmentsUpdated += _onAttachmentsUpdated
            self._appearanceListeners[armorInspector] = (appearance, _onAttachmentsUpdated)
            return

    def _unregisterAttachmentsUpdates(self, armorInspector):
        listener = self._appearanceListeners.pop(armorInspector, None)
        if listener is None:
            return
        else:
            appearance, callback = listener
            appearance.onAttachmentsUpdated -= callback
            return
