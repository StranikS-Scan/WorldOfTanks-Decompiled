# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/battle_control/controllers/equipments_items.py
import math
import typing
from functools import partial
import BigWorld
import CGF
import Math
import SoundGroups
from AvatarInputHandler import MapCaseMode
from SMReconAbilityEntityComponent import SMReconAbilityEntityComponent
from aih_constants import CTRL_MODE_NAME
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.genConsts.ANIMATION_TYPES import ANIMATION_TYPES
from gui.battle_control import avatar_getter
from gui.battle_control.controllers.consumables import equipment_ctrl
from gui.shared.system_factory import registerEquipmentItem
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from story_mode.avatar_input_handler.control_modes import StoryModeArcadeMinefieldControlMode, SMStrategicMapCaseControlMode
from story_mode.gui.story_mode_gui_constants import ABILITY_ON_COOLDOWN_ACTIVATION_ERROR_KEY
from story_mode.gui.sound_constants import SMN_ARCADE_ARTILLERY_ACTIVATE_SOUND, SMN_ARCADE_ARTILLERY_DEACTIVATE_SOUND, SMN_ARCADE_ARTILLERY_SET_SOUND, SMN_ARCADE_ARTILLERY_STATE_GROUP, SMN_ARCADE_ARTILLERY_STATE_IN, SMN_ARCADE_ARTILLERY_STATE_OUT, SMN_ARCADE_ARTILLERY_DESTROYER_SOUND, DISTRACTION_ABILITY_ACTIVATE_SOUND, DISTRACTION_ABILITY_CANCEL_SOUND, DISTRACTION_ABILITY_SET_SOUND, RECON_ABILITY_ACTIVATE_SOUND, RECON_ABILITY_DEACTIVATE_SOUND, RECON_ABILITY_CANCEL_SOUND, RECON_ABILITY_SET_SOUND, RECON_ABILITY_ENGINE_STOP_SOUND, RECON_ABILITY_ENGINE_START_SOUND
from story_mode_common.story_mode_constants import RECON_ABILITY, EQUIPMENT_STAGES as STAGES, DISTRACTION_ABILITY, SCC_AIRSTRIKE_ABILITY, SCC_AIRSTRIKE_ABILITY_HARD
if typing.TYPE_CHECKING:
    from Avatar import Avatar
    from items import artefacts
_SMN_ARCADE_ARTILLERY_ITEMS = ('arcade_artillery_smn_battleship_lvl1', 'arcade_artillery_smn_battleship_lvl1_hard', 'arcade_artillery_smn_battleship_lvl2', 'arcade_artillery_smn_battleship_lvl2_hard', 'arcade_artillery_smn_battleship_lvl3', 'arcade_artillery_smn_battleship_lvl3_hard')
_SMN_ARCADE_ARTILLERY_DESTROYER_ITEMS = {'arcade_artillery_smn_destroyer', 'arcade_artillery_smn_destroyer_hard'}
_EQUIPMENT_STAGE_DESTROYER_SHOOTING = -1

class _SmnRefillEquipmentItem(equipment_ctrl._RefillEquipmentItem):

    def __init__(self, *args, **kwargs):
        self._mapCaseModeActive = False
        super(_SmnRefillEquipmentItem, self).__init__(*args, **kwargs)

    def getAimingControlMode(self):
        return StoryModeArcadeMinefieldControlMode

    def update(self, quantity, stage, timeRemaining, totalTime):
        super(_SmnRefillEquipmentItem, self).update(quantity, stage, timeRemaining, totalTime)
        if self._mapCaseModeActive:
            if stage == STAGES.COOLDOWN:
                SoundGroups.g_instance.playSound2D(SMN_ARCADE_ARTILLERY_SET_SOUND)
            SoundGroups.g_instance.playSound2D(SMN_ARCADE_ARTILLERY_DEACTIVATE_SOUND)
            SoundGroups.g_instance.setState(SMN_ARCADE_ARTILLERY_STATE_GROUP, SMN_ARCADE_ARTILLERY_STATE_OUT)
            self._mapCaseModeActive = False
        elif stage == STAGES.PREPARING:
            SoundGroups.g_instance.playSound2D(SMN_ARCADE_ARTILLERY_ACTIVATE_SOUND)
            SoundGroups.g_instance.setState(SMN_ARCADE_ARTILLERY_STATE_GROUP, SMN_ARCADE_ARTILLERY_STATE_IN)
            self._mapCaseModeActive = True


class _SmnArcadeArtilleryItem(_SmnRefillEquipmentItem, equipment_ctrl._ArcadeArtilleryItem):
    pass


class _SmnReplayArcadeArtilleryItem(_SmnRefillEquipmentItem, equipment_ctrl._ReplayArcadeArtilleryItem):
    pass


class _SmnArcadeArtilleryBaseItem(object):

    def update(self, quantity, stage, timeRemaining, totalTime):
        super(_SmnArcadeArtilleryBaseItem, self).update(quantity, stage, timeRemaining, totalTime)
        if stage == _EQUIPMENT_STAGE_DESTROYER_SHOOTING:
            SoundGroups.g_instance.playSound2D(SMN_ARCADE_ARTILLERY_DESTROYER_SOUND)


class _SmnArcadeArtilleryDestroyerItem(_SmnArcadeArtilleryBaseItem, equipment_ctrl._ArcadeArtilleryItem):
    pass


class _SmnReplayArcadeArtilleryDestroyerItem(_SmnArcadeArtilleryBaseItem, equipment_ctrl._ReplayArcadeArtilleryItem):
    pass


class AbilityItem(equipment_ctrl._RefillEquipmentItem, equipment_ctrl._OrderItem):

    def __init__(self, *args, **kwargs):
        self._abilityUseInProgress = False
        super(AbilityItem, self).__init__(*args, **kwargs)

    def canActivate(self, entityName=None, avatar=None):
        if self._stage in [STAGES.STARTUP_COOLDOWN, STAGES.COOLDOWN] and self._timeRemaining > 0:
            error = equipment_ctrl._ActivationError(ABILITY_ON_COOLDOWN_ACTIVATION_ERROR_KEY, {'name': self.getDescriptor().userString})
            return (False, error)
        return super(AbilityItem, self).canActivate(entityName, avatar)

    def getTimeRemaining(self):
        return min(math.ceil(self._timeRemaining), self._totalTime) if self._timeRemaining else self._timeRemaining

    def getAimingControlMode(self):
        return StoryModeArcadeMinefieldControlMode

    def _playSoundAndChangeState(self, sound, final):
        SoundGroups.g_instance.playSound2D(sound)
        newState = SMN_ARCADE_ARTILLERY_STATE_OUT if final else SMN_ARCADE_ARTILLERY_STATE_IN
        SoundGroups.g_instance.setState(SMN_ARCADE_ARTILLERY_STATE_GROUP, newState)
        self._abilityUseInProgress = not final


class SMStrategicAbilityItem(AbilityItem):
    _PREFAB_URL = ''

    def __init__(self, descriptor, quantity, stage, timeRemaining, totalTime, tags):
        super(SMStrategicAbilityItem, self).__init__(descriptor, quantity, stage, timeRemaining, totalTime, tags)
        self._prefab = None
        self._isSelecting = False
        return

    def getAimingControlMode(self):
        return SMStrategicMapCaseControlMode

    def updateMapCase(self, stage=None):
        if (not BigWorld.player().isObserver() or BigWorld.player().isObserverFPV) and self._stage != stage and self._stage != STAGES.NOT_RUNNING:
            self._updateVisual(stage or self._stage)
            if stage == STAGES.PREPARING:
                self._cancelPreviousMode()
        super(SMStrategicAbilityItem, self).updateMapCase(stage)

    def _cancelPreviousMode(self):
        inputHandler = BigWorld.player().inputHandler
        if isinstance(inputHandler.ctrl, self.getAimingControlMode()):
            inputHandler.ctrl.turnOff()

    def clear(self):
        self._removePrefab()
        super(SMStrategicAbilityItem, self).clear()

    def _updateVisual(self, stage):
        if stage == STAGES.PREPARING and self._PREFAB_URL:
            self._loadPrefab()
        elif stage in (STAGES.READY, STAGES.DEACTIVATING, STAGES.COOLDOWN):
            self._removePrefab()

    def _loadPrefab(self):
        self._isSelecting = True
        CGF.loadGameObjectIntoHierarchy(self._PREFAB_URL, BigWorld.player().vehicle.entityGameObject, Math.Vector3(), self._onPrefabLoaded)

    def _onPrefabLoaded(self, prefab):
        if self._isSelecting:
            self._prefab = prefab
            self._prefab.activate()
        else:
            CGF.removeGameObject(prefab)

    def _removePrefab(self):
        if self._prefab is not None:
            CGF.removeGameObject(self._prefab)
            self._prefab = None
        self._isSelecting = False
        return


class DistractionAbilityItem(SMStrategicAbilityItem):
    _PREFAB_URL = 'content/CGFPrefabs/Storymode/tank_rectangle.prefab'

    def update(self, quantity, stage, timeRemaining, totalTime):
        super(DistractionAbilityItem, self).update(quantity, stage, timeRemaining, totalTime)
        if stage == STAGES.PREPARING:
            self._playSoundAndChangeState(DISTRACTION_ABILITY_ACTIVATE_SOUND, False)
        elif stage == STAGES.READY and self._abilityUseInProgress:
            self._playSoundAndChangeState(DISTRACTION_ABILITY_CANCEL_SOUND, True)
        elif stage == STAGES.COOLDOWN and self._abilityUseInProgress:
            self._playSoundAndChangeState(DISTRACTION_ABILITY_SET_SOUND, True)


class ReconAbilityItem(SMStrategicAbilityItem):
    _PREFAB_URL = 'content/CGFPrefabs/Storymode/tank_rectangle.prefab'
    appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, *args, **kwargs):
        super(ReconAbilityItem, self).__init__(*args, **kwargs)
        SMReconAbilityEntityComponent.onSMReconEntityCreated += self._onSMReconEntityCreated
        self._isEntityViewModeActive = False

    def clear(self):
        SMReconAbilityEntityComponent.onSMReconEntityCreated -= self._onSMReconEntityCreated
        if self._abilityUseInProgress:
            self._playSoundAndChangeState(RECON_ABILITY_DEACTIVATE_SOUND, True)
        super(ReconAbilityItem, self).clear()

    def isInCooldown(self):
        return self._stage in (STAGES.ACTIVATING, STAGES.COOLDOWN, STAGES.DEACTIVATING)

    def isInPreparing(self):
        return super(ReconAbilityItem, self).isInPreparing() or self.getStage() == STAGES.ACTIVE

    def canDeactivate(self):
        battleApp = self.appLoader.getDefBattleApp()
        return False if bool(battleApp.containerManager.getViewByKey(ViewKey(VIEW_ALIAS.INGAME_MENU))) or bool(battleApp.containerManager.getViewByKey(ViewKey(VIEW_ALIAS.INGAME_HELP))) else super(ReconAbilityItem, self).canDeactivate()

    @property
    def becomeReady(self):
        return super(ReconAbilityItem, self).becomeReady or self.isReady and self._serverPrevStage in [STAGES.ACTIVATING, STAGES.ACTIVE, STAGES.DEACTIVATING]

    def getAnimationType(self):
        if self._stage == STAGES.COOLDOWN:
            return ANIMATION_TYPES.MOVE_ORANGE_BAR_UP | ANIMATION_TYPES.SHOW_COUNTER_ORANGE
        return ANIMATION_TYPES.MOVE_GREEN_BAR_UP | ANIMATION_TYPES.TIMER_INVISIBLE if self._stage in (STAGES.ACTIVATING, STAGES.DEACTIVATING) else super(ReconAbilityItem, self).getAnimationType()

    def updateMapCase(self, stage=None):
        if not BigWorld.player().isObserver() or BigWorld.player().isObserverFPV:
            if self._stage == stage or self._stage == STAGES.NOT_RUNNING:
                return
            if stage is None:
                stage = self._stage
            self._updateVisual(stage)
            newStage, prevStage = stage, self._stage
            if newStage == STAGES.PREPARING:
                self._cancelPreviousMode()
                self._activateMapCase()
            elif newStage == STAGES.READY and prevStage == STAGES.PREPARING:
                self._turnOffMapCase()
            elif newStage in [STAGES.COOLDOWN, STAGES.READY] and self._isEntityViewModeActive:
                self._changeControlMode(CTRL_MODE_NAME.ARCADE)
                self._isEntityViewModeActive = False
        return

    def update(self, quantity, stage, timeRemaining, totalTime):
        super(ReconAbilityItem, self).update(quantity, stage, timeRemaining, totalTime)
        if stage == STAGES.PREPARING:
            self._playSoundAndChangeState(RECON_ABILITY_ACTIVATE_SOUND, False)
        elif stage == STAGES.ACTIVATING:
            SoundGroups.g_instance.playSound2D(RECON_ABILITY_SET_SOUND)
            SoundGroups.g_instance.playSound2D(RECON_ABILITY_ENGINE_STOP_SOUND)
        elif stage == STAGES.DEACTIVATING:
            SoundGroups.g_instance.playSound2D(RECON_ABILITY_DEACTIVATE_SOUND)
            SoundGroups.g_instance.playSound2D(RECON_ABILITY_ENGINE_START_SOUND)
        elif stage == STAGES.COOLDOWN and self._abilityUseInProgress:
            SoundGroups.g_instance.setState(SMN_ARCADE_ARTILLERY_STATE_GROUP, SMN_ARCADE_ARTILLERY_STATE_OUT)
            self._abilityUseInProgress = False
        elif stage == STAGES.READY and self._abilityUseInProgress:
            self._playSoundAndChangeState(RECON_ABILITY_CANCEL_SOUND, True)

    def _onSMReconEntityCreated(self, entityId):
        self._turnOffMapCase()
        self._changeControlMode(CTRL_MODE_NAME.SM_ENTITY_VIEW, entityId=entityId)
        self._isEntityViewModeActive = True

    def _activateMapCase(self):
        MapCaseMode.activateMapCase(self.getEquipmentID(), partial(self.deactivate), self.getAimingControlMode())

    def _turnOffMapCase(self):
        MapCaseMode.turnOffMapCase(self.getEquipmentID(), self.getAimingControlMode())

    @staticmethod
    def _changeControlMode(mode, **kwargs):
        inputHandler = avatar_getter.getInputHandler()
        if inputHandler is not None:
            inputHandler.onControlModeChanged(mode, **kwargs)
        return


class AbilityReplayItem(equipment_ctrl._ReplayOrderItem):

    def getAimingControlMode(self):
        return StoryModeArcadeMinefieldControlMode


class SccAirstrikeAbilityItem(SMStrategicAbilityItem, _SmnRefillEquipmentItem):
    pass


class SccReplayAirstrikeAbilityItem(_SmnRefillEquipmentItem, equipment_ctrl._ReplayOrderItem):
    pass


def register():
    for name in _SMN_ARCADE_ARTILLERY_ITEMS:
        registerEquipmentItem(name, _SmnArcadeArtilleryItem, _SmnReplayArcadeArtilleryItem)

    for name in _SMN_ARCADE_ARTILLERY_DESTROYER_ITEMS:
        registerEquipmentItem(name, _SmnArcadeArtilleryDestroyerItem, _SmnReplayArcadeArtilleryDestroyerItem)

    registerEquipmentItem(RECON_ABILITY, ReconAbilityItem, AbilityReplayItem)
    registerEquipmentItem(DISTRACTION_ABILITY, DistractionAbilityItem, AbilityReplayItem)
    registerEquipmentItem(SCC_AIRSTRIKE_ABILITY, SccAirstrikeAbilityItem, SccReplayAirstrikeAbilityItem)
    registerEquipmentItem(SCC_AIRSTRIKE_ABILITY_HARD, SccAirstrikeAbilityItem, SccReplayAirstrikeAbilityItem)
