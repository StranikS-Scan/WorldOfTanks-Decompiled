# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/HWArenaPhasesComponent.py
from __future__ import absolute_import
import BigWorld
from helpers import isPlayerAvatar
from script_component.DynamicScriptComponent import DynamicScriptComponent
import Event
import logging
from helpers.CallbackDelayer import CallbackDelayer
from helpers.EffectsList import effectsFromSection, EffectsListPlayer
from helpers import newFakeModel, dependency
from halloween_dyn_object_cache import HWEffects, getEffectSection
from halloween_common.halloween_constants import INVALID_PHASE
from halloween.gui.halloween_gui_constants import BATTLE_CTRL_ID
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)

class HWEnvironmentSwitcher(object):

    def __init__(self, spaceID):
        self._isSwitchInProcess = False
        self._callbackDelayer = CallbackDelayer()
        self._fakeModel = None
        self._effectsPlayer = None
        self._spaceID = spaceID
        section = getEffectSection(HWEffects.PHASE_SWITCH)
        self._effects = effectsFromSection(section)
        self._envSwitchDelay = section['envSwitchDelay'].asFloat
        return

    def onDestroy(self):
        self._effects = None
        self._callbackDelayer.destroy()
        self._cancelOngoingSwitcher()
        return

    def setupEnvironment(self, envName, isInstantSwitch=False):
        self._cancelOngoingSwitcher()
        if isInstantSwitch or self._effects is None:
            self._switchEnvironment(envName)
            return
        else:
            self._fakeModel = newFakeModel()
            BigWorld.player().addModel(self._fakeModel)
            self._effectsPlayer = EffectsListPlayer(self._effects.effectsList, self._effects.keyPoints, debugParent=self)
            self._effectsPlayer.play(self._fakeModel, callbackFunc=self._cancelOngoingSwitcher)
            self._callbackDelayer.delayCallback(self._envSwitchDelay, self._switchEnvironment, envName)
            return

    def _cancelOngoingSwitcher(self):
        self._callbackDelayer.clearCallbacks()
        if self._effectsPlayer:
            self._effectsPlayer.stop()
            self._effectsPlayer = None
        if self._fakeModel:
            BigWorld.player().delModel(self._fakeModel)
            self._fakeModel = None
        return

    def _switchEnvironment(self, envName):
        BigWorld.spaces[self._spaceID].setEnvironment(envName)


class HWArenaPhasesComponent(DynamicScriptComponent):
    onPhaseChanged = Event.Event()
    onPhaseModifierChanged = Event.Event()
    onPhaseTimeChanged = Event.Event()
    onHideVehicleOnMinimap = Event.Event()
    onBossVulnerableChanged = Event.Event()
    onMinimapAutoZoomChanged = Event.Event()
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(HWArenaPhasesComponent, self).__init__()
        self.envSwitcher = None
        return

    def onDestroy(self):
        if self.envSwitcher:
            self.envSwitcher.onDestroy()
            self.envSwitcher = None
        self.onPhaseChanged.clear()
        self.onPhaseTimeChanged.clear()
        self.onPhaseModifierChanged.clear()
        player = BigWorld.player()
        if player:
            player.onAvatarVehicleChanged -= self._onAvatarVehicleChanged
        super(HWArenaPhasesComponent, self).onDestroy()
        return

    def _onAvatarReady(self):
        self.onPhaseModifierChanged(self)
        if self.phasesCount:
            self.onPhaseChanged(self)
            lastPhase = self.activePhase == self.phasesCount
            self.onPhaseTimeChanged(self.timeLeft, self.timeLeft, lastPhase)
        player = BigWorld.player()
        if player:
            player.onAvatarVehicleChanged += self._onAvatarVehicleChanged
        self.envSwitcher = HWEnvironmentSwitcher(self.entity.spaceID)
        self._setupEnvironment(True)

    @property
    def hwBattleGuiCtrl(self):
        return self.guiSessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.HW_BATTLE_GUI_CTRL)

    def set_activePhase(self, prev):
        _logger.info('HWArenaPhasesComponent set activePhase=%s', self.activePhase)
        self.onPhaseChanged(self)

    def set_modifierName(self, prev):
        _logger.info('HWArenaPhasesComponent set modifierName=%s', self.modifierName)
        self.onPhaseModifierChanged(self)

    def set_modifierColor(self, prev):
        _logger.info('HWArenaPhasesComponent set modifierColor=%s', self.modifierColor)
        self.onPhaseModifierChanged(self)

    def set_timeLeft(self, prev):
        lastPhase = self.activePhase == self.phasesCount
        self.onPhaseTimeChanged(self.timeLeft, prev, lastPhase)

    def set_activeEnvironment(self, prev):
        if not self._isAvatarReady:
            return
        self._setupEnvironment()

    def set_isBossVulnerable(self, prev):
        self.onBossVulnerableChanged(self.isBossVulnerable)

    def set_minimapAutoZoom(self, prev):
        self.onMinimapAutoZoomChanged(self.minimapAutoZoom)

    def _setupEnvironment(self, isInstant=False):
        if self.envSwitcher is None or not self.activeEnvironment:
            return
        else:
            self.envSwitcher.setupEnvironment(self.activeEnvironment, isInstant)
            return

    def hideVehicleOnMinimap(self, vehicleID):
        self.onHideVehicleOnMinimap(vehicleID)

    def notifyPhaseTimeChanged(self, looterID, ownerID, amount):
        hwBattleGuiCtrl = self.hwBattleGuiCtrl
        if hwBattleGuiCtrl:
            hwBattleGuiCtrl.notifyPhaseTimeChanged(looterID, ownerID, amount)

    def isLastPhase(self):
        return self.activePhase == self.phasesCount and self.activePhase != INVALID_PHASE

    @staticmethod
    def getInstance():
        if not isPlayerAvatar():
            return None
        else:
            player = BigWorld.player()
            if not player:
                return None
            return None if not player.arena or not player.arena.arenaInfo else getattr(player.arena.arenaInfo, 'HWArenaPhasesComponent', None)

    def _onAvatarVehicleChanged(self):
        if self.phasesCount:
            lastPhase = self.activePhase == self.phasesCount
            self.onPhaseTimeChanged(self.timeLeft, self.timeLeft, lastPhase)
