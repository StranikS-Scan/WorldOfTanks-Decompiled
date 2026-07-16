# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/wot_plus/cgf_components/pro_boost_effect_manager.py
from __future__ import absolute_import
import logging
from helpers.CallbackDelayer import CallbackDelayer
from typing import TYPE_CHECKING, Optional, Callable, Dict, List
import BigWorld
import CGF
import Math
from CurrentVehicle import g_currentPreviewVehicle, g_currentVehicle
from frameworks.wulf import WindowStatus
from gui.game_control.wot_plus.utils import ProBoostUtils
from gui.lobby_state_machine.states import isInHangarState
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from helpers import dependency
from renewable_subscription_common.settings_constants import PRO_BOOST_PDATA_KEY, PRO_BOOSTED_VEHICLE
from skeletons.gui.game_control import IWotPlusController
from skeletons.gui.impl import IGuiLoader
from cgf_script.registration import registerModule
if TYPE_CHECKING:
    from gui.game_control.wot_plus_controller import WotPlusController
    from gui.impl.gui_loader import GuiLoader
_ACTIVATION_TIMEOUT = 0.5
_ACTIVATION_PREFAB = 'content/CGFPrefabs/Lobby/proboost_activation.prefab'
_DEACTIVATION_PREFAB = 'content/CGFPrefabs/Lobby/proboost_deactivation.prefab'
_logger = logging.getLogger(__name__)

class WotPlusProBoostSystem(CGF.System):
    _wotPlusCtrl = dependency.descriptor(IWotPlusController)
    _uiLoader = dependency.descriptor(IGuiLoader)
    Reactions = CGF.Reactions()

    def __init__(self):
        super(WotPlusProBoostSystem, self).__init__()
        self._boostedVehicleInvID = self._wotPlusCtrl.getProBoostedVehicleInvID()
        self._delayer = CallbackDelayer()
        self._activationEffectGO = None
        self._deactivationEffectGO = None
        self._windowsManager = self._uiLoader.windowsManager
        self._loadingInProgressMap = {}
        return

    def onMappingLoaded(self):
        self._wotPlusCtrl.onDataChanged += self._onControllerDataChanged
        g_currentVehicle.onChanged += self._activateEffect
        g_currentVehicle.onChangeStarted += self._deactivateEffect
        g_eventBus.addListener(events.PrebattleEvent.SWITCHED, self._onPrbSwitch, scope=EVENT_BUS_SCOPE.LOBBY)
        self._windowsManager.onWindowStatusChanged += self._onWindowStatusChanged
        if not g_currentPreviewVehicle.vehicleEntityID and self._wotPlusCtrl.hasSubscription():
            self._delayer.delayCallback(_ACTIVATION_TIMEOUT, self._activateEffect)

    def onMappingUnloaded(self):
        self._wotPlusCtrl.onDataChanged -= self._onControllerDataChanged
        g_currentVehicle.onChanged -= self._activateEffect
        g_currentVehicle.onChangeStarted -= self._deactivateEffect
        g_eventBus.removeListener(events.PrebattleEvent.SWITCHED, self._onPrbSwitch, scope=EVENT_BUS_SCOPE.LOBBY)
        self._windowsManager.onWindowStatusChanged -= self._onWindowStatusChanged
        queue = CGF.CommandQueue(self.spaceID)
        if self._activationEffectGO:
            queue.removeGameObject(self._activationEffectGO)
        if self._deactivationEffectGO:
            queue.removeGameObject(self._deactivationEffectGO)
        self._activationEffectGO = None
        self._deactivationEffectGO = None
        self._windowsManager = None
        self._delayer.destroy()
        return

    @property
    def isCurrentVehicleAvailableAndBoosted(self):
        return g_currentPreviewVehicle.vehicleEntityID and self._boostedVehicleInvID and g_currentVehicle.isInHangar() and g_currentVehicle.invID == self._boostedVehicleInvID

    def _loadProBoostActivationEffect(self):
        if self._loadingInProgressMap.get(_ACTIVATION_PREFAB, False):
            _logger.debug('Proboost activation effect is already loading')
            return
        self._loadingInProgressMap[_ACTIVATION_PREFAB] = True
        self._loadPrefabWithCallback(_ACTIVATION_PREFAB, self._onActivationPrefabLoaded)

    def _loadProBoostDeactivationEffect(self):
        if self._loadingInProgressMap.get(_DEACTIVATION_PREFAB, False):
            _logger.debug('Proboost deactivation effect is already loading')
            return
        self._loadingInProgressMap[_DEACTIVATION_PREFAB] = True
        self._loadPrefabWithCallback(_DEACTIVATION_PREFAB, self._onDeactivationPrefabLoaded)

    def _loadPrefabWithCallback(self, prefab, callback):
        CGF.loadAndCreatePrefabWithParent(prefab, BigWorld.entity(g_currentPreviewVehicle.vehicleEntityID).entityGameObject, Math.Vector3(), callback)

    def _onControllerDataChanged(self, diff):
        proBoostDiff = diff.get(PRO_BOOST_PDATA_KEY, None)
        if proBoostDiff and PRO_BOOSTED_VEHICLE in proBoostDiff:
            newBoostedVehicle = proBoostDiff[PRO_BOOSTED_VEHICLE]
            if self._boostedVehicleInvID and not newBoostedVehicle:
                self._deactivateEffect()
                self._boostedVehicleInvID = None
                return
            self._boostedVehicleInvID = newBoostedVehicle
            self._activateEffect()
        return

    def _activateEffect(self):
        if not isInHangarState() or not ProBoostUtils.isGameModeCompatibleForProBoost():
            return
        self.__toggleEffects(self._activationEffectGO, self._deactivationEffectGO, self._loadProBoostActivationEffect)

    def _deactivateEffect(self):
        self.__toggleEffects(self._deactivationEffectGO, self._activationEffectGO, self._loadProBoostDeactivationEffect)

    def __toggleEffects(self, prefabToActivate, prefabToDeactivate, loadingMethod):
        if not self.isCurrentVehicleAvailableAndBoosted:
            return
        if not prefabToActivate:
            loadingMethod()
        else:
            prefabToActivate.activate()
        if prefabToDeactivate:
            prefabToDeactivate.deactivate()

    def _onActivationPrefabLoaded(self, objects, queue):
        self._activationEffectGO = queue.gameObject(objects[0])
        self._loadingInProgressMap[_ACTIVATION_PREFAB] = False

    def _onDeactivationPrefabLoaded(self, objects, queue):
        self._deactivationEffectGO = queue.gameObject(objects[0])
        self._loadingInProgressMap[_DEACTIVATION_PREFAB] = False

    def _onWindowStatusChanged(self, _, status):
        if not self.isCurrentVehicleAvailableAndBoosted:
            return
        if status == WindowStatus.DESTROYED and isInHangarState():
            self._activateEffect()
        elif status == WindowStatus.LOADED and not isInHangarState():
            self._deactivateEffect()

    def _onPrbSwitch(self, _):
        if not self.isCurrentVehicleAvailableAndBoosted:
            return
        if not ProBoostUtils.isGameModeCompatibleForProBoost():
            self._deactivateEffect()
        else:
            self._activateEffect()


@registerModule
class WotPlusProBoostModule(object):
    name = 'WoT plus boost'
    group = 'Hangar'
    systems = [CGF.RegisterSystem(WotPlusProBoostSystem, domain=CGF.Domain.Client)]
