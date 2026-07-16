# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/armor_inspector_component.py
from __future__ import absolute_import
import typing
import logging
from collections import namedtuple
import BigWorld
import CGF
import armor_inspector
from account_helpers.settings_core.settings_constants import GRAPHICS
from cgf_script.registration import registerComponent
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from shared_utils import nextTick
from skeletons.account_helpers.settings_core import ISettingsCore
from constants import IS_EDITOR, IS_CGF_DUMP
if typing.TYPE_CHECKING:
    from gui.impl.lobby.vehicle_hub.sub_presenters.armor.config.models import TierModel
    MatInfo = typing.Tuple[int, float, float]
_logger = logging.getLogger(__name__)
_PendingShow = namedtuple('_PendingShow', ('vehicleID', 'gameObject', 'tierModel', 'showProbability', 'withFade'))
if IS_EDITOR or IS_CGF_DUMP:

    class HangarVehicle(object):
        pass


else:
    from HangarVehicle import HangarVehicle

@registerComponent
class ArmorInspectorComponent(object):
    domain = CGF.Domain.Client
    editorTitle = 'Armor Inspector'

    def __init__(self):
        super(ArmorInspectorComponent, self).__init__()
        self.vehicleID = None
        self.fadeOnRemove = False
        self.showProbability = False
        return


class ArmorInspectorSystem(CGF.System):
    _settingsCore = dependency.descriptor(ISettingsCore)
    InspectorActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRw(ArmorInspectorComponent))
    InspectorDeactivated = CGF.DeactivateReaction(CGF.GameObject, CGF.ReactRo(ArmorInspectorComponent))
    HangarVehicleAccess = CGF.AccessReaction(CGF.Rw(HangarVehicle))
    Reactions = CGF.Reactions(InspectorActivated, InspectorDeactivated, HangarVehicleAccess)

    def __init__(self, *args):
        super(ArmorInspectorSystem, self).__init__(*args)
        self._appearanceListeners = {}
        self._pendingShow = None
        return

    def update(self):
        vehicleAccess = self.reaction(self.HangarVehicleAccess)
        for go, component in self.reaction(self.InspectorDeactivated):
            self.onRemoved(go, component)

        for go, armorInspector in self.reaction(self.InspectorActivated):
            self.onAdded(go, armorInspector, vehicleAccess)

    def onMappingLoaded(self):
        self._settingsCore.onSettingsChanged += self._clientColorSettingsChanged
        self._setSettings()

    def onMappingUnloaded(self):
        self._settingsCore.onSettingsChanged -= self._clientColorSettingsChanged

    def onAdded(self, gameObject, armorInspector, vehicleAccess):
        from gui.impl.lobby.vehicle_hub.sub_presenters.armor.config import getConfig
        vehicle = CGF.findParentWithReaction(gameObject, vehicleAccess)
        if vehicle is None:
            _logger.error('Invalid game object for ArmorInspectorComponent! Must be HangarVehicle.')
            return
        else:
            armorInspector.vehicleID = vehicle.id
            tierModel = getConfig().tierList.getTierModel(vehicle.typeDescriptor.level)
            _logger.debug('Showing Armor inspector for entityID: %s', vehicle.id)
            self._show(vehicle, gameObject, tierModel, armorInspector.showProbability, True)
            self._registerAttachmentsUpdates(vehicle, armorInspector, gameObject, tierModel)
            return

    def _show(self, vehicle, gameObject, tierModel, showProbability, withFade):
        if self._showImpl(vehicle, gameObject, tierModel, showProbability, withFade):
            self._pendingShow = None
            return
        else:
            wasPending = self._pendingShow is not None
            self._pendingShow = _PendingShow(vehicle.id, gameObject, tierModel, showProbability, withFade)
            if not wasPending:
                self._retryPending()
            return

    def _showImpl(self, vehicle, gameObject, tierModel, showProbability, withFade):
        from gui.impl.lobby.vehicle_hub.sub_presenters.armor.utils import getAllMatInfos
        return armor_inspector.show(self.spaceID, vehicle.id, gameObject, getAllMatInfos(vehicle), (tierModel.normalArmor.min, tierModel.normalArmor.max), (tierModel.spacedArmor.min, tierModel.spacedArmor.max), showProbability, withFade)

    @nextTick
    def _retryPending(self):
        pending = self._pendingShow
        if pending is None:
            return
        else:
            vehicle = BigWorld.entities.get(pending.vehicleID)
            if vehicle is None:
                self._pendingShow = None
                return
            if self._showImpl(vehicle, pending.gameObject, pending.tierModel, pending.showProbability, pending.withFade):
                self._pendingShow = None
                return
            self._retryPending()
            return

    def onRemoved(self, gameObject, component):
        if component.vehicleID is None:
            return
        else:
            _logger.debug('Hiding Armor inspector for entityID: %s', component.vehicleID)
            self._pendingShow = None
            self._unregisterAttachmentsUpdates(gameObject)
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

    def _registerAttachmentsUpdates(self, vehicle, armorInspector, gameObject, tierModel):
        if vehicle is None:
            return
        else:
            showProbability = armorInspector.showProbability

            def _onAttachmentsUpdated():
                self._show(vehicle, gameObject, tierModel, showProbability, False)

            appearance = vehicle.appearance
            appearance.onAttachmentsUpdated += _onAttachmentsUpdated
            self._appearanceListeners[gameObject] = (appearance, _onAttachmentsUpdated)
            return

    def _unregisterAttachmentsUpdates(self, gameObject):
        listener = self._appearanceListeners.pop(gameObject, None)
        if listener is None:
            return
        else:
            appearance, callback = listener
            appearance.onAttachmentsUpdated -= callback
            return
