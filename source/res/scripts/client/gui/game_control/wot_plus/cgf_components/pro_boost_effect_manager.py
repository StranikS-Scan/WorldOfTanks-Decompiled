# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/wot_plus/cgf_components/pro_boost_effect_manager.py
from helpers.CallbackDelayer import CallbackDelayer
from typing import TYPE_CHECKING, Optional, Callable, Dict
import BigWorld
import CGF
import Math
from CurrentVehicle import g_currentPreviewVehicle, g_currentVehicle
from cgf_script.managers_registrator import Rule, registerManager, registerRule
from frameworks.wulf import WindowStatus
from gui.game_control.wot_plus.utils import ProBoostUtils
from gui.lobby_state_machine.states import isInHangarState
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from helpers import dependency
from renewable_subscription_common.settings_constants import PRO_BOOST_PDATA_KEY, PRO_BOOSTED_VEHICLE
from skeletons.gui.game_control import IWotPlusController
from skeletons.gui.impl import IGuiLoader
if TYPE_CHECKING:
    from gui.game_control.wot_plus_controller import WotPlusController
    from gui.impl.gui_loader import GuiLoader
_ACTIVATION_TIMEOUT = 0.5
_ACTIVATION_PREFAB = 'content/CGFPrefabs/Lobby/proboost_activation.prefab'
_DEACTIVATION_PREFAB = 'content/CGFPrefabs/Lobby/proboost_deactivation.prefab'

class WotPlusProBoostManager(CGF.ComponentManager):
    _wotPlusCtrl = dependency.descriptor(IWotPlusController)
    _uiLoader = dependency.descriptor(IGuiLoader)

    def __init__(self, *args):
        super(WotPlusProBoostManager, self).__init__(*args)
        self._boostedVehicleInvID = self._wotPlusCtrl.getProBoostedVehicleInvID()
        self._delayer = CallbackDelayer()
        self._activationEffectGO = None
        self._deactivationEffectGO = None
        self._windowsManager = self._uiLoader.windowsManager
        return

    def activate(self):
        self._wotPlusCtrl.onDataChanged += self._onControllerDataChanged
        g_currentVehicle.onChanged += self._activateEffect
        g_currentVehicle.onChangeStarted += self._deactivateEffect
        g_eventBus.addListener(events.PrebattleEvent.SWITCHED, self._onPrbSwitch, scope=EVENT_BUS_SCOPE.LOBBY)
        self._windowsManager.onWindowStatusChanged += self._onWindowStatusChanged
        if not g_currentPreviewVehicle.vehicleEntityID and self._wotPlusCtrl.hasSubscription():
            self._delayer.delayCallback(_ACTIVATION_TIMEOUT, self._activateEffect)

    def deactivate(self):
        self._wotPlusCtrl.onDataChanged -= self._onControllerDataChanged
        g_currentVehicle.onChanged -= self._activateEffect
        g_currentVehicle.onChangeStarted -= self._deactivateEffect
        g_eventBus.removeListener(events.PrebattleEvent.SWITCHED, self._onPrbSwitch, scope=EVENT_BUS_SCOPE.LOBBY)
        self._windowsManager.onWindowStatusChanged -= self._onWindowStatusChanged
        if self._activationEffectGO:
            CGF.removeGameObject(self._activationEffectGO)
        if self._deactivationEffectGO:
            CGF.removeGameObject(self._deactivationEffectGO)
        self._activationEffectGO = None
        self._deactivationEffectGO = None
        self._windowsManager = None
        self._delayer.destroy()
        return

    @property
    def isCurrentVehicleAvailableAndBoosted(self):
        return g_currentPreviewVehicle.vehicleEntityID and self._boostedVehicleInvID and g_currentVehicle.isInHangar() and g_currentVehicle.invID == self._boostedVehicleInvID

    def _loadProBoostActivationEffect(self):
        self._loadPrefabWithCallback(_ACTIVATION_PREFAB, self._onActivationPrefabLoaded)

    def _loadProBoostDeactivationEffect(self):
        self._loadPrefabWithCallback(_DEACTIVATION_PREFAB, self._onDeactivationPrefabLoaded)

    def _loadPrefabWithCallback(self, prefab, callback):
        CGF.loadGameObjectIntoHierarchy(prefab, BigWorld.entity(g_currentPreviewVehicle.vehicleEntityID).entityGameObject, Math.Vector3(), callback)

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

    def _onActivationPrefabLoaded(self, prefabGO):
        self._activationEffectGO = prefabGO

    def _onDeactivationPrefabLoaded(self, prefabGO):
        self._deactivationEffectGO = prefabGO

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


@registerRule
class WotPlusProBoostRule(Rule):
    category = 'Hangar rules'
    domain = CGF.DomainOption.DomainClient

    @registerManager(WotPlusProBoostManager)
    def wotPlusProBoostManager(self):
        return None
