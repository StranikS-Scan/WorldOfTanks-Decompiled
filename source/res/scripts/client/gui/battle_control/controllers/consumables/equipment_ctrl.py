# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/consumables/equipment_ctrl.py
import itertools
import logging
from collections import namedtuple
from functools import partial
from typing import TYPE_CHECKING
import BigWorld
import Event
import SoundGroups
from AvatarInputHandler.AimingSystems import getShotTargetInfo
from PlayerEvents import g_playerEvents
from aih_constants import CTRL_MODE_NAME
from comp7_common import ROLE_EQUIPMENT_TAG
from constants import VEHICLE_SETTING, EQUIPMENT_STAGES, ARENA_BONUS_TYPE
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.system_factory import collectEquipmentItem
from gui.Scaleform.genConsts.ANIMATION_TYPES import ANIMATION_TYPES
from gui.Scaleform.genConsts.BATTLE_MARKERS_CONSTS import BATTLE_MARKERS_CONSTS
from gui.battle_control import avatar_getter, vehicle_getter
from gui.battle_control.battle_constants import makeExtraName, VEHICLE_COMPLEX_ITEMS, BATTLE_CTRL_ID
from gui.battle_control.controllers.interfaces import IBattleController
from gui.shared.utils.MethodsRules import MethodsRules
from gui.shared.utils.decorators import ReprInjector
from gui.sounds.epic_sound_constants import EPIC_SOUND
from helpers import i18n, dependency
from items import vehicles, EQUIPMENT_TYPES, ITEM_TYPES
from points_of_interest_shared import POI_EQUIPMENT_TAG, PoiTypesByPoiEquipmentName
from shared_utils import findFirst, forEach, CONST_CONTAINER
from skeletons.gui.battle_session import IBattleSessionProvider
from soft_exception import SoftException
if TYPE_CHECKING:
    from items.artefacts import Equipment
_ActivationError = namedtuple('_ActivationError', 'key ctx')
_ROLE_EQUIPMENT_ANIMATION_TYPE = ANIMATION_TYPES.MOVE_ORANGE_BAR_UP | ANIMATION_TYPES.SHOW_COUNTER_ORANGE
_logger = logging.getLogger(__name__)

class NotApplyingError(_ActivationError):
    pass


class InCooldownError(_ActivationError):

    def __new__(cls, name):
        return super(InCooldownError, cls).__new__(cls, 'equipmentIsInCooldown', {'name': name})

    def __init__(self, name):
        super(InCooldownError, self).__init__('equipmentIsInCooldown', {'name': name})


class NotReadyError(_ActivationError):

    def __new__(cls, name):
        return super(NotReadyError, cls).__new__(cls, 'orderNotReady', {'name': name})

    def __init__(self, name):
        super(NotReadyError, self).__init__('orderNotReady', {'name': name})


class PoiUnavailableError(_ActivationError):

    @staticmethod
    def _getPoiName(equipmentName):
        poiType = PoiTypesByPoiEquipmentName.get(equipmentName)
        return backport.text(R.strings.points_of_interest.type.dyn(poiType.name.lower())())

    def __new__(cls, name):
        return super(PoiUnavailableError, cls).__new__(cls, 'equipmentPoiUnavailable', {'name': cls._getPoiName(name)})

    def __init__(self, name):
        super(PoiUnavailableError, self).__init__('equipmentPoiUnavailable', {'name': self._getPoiName(name)})


class Comp7RoleSkillUnavailable(_ActivationError):

    def __new__(cls, name):
        return super(Comp7RoleSkillUnavailable, cls).__new__(cls, 'comp7RoleSkillUnavailable', {'name': name})

    def __init__(self, name):
        super(Comp7RoleSkillUnavailable, self).__init__('comp7RoleSkillUnavailable', {'name': name})


class Comp7RoleSkillAlreadyActivated(_ActivationError):

    def __new__(cls, name):
        return super(Comp7RoleSkillAlreadyActivated, cls).__new__(cls, 'comp7RoleSkillAlreadyActivated', {'name': name})

    def __init__(self, name):
        super(Comp7RoleSkillAlreadyActivated, self).__init__('comp7RoleSkillAlreadyActivated', {'name': name})


class Comp7RoleSkillCooldown(_ActivationError):

    def __new__(cls, name):
        return super(Comp7RoleSkillCooldown, cls).__new__(cls, 'comp7RoleSkillCooldown', {'name': name})

    def __init__(self, name):
        super(Comp7RoleSkillCooldown, self).__init__('comp7RoleSkillCooldown', {'name': name})


class NeedEntitySelection(_ActivationError):
    pass


class IgnoreEntitySelection(_ActivationError):
    pass


class EquipmentSound(object):
    _soundMap = {251: 'battle_equipment_251',
     507: 'battle_equipment_507',
     1019: 'battle_equipment_1019',
     763: 'battle_equipment_763',
     1531: 'battle_equipment_1531',
     46331: 'battle_equipment_1531',
     1275: 'battle_equipment_1275'}

    @staticmethod
    def getSounds():
        return EquipmentSound._soundMap.values()

    @staticmethod
    def playSound(ID):
        soundName = EquipmentSound._soundMap.get(ID, None)
        if soundName is not None:
            SoundGroups.g_instance.playSound2D(soundName)
        return

    @staticmethod
    def playReady(item):
        equipment = vehicles.g_cache.equipments()[item.getEquipmentID()]
        if equipment is not None:
            if equipment.soundNotification is not None:
                avatar_getter.getSoundNotifications().play(equipment.soundNotification)
        return


@ReprInjector.simple(('_tags', 'tags'), ('_quantity', 'quantity'), ('_stage', 'stage'), ('_prevStage', 'prevStage'), ('_timeRemaining', 'timeRemaining'), ('_totalTime', 'totalTime'), ('_animationType', 'animationType'))
class _EquipmentItem(object):
    __slots__ = ('_tags', '_descriptor', '_quantity', '_stage', '_prevStage', '_timeRemaining', '_prevQuantity', '_totalTime', '_animationType', '_serverPrevStage', '_index')

    def __init__(self, descriptor, quantity, stage, timeRemaining, totalTime, tags):
        super(_EquipmentItem, self).__init__()
        self._tags = tags
        self._descriptor = descriptor
        self._quantity = 0
        self._stage = 0
        self._serverPrevStage = None
        self._prevStage = 0
        self._prevQuantity = 0
        self._timeRemaining = 0
        self._index = 0
        self._totalTime = totalTime
        self._animationType = ANIMATION_TYPES.MOVE_ORANGE_BAR_UP | ANIMATION_TYPES.SHOW_COUNTER_ORANGE | ANIMATION_TYPES.DARK_COLOR_TRANSFORM
        self.update(quantity, stage, timeRemaining, totalTime)
        return

    def getAnimationType(self):
        return self._animationType

    def setServerPrevStage(self, prevStage):
        self._serverPrevStage = prevStage

    def getTags(self):
        return self._tags

    def isEntityRequired(self):
        return False

    def getEntitiesIterator(self, avatar=None):
        raise SoftException('Invokes getEntitiesIterator, than it is not required')

    def getGuiIterator(self, avatar=None):
        raise SoftException('Invokes getGuiIterator, than it is not required')

    @property
    def isAvailableToUse(self):
        return self.getQuantity() > 0 and self.isReady

    def canActivate(self, entityName=None, avatar=None):
        if self._timeRemaining > 0 and self._stage and self._stage not in (EQUIPMENT_STAGES.DEPLOYING, EQUIPMENT_STAGES.COOLDOWN, EQUIPMENT_STAGES.SHARED_COOLDOWN):
            result = False
            error = _ActivationError('equipmentAlreadyActivated', {'name': self._descriptor.userString})
        elif self._stage and self._stage not in (EQUIPMENT_STAGES.READY, EQUIPMENT_STAGES.PREPARING):
            result = False
            error = None
            if self._stage == EQUIPMENT_STAGES.ACTIVE:
                error = _ActivationError('equipmentAlreadyActivated', {'name': self._descriptor.userString})
            elif self._stage == EQUIPMENT_STAGES.COOLDOWN and self._quantity:
                error = InCooldownError(self._descriptor.userString)
        elif self._quantity <= 0:
            result = False
            error = None
        else:
            result = True
            error = None
        return (result, error)

    def getActivationCode(self, entityName=None, avatar=None):
        return None

    def clear(self):
        self._descriptor = None
        self._quantity = 0
        self._prevQuantity = 0
        self._stage = 0
        self._prevStage = 0
        self._timeRemaining = 0
        self._totalTime = 0
        return

    def update(self, quantity, stage, timeRemaining, totalTime):
        self._prevQuantity = self._quantity
        self._quantity = quantity
        self._prevStage = self._stage
        self._stage = stage
        self._timeRemaining = timeRemaining
        self._totalTime = totalTime
        self._soundUpdate(self._prevQuantity, quantity)

    def updateMapCase(self, stage=None):
        pass

    def activate(self, entityName=None, avatar=None):
        if 'avatar' in self._descriptor.tags:
            index = self._index if hasattr(self, '_index') and self._index > 0 else 0
            avatar_getter.activateAvatarEquipment(self.getEquipmentID(), avatar, index)
        else:
            avatar_getter.changeVehicleSetting(VEHICLE_SETTING.ACTIVATE_EQUIPMENT, self.getActivationCode(entityName, avatar), avatar=avatar)

    def deactivate(self):
        if not self.canDeactivate() or self._descriptor is None:
            return
        else:
            index = self._index if hasattr(self, '_index') and self._index > 0 else 0
            if 'avatar' in self._descriptor.tags:
                avatar_getter.activateAvatarEquipment(self.getEquipmentID(), None, index)
            else:
                avatar_getter.changeVehicleSetting(VEHICLE_SETTING.ACTIVATE_EQUIPMENT, self.getEquipmentID())
            return

    @property
    def isReusable(self):
        return self._descriptor and self._descriptor.reuseCount != 0

    @property
    def isReady(self):
        return self._stage == EQUIPMENT_STAGES.READY

    @property
    def becomeReady(self):
        return self.isReady and self._serverPrevStage in (EQUIPMENT_STAGES.DEPLOYING,
         EQUIPMENT_STAGES.UNAVAILABLE,
         EQUIPMENT_STAGES.COOLDOWN,
         EQUIPMENT_STAGES.SHARED_COOLDOWN,
         EQUIPMENT_STAGES.EXHAUSTED,
         EQUIPMENT_STAGES.NOT_RUNNING)

    @property
    def becomeAvailable(self):
        return self.getPrevQuantity() <= 0 and self.getQuantity() > 0

    def getDescriptor(self):
        return self._descriptor

    def getQuantity(self):
        return self._quantity

    def getPrevQuantity(self):
        return self._prevQuantity

    def isQuantityUsed(self):
        return 'showQuantity' in self._descriptor.tags

    def getStage(self):
        return self._stage

    def getPrevStage(self):
        return self._prevStage

    def getTimeRemaining(self):
        return self._timeRemaining

    def isValid(self):
        return self._descriptor is not None

    @property
    def index(self):
        return self._index

    def setIndex(self, index):
        self._index = index

    def getTotalTime(self):
        return self._totalTime

    def getMarker(self):
        return self._descriptor.name.split('_')[0]

    def getEnemyMarker(self):
        return self.getMarker()

    def getMarkerColor(self):
        return BATTLE_MARKERS_CONSTS.COLOR_GREEN

    def getEnemyMarkerColor(self):
        return self.getMarkerColor()

    def getEquipmentID(self):
        _, innationID = self._descriptor.id
        return innationID

    def isAvatar(self):
        return self._descriptor and 'avatar' in self._descriptor.tags

    def _soundUpdate(self, prevQuantity, quantity):
        if prevQuantity > quantity and self._stage != self._prevStage:
            if self._stage != EQUIPMENT_STAGES.NOT_RUNNING:
                EquipmentSound.playSound(self._descriptor.compactDescr)
        if self.becomeReady:
            EquipmentSound.playReady(self)

    def canDeactivate(self):
        return True


class _RefillEquipmentItem(object):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _PRE_REFILL_TIME = 3

    def __init__(self, *args, **kwargs):
        self._preRefillCallback = None
        super(_RefillEquipmentItem, self).__init__(*args, **kwargs)
        return

    def update(self, quantity, stage, timeRemaining, totalTime):
        super(_RefillEquipmentItem, self).update(quantity, stage, timeRemaining, totalTime)
        if timeRemaining > self._PRE_REFILL_TIME:
            if self._preRefillCallback is not None:
                self.clear()
            self._preRefillCallback = BigWorld.callback(timeRemaining - self._PRE_REFILL_TIME, self._preRefill)
        if self.isReady and self._prevStage in (EQUIPMENT_STAGES.COOLDOWN, EQUIPMENT_STAGES.SHARED_COOLDOWN):
            self._refillComplete()
        return

    def clear(self):
        if self._preRefillCallback is not None:
            BigWorld.cancelCallback(self._preRefillCallback)
            self._preRefillCallback = None
        return

    def _preRefill(self):
        self._preRefillCallback = None
        SoundGroups.g_instance.playSound2D('be_pre_replenishment')
        return

    def _refillComplete(self):
        SoundGroups.g_instance.playSound2D('be_replenishment_full')


class _AutoItem(_EquipmentItem):

    def canActivate(self, entityName=None, avatar=None):
        return (False, None)


class _TriggerItem(_EquipmentItem):

    def getActivationCode(self, entityName=None, avatar=None):
        flag = 1 if self._timeRemaining == 0 else 0
        return (flag << 16) + self._descriptor.id[1]


class _ExpandedItem(_EquipmentItem):

    def isEntityRequired(self):
        return not self._descriptor.repairAll

    def canActivate(self, entityName=None, avatar=None):
        result, error = super(_ExpandedItem, self).canActivate(entityName, avatar)
        return (result, error) if not result else self._canActivate(entityName, avatar)

    def getActivationCode(self, entityName=None, avatar=None):
        if not self.isEntityRequired():
            return 65536 + self._descriptor.id[1]
        else:
            extrasDict = avatar_getter.getVehicleExtrasDict(avatar)
            if entityName is None:
                return
            extraName = makeExtraName(entityName)
            if extraName not in extrasDict:
                return
            return (extrasDict[extraName].index << 16) + self._descriptor.id[1]
            return

    def _getEntitiesAreSafeKey(self):
        pass

    def _getEntityIsSafeKey(self):
        pass

    def _getEntityUserString(self, entityName, avatar=None):
        extrasDict = avatar_getter.getVehicleExtrasDict(avatar)
        extraName = makeExtraName(entityName)
        if extraName in extrasDict:
            userString = extrasDict[extraName].deviceUserString
        else:
            userString = entityName
        return userString

    def _canActivate(self, entityName=None, avatar=None):
        deviceStates = avatar_getter.getVehicleDeviceStates(avatar)
        if not deviceStates:
            return (False, _ActivationError(self._getEntitiesAreSafeKey(), None))
        elif entityName is None:
            for item in self.getEntitiesIterator():
                if item[0] in deviceStates:
                    isEntityNotRequired = not self.isEntityRequired()
                    return (isEntityNotRequired, None if isEntityNotRequired else NeedEntitySelection('', None))

            return (False, _ActivationError(self._getEntitiesAreSafeKey(), None))
        else:
            return self._canApplyForEntity(entityName, deviceStates)

    def _canApplyForEntity(self, entityName, deviceStates):
        return (False, NotApplyingError(self._getEntityIsSafeKey(), {'entity': self._getEntityUserString(entityName)})) if entityName not in deviceStates else (True, None)


class _ExtinguisherItem(_RefillEquipmentItem, _EquipmentItem):

    def canActivate(self, entityName=None, avatar=None):
        result, error = super(_ExtinguisherItem, self).canActivate(entityName, avatar)
        if not result:
            return (result, error)
        else:
            return (False, _ActivationError('extinguisherDoesNotActivated', {'name': self._descriptor.userString})) if not avatar_getter.isVehicleInFire(avatar) else (True, None)

    def getActivationCode(self, entityName=None, avatar=None):
        return 65536 + self._descriptor.id[1]


class _MedKitItem(_RefillEquipmentItem, _ExpandedItem):

    def getActivationCode(self, entityName=None, avatar=None):
        activationCode = super(_MedKitItem, self).getActivationCode(entityName, avatar)
        if activationCode is None and avatar_getter.isVehicleStunned() and self.isReusable:
            extrasDict = avatar_getter.getVehicleExtrasDict(avatar)
            activationCode = (extrasDict[makeExtraName('commander')].index << 16) + self._descriptor.id[1]
        return activationCode

    def getEntitiesIterator(self, avatar=None):
        return vehicle_getter.TankmenStatesIterator(avatar_getter.getVehicleDeviceStates(avatar), avatar_getter.getVehicleTypeDescriptor(avatar))

    def getGuiIterator(self, avatar=None):
        for name, state in self.getEntitiesIterator(avatar):
            yield (name, name, state)

    def _canActivate(self, entityName=None, avatar=None):
        result, error = super(_MedKitItem, self)._canActivate(entityName, avatar)
        return (True, IgnoreEntitySelection('', None)) if not result and type(error) not in (NeedEntitySelection, NotApplyingError) and avatar_getter.isVehicleStunned() and self.isReusable else (result, error)

    def _canApplyForEntity(self, entityName, deviceStates):
        if entityName not in deviceStates:
            if not avatar_getter.isVehicleStunned():
                return (False, NotApplyingError(self._getEntityIsSafeKey(), {'entity': self._getEntityUserString(entityName)}))
            return (self.isReusable, None)
        else:
            return (True, None)

    def _getEntitiesAreSafeKey(self):
        pass

    def _getEntityIsSafeKey(self):
        pass


class _RepairKitItem(_RefillEquipmentItem, _ExpandedItem):

    def getEntitiesIterator(self, avatar=None):
        return vehicle_getter.VehicleDeviceStatesIterator(avatar_getter.getVehicleDeviceStates(avatar), avatar_getter.getVehicleTypeDescriptor(avatar))

    def getGuiIterator(self, avatar=None):
        return vehicle_getter.VehicleGUIItemStatesIterator(avatar_getter.getVehicleDeviceStates(avatar), avatar_getter.getVehicleTypeDescriptor(avatar))

    def _getEntitiesAreSafeKey(self):
        pass

    def _getEntityIsSafeKey(self):
        pass

    def _getEntityUserString(self, entityName, avatar=None):
        return i18n.makeString('#ingame_gui:devices/{0}'.format(entityName)) if entityName in VEHICLE_COMPLEX_ITEMS else super(_RepairKitItem, self)._getEntityUserString(entityName, avatar)


class _RepairCrewAndModules(_ExpandedItem):

    def getEntitiesIterator(self, avatar=None):
        return itertools.chain(vehicle_getter.VehicleDeviceStatesIterator(avatar_getter.getVehicleDeviceStates(avatar), avatar_getter.getVehicleTypeDescriptor(avatar)), vehicle_getter.TankmenStatesIterator(avatar_getter.getVehicleDeviceStates(avatar), avatar_getter.getVehicleTypeDescriptor(avatar)))

    def canActivate(self, entityName=None, avatar=None):
        result, error = super(_RepairCrewAndModules, self).canActivate(entityName, avatar)
        return (True, IgnoreEntitySelection('', None)) if not result and type(error) not in (NeedEntitySelection, NotApplyingError) and avatar_getter.isVehicleStunned() else (result, error)

    def _getEntitiesAreSafeKey(self):
        pass

    def _getEntityIsSafeKey(self):
        pass

    def _getEntityUserString(self, entityName, avatar=None):
        return i18n.makeString('#ingame_gui:devices/{0}'.format(entityName)) if entityName in VEHICLE_COMPLEX_ITEMS else super(_RepairCrewAndModules, self)._getEntityUserString(entityName, avatar)


class _OrderItem(_TriggerItem):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _ACTIVATION_COOLDOWN = 0.2
    _lastActivationTime = 0

    def deactivate(self):
        if self._descriptor is not None:
            super(_OrderItem, self).deactivate()
        return

    def canActivate(self, entityName=None, avatar=None):
        if self._timeRemaining > 0 and self._stage and self._stage in (EQUIPMENT_STAGES.DEPLOYING, EQUIPMENT_STAGES.COOLDOWN, EQUIPMENT_STAGES.SHARED_COOLDOWN):
            error = self._getErrorMsg()
            return (False, error)
        else:
            result, error = super(_OrderItem, self).canActivate(entityName, avatar)
            if result:
                currentTime = BigWorld.time()
                if currentTime - _OrderItem._lastActivationTime > _OrderItem._ACTIVATION_COOLDOWN:
                    _OrderItem._lastActivationTime = currentTime
                else:
                    _logger.info('Attempt to use Arcade equipments simultaneously!')
                    return (False, None)
            return (result, error)

    def update(self, quantity, stage, timeRemaining, totalTime):
        self.updateMapCase(stage)
        super(_OrderItem, self).update(quantity, stage, timeRemaining, totalTime)

    def updateMapCase(self, stage=None):
        if not BigWorld.player().isObserver() or BigWorld.player().isObserverFPV:
            if self._stage == stage or self._stage == EQUIPMENT_STAGES.NOT_RUNNING:
                return
            if stage is None:
                stage = self._stage
            from AvatarInputHandler import MapCaseMode
            if stage == EQUIPMENT_STAGES.PREPARING and self._needActivateMapCase():
                MapCaseMode.activateMapCase(self.getEquipmentID(), partial(self.deactivate), self.getAimingControlMode())
            elif self._stage == EQUIPMENT_STAGES.PREPARING:
                if self._needActivateMapCase():
                    MapCaseMode.turnOffMapCase(self.getEquipmentID(), self.getAimingControlMode())
                else:
                    self.deactivate()
        return

    def _getErrorMsg(self):
        return NotReadyError(self._descriptor.userString)

    def getAimingControlMode(self):
        from AvatarInputHandler.MapCaseMode import MapCaseControlMode
        return MapCaseControlMode

    def _needActivateMapCase(self):
        inputHandler = avatar_getter.getInputHandler()
        arenaVisitor = self.__sessionProvider.arenaVisitor
        return not (inputHandler.ctrlModeName == CTRL_MODE_NAME.POSTMORTEM and arenaVisitor.getArenaBonusType() in ARENA_BONUS_TYPE.BATTLE_ROYALE_RANGE) if inputHandler is not None and arenaVisitor is not None else True


class _ArtilleryItem(_OrderItem):

    def getMarker(self):
        pass

    def getMarkerColor(self):
        return BATTLE_MARKERS_CONSTS.COLOR_YELLOW


class _ArtilleryAOEFort(_ArtilleryItem):

    def getMarker(self):
        pass

    def getMarkerColor(self):
        return BATTLE_MARKERS_CONSTS.COLOR_GREEN

    def getEnemyMarker(self):
        pass

    def getEnemyMarkerColor(self):
        return BATTLE_MARKERS_CONSTS.COLOR_RED


class _EpicArtilleryItem(_OrderItem):

    def getMarker(self):
        pass

    def getMarkerColor(self):
        return BATTLE_MARKERS_CONSTS.COLOR_GREEN

    def getAimingControlMode(self):
        from AvatarInputHandler.MapCaseMode import EpicMapCaseControlMode
        return EpicMapCaseControlMode


class _ArcadeArtilleryItem(_ArtilleryItem):

    def getAimingControlMode(self):
        from AvatarInputHandler.MapCaseMode import ArcadeMapCaseControlMode
        return ArcadeMapCaseControlMode

    def getMarker(self):
        pass

    def getMarkerColor(self):
        return BATTLE_MARKERS_CONSTS.COLOR_GREEN


class _BomberItem(_OrderItem):

    def getMarker(self):
        pass

    def getAimingControlMode(self):
        from AvatarInputHandler.MapCaseMode import EpicMapCaseControlMode
        return EpicMapCaseControlMode


class _BattleRoyaleBomber(_BomberItem):

    def _getErrorMsg(self):
        return InCooldownError(self._descriptor.userString)


class _ArcadeBomberItem(_BomberItem):

    def getAimingControlMode(self):
        from AvatarInputHandler.MapCaseMode import ArcadeMapCaseControlMode
        return ArcadeMapCaseControlMode

    def _getErrorMsg(self):
        return InCooldownError(self._descriptor.userString) if self._quantity else None


class _ArcadeMineFieldItem(_OrderItem):

    def getAimingControlMode(self):
        from AvatarInputHandler.MapCaseMode import ArcadeMapCaseControlMode
        return ArcadeMapCaseControlMode


class _ArcadeMineFieldEpicBattleItem(_OrderItem):

    def update(self, quantity, stage, timeRemaining, totalTime):
        if stage == EQUIPMENT_STAGES.PREPARING and self._stage != stage:
            SoundGroups.g_instance.playSound2D(EPIC_SOUND.EB_ABILITY_MINEFIELD_APPLY)
        super(_ArcadeMineFieldEpicBattleItem, self).update(quantity, stage, timeRemaining, totalTime)

    def getAimingControlMode(self):
        from AvatarInputHandler.MapCaseMode import AracdeMinefieldControleMode
        return AracdeMinefieldControleMode


class _ReconItem(_OrderItem):

    def getMarker(self):
        pass


class _SmokeItem(_OrderItem):

    def getMarker(self):
        pass


class _BattleRoyaleSmokeItem(_SmokeItem):

    def _getErrorMsg(self):
        return InCooldownError(self._descriptor.userString)


class _ArcadeSmokeItem(_SmokeItem):

    def getAimingControlMode(self):
        from AvatarInputHandler.MapCaseMode import ArcadeMapCaseControlMode
        return ArcadeMapCaseControlMode

    def _getErrorMsg(self):
        return InCooldownError(self._descriptor.userString) if self._quantity else None


class _StealthRadarItem(_OrderItem):
    pass


class _InspireItem(_OrderItem):
    pass


class _AfterburningItem(_TriggerItem):
    __slots__ = ('__totalDeployingTime', '__totalConsumingTime', '__totalRechargingTime', '__totalCooldownTime', '_prevTimeRemaining', '__fullyChargedSoundCbId', '__almostChargedSoundCbId', '__almostChargedSound', '__playingSoundObj')
    _FULL_CHARGE_DELAY_SOUND_TIME = 5.0
    _ALMOST_CHARGED_SOUND_ID = 'be_pre_replenishment'
    _EXAUSTED_SOUND_ID = 'be_nitro_empty'
    _STOPPED_BY_USER_SOUND_ID = 'be_nitro_stop'
    _ACTIVATED_SOUND_ID = 'be_nitro_activating'

    def __init__(self, descriptor, quantity, stage, timeRemaining, totalTime, tags=None):
        self.__totalDeployingTime = descriptor.deploySeconds
        self.__totalConsumingTime = descriptor.consumeSeconds
        self.__totalRechargingTime = descriptor.rechargeSeconds
        self.__totalCooldownTime = descriptor.cooldownSeconds
        self._prevTimeRemaining = -1
        self.__fullyChargedSoundCbId = None
        self.__almostChargedSoundCbId = None
        self.__almostChargedSound = None
        self.__playingSoundObj = None
        super(_AfterburningItem, self).__init__(descriptor, quantity, stage, timeRemaining, totalTime, tags)
        return

    def getTags(self):
        pass

    def clear(self):
        super(_AfterburningItem, self).clear()
        if self.__playingSoundObj and self.__playingSoundObj.isPlaying:
            self.__playingSoundObj.stop()
        self.__playingSoundObj = None
        if self.__fullyChargedSoundCbId is not None:
            BigWorld.cancelCallback(self.__fullyChargedSoundCbId)
        if self.__almostChargedSoundCbId is not None:
            BigWorld.cancelCallback(self.__almostChargedSoundCbId)
        return

    def update(self, quantity, stage, timeRemaining, totalTime):
        self._prevTimeRemaining = self._timeRemaining
        if self._stage != stage and self._stage in (EQUIPMENT_STAGES.READY, EQUIPMENT_STAGES.PREPARING):
            self._cleanReadyStageSounds()
        super(_AfterburningItem, self).update(quantity, stage, timeRemaining, totalTime)
        if stage == EQUIPMENT_STAGES.ACTIVE and self._prevStage != EQUIPMENT_STAGES.ACTIVE:
            self._animationType = ANIMATION_TYPES.MOVE_GREEN_BAR_DOWN | ANIMATION_TYPES.CENTER_COUNTER | ANIMATION_TYPES.GREEN_GLOW_SHOW | ANIMATION_TYPES.DARK_COLOR_TRANSFORM
            totalTime = self.__totalConsumingTime
            self.__createAndPlaySound(self._ACTIVATED_SOUND_ID)
        elif stage == EQUIPMENT_STAGES.PREPARING:
            self._animationType = ANIMATION_TYPES.MOVE_GREEN_BAR_UP | ANIMATION_TYPES.SHOW_COUNTER_GREEN
            if self._prevStage != stage and self._prevStage != EQUIPMENT_STAGES.COOLDOWN:
                self._animationType |= ANIMATION_TYPES.GREEN_GLOW_HIDE
            totalTime = self.__totalRechargingTime
            self.__processReadyStateSounds(timeRemaining)
            if self._prevStage == EQUIPMENT_STAGES.ACTIVE:
                self.__playSoundOnce(self._STOPPED_BY_USER_SOUND_ID)
        elif stage == EQUIPMENT_STAGES.DEPLOYING:
            self._animationType = ANIMATION_TYPES.MOVE_ORANGE_BAR_UP | ANIMATION_TYPES.SHOW_COUNTER_ORANGE
            totalTime = self.__totalDeployingTime
        elif stage == EQUIPMENT_STAGES.COOLDOWN:
            self._animationType = ANIMATION_TYPES.MOVE_ORANGE_BAR_UP | ANIMATION_TYPES.SHOW_COUNTER_ORANGE | ANIMATION_TYPES.FILL_PARTIALLY
            totalTime = self.__totalCooldownTime
            if self._prevStage == EQUIPMENT_STAGES.ACTIVE:
                self.__playSoundOnce(self._EXAUSTED_SOUND_ID)
        elif stage == EQUIPMENT_STAGES.READY and self.becomeReady:
            self.__processReadyStateSounds(timeRemaining)
        self._totalTime = totalTime

    def canActivate(self, entityName=None, avatar=None):
        result, error = False, None
        if self._stage in (EQUIPMENT_STAGES.READY, EQUIPMENT_STAGES.PREPARING, EQUIPMENT_STAGES.ACTIVE):
            result = True
        elif self._stage == EQUIPMENT_STAGES.COOLDOWN and self._quantity:
            error = InCooldownError(self._descriptor.userString)
        elif self._stage == EQUIPMENT_STAGES.DEPLOYING:
            error = NotReadyError(self._descriptor.userString)
        return (result, error)

    def getEntitiesIterator(self, avatar=None):
        return []

    @property
    def becomeReady(self):
        return super(_AfterburningItem, self).becomeReady

    def _soundUpdate(self, prevQuantity, quantity):
        pass

    def _cleanReadyStageSounds(self):
        self.__cleanFullReadySound()
        self.__cleanAlmostReadySound()

    def _playChargedSound(self):
        EquipmentSound.playReady(self)
        self.__fullyChargedSoundCbId = None
        return

    def _playAlmostChargedSound(self):
        if self.__almostChargedSound is None:
            self.__almostChargedSound = SoundGroups.g_instance.getSound2D(self._ALMOST_CHARGED_SOUND_ID)
        else:
            self.__almostChargedSound.stop()
        self.__almostChargedSound.play()
        self.__almostChargedSoundCbId = None
        return

    def __processReadyStateSounds(self, timeRemaining):
        if timeRemaining > -1:
            self.__cleanFullReadySound()
            self.__fullyChargedSoundCbId = BigWorld.callback(timeRemaining, self._playChargedSound)
            if timeRemaining >= self._FULL_CHARGE_DELAY_SOUND_TIME:
                self.__cleanAlmostReadySound()
                if self.__almostChargedSound is not None:
                    self.__almostChargedSound.stop()
                self.__almostChargedSoundCbId = BigWorld.callback(timeRemaining - self._FULL_CHARGE_DELAY_SOUND_TIME, self._playAlmostChargedSound)
        elif self.becomeReady:
            self.__cleanFullReadySound()
            self._playChargedSound()
        return

    def __cleanAlmostReadySound(self):
        if self.__almostChargedSoundCbId is not None:
            BigWorld.cancelCallback(self.__almostChargedSoundCbId)
            self.__almostChargedSoundCbId = None
        return

    def __cleanFullReadySound(self):
        if self.__fullyChargedSoundCbId is not None:
            BigWorld.cancelCallback(self.__fullyChargedSoundCbId)
            self.__fullyChargedSoundCbId = None
        return

    def __playSoundOnce(self, sound):
        SoundGroups.g_instance.playSound2D(sound)

    def __createAndPlaySound(self, sound):
        self.__playingSoundObj = SoundGroups.g_instance.getSound2D(sound)
        self.__playingSoundObj.play()


class _RegenerationKitItem(_EquipmentItem):

    def canActivate(self, entityName=None, avatar=None):
        if self._timeRemaining <= 0 < self._quantity and self._stage in (EQUIPMENT_STAGES.READY, EQUIPMENT_STAGES.PREPARING):
            result = True
            error = None
        else:
            result = False
            error = None
            if self._stage == EQUIPMENT_STAGES.COOLDOWN and self._quantity:
                error = NotReadyError(self._descriptor.userString)
        if not result or not avatar:
            return (result, error)
        else:
            vehicle = BigWorld.entities.get(avatar.playerVehicleID)
            return (False, _ActivationError('vehicleIsNotDamaged', {'name': self._descriptor.userString})) if not vehicle or vehicle.health >= vehicle.maxHealth and not any((deviceState in ('destroyed', 'critical') for deviceState in avatar.deviceStates.itervalues())) else (True, None)

    def getActivationCode(self, entityName=None, avatar=None):
        return 65536 + self._descriptor.id[1]

    def getAnimationType(self):
        return ANIMATION_TYPES.MOVE_GREEN_BAR_DOWN | ANIMATION_TYPES.SHOW_COUNTER_ORANGE | ANIMATION_TYPES.DARK_COLOR_TRANSFORM if self._stage == EQUIPMENT_STAGES.ACTIVE else super(_RegenerationKitItem, self).getAnimationType()


class DynComponentsGroupItem(_TriggerItem):

    def update(self, quantity, stage, timeRemaining, totalTime):
        super(DynComponentsGroupItem, self).update(quantity, stage, timeRemaining, totalTime)
        if stage in (EQUIPMENT_STAGES.COOLDOWN, EQUIPMENT_STAGES.READY):
            self._totalTime = self._descriptor.cooldownSeconds
        elif stage == EQUIPMENT_STAGES.ACTIVE:
            self._timeRemaining = min(self._timeRemaining, self._descriptor.durationSeconds)
            self._totalTime = self._descriptor.durationSeconds

    def getEntitiesIterator(self, avatar=None):
        return []

    def getGuiIterator(self, avatar=None):
        return []


class DynComponentsGroupPassiveItem(DynComponentsGroupItem):

    def canActivate(self, entityName=None, avatar=None):
        return (False, None)


class _VisualScriptItem(_TriggerItem):

    def __init__(self, *args):
        self.__canDeactivate = False
        super(_VisualScriptItem, self).__init__(*args)

    def _getErrorMsg(self):
        stage = self.getStage()
        return InCooldownError(self._descriptor.userString) if stage == EQUIPMENT_STAGES.COOLDOWN else NotReadyError(self._descriptor.userString)

    def canActivate(self, entityName=None, avatar=None):
        if not avatar:
            avatar = BigWorld.player()
        visualScriptEquipment = self._getComponent(avatar)
        if visualScriptEquipment is not None:
            _, errorKey = visualScriptEquipment.canActivate()
            if errorKey is not None:
                return (False, _ActivationError(errorKey, {'name': self._descriptor.userString}))
        else:
            _logger.error('Missing VisualScriptEquipment dynamic component.')
            return (False, None)
        if self._stage in (EQUIPMENT_STAGES.UNAVAILABLE,
         EQUIPMENT_STAGES.COOLDOWN,
         EQUIPMENT_STAGES.NOT_RUNNING,
         EQUIPMENT_STAGES.EXHAUSTED):
            error = self._getErrorMsg()
            return (False, error)
        else:
            return super(_VisualScriptItem, self).canActivate(entityName=entityName, avatar=avatar)

    def canDeactivate(self):
        return super(_VisualScriptItem, self).canDeactivate() and self.__canDeactivate

    def getEntitiesIterator(self, avatar=None):
        return []

    def getGuiIterator(self, avatar=None):
        return []

    def updateMapCase(self, stage=None):
        if BigWorld.player().isObserver() and not BigWorld.player().isObserverFPV:
            return
        else:
            aimingControlMode = self._getAimingControlMode()
            if aimingControlMode is None:
                return
            if self._stage == stage:
                return
            if stage is None:
                stage = self._stage
            from AvatarInputHandler import MapCaseMode
            if stage == EQUIPMENT_STAGES.PREPARING:
                MapCaseMode.activateMapCase(self.getEquipmentID(), partial(self.deactivate), aimingControlMode)
            elif self._stage == EQUIPMENT_STAGES.PREPARING:
                MapCaseMode.turnOffMapCase(self.getEquipmentID(), aimingControlMode)
            return

    def update(self, quantity, stage, timeRemaining, totalTime):
        self.updateMapCase(stage)
        if stage != self._stage:
            self.__canDeactivate = stage in (EQUIPMENT_STAGES.PREPARING,)
        super(_VisualScriptItem, self).update(quantity, stage, timeRemaining, totalTime)
        if stage in (EQUIPMENT_STAGES.COOLDOWN, EQUIPMENT_STAGES.ACTIVE):
            self._totalTime = timeRemaining
        elif stage in (EQUIPMENT_STAGES.UNAVAILABLE,
         EQUIPMENT_STAGES.READY,
         EQUIPMENT_STAGES.PREPARING,
         EQUIPMENT_STAGES.EXHAUSTED):
            self._totalTime = 0

    def deactivate(self):
        super(_VisualScriptItem, self).deactivate()
        self.__canDeactivate = False

    def getAnimationType(self):
        return ANIMATION_TYPES.MOVE_GREEN_BAR_DOWN | ANIMATION_TYPES.SHOW_COUNTER_GREEN | ANIMATION_TYPES.DARK_COLOR_TRANSFORM if self._stage == EQUIPMENT_STAGES.ACTIVE else super(_VisualScriptItem, self).getAnimationType()

    def _getComponent(self, avatar=None):
        if not avatar:
            avatar = BigWorld.player()
        vehicle = avatar.getVehicleAttached()
        return vehicle.dynamicComponents.get(self._descriptor.name) if vehicle is not None else None

    def _getAimingControlMode(self):
        return None


class _PoiEquipmentItemVS(_VisualScriptItem):

    def canActivate(self, entityName=None, avatar=None):
        return (False, self._getErrorMsg()) if not self._getComponent() else super(_PoiEquipmentItemVS, self).canActivate(entityName, avatar)

    def _getErrorMsg(self):
        return PoiUnavailableError(self._descriptor.name) if self._stage in (EQUIPMENT_STAGES.UNAVAILABLE, EQUIPMENT_STAGES.NOT_RUNNING, EQUIPMENT_STAGES.EXHAUSTED) else super(_PoiEquipmentItemVS, self)._getErrorMsg()


class _PoiArtilleryItem(_ArtilleryItem):

    def getMarker(self):
        pass

    def getMarkerColor(self):
        return BATTLE_MARKERS_CONSTS.COLOR_GREEN

    def _getErrorMsg(self):
        return PoiUnavailableError(self._descriptor.name) if self._stage in (EQUIPMENT_STAGES.UNAVAILABLE, EQUIPMENT_STAGES.NOT_RUNNING, EQUIPMENT_STAGES.EXHAUSTED) else super(_PoiArtilleryItem, self)._getErrorMsg()

    def canActivate(self, entityName=None, avatar=None):
        return (False, self._getErrorMsg()) if self._stage in (EQUIPMENT_STAGES.UNAVAILABLE, EQUIPMENT_STAGES.NOT_RUNNING, EQUIPMENT_STAGES.EXHAUSTED) else super(_PoiArtilleryItem, self).canActivate(entityName, avatar)


class _RoleSkillVSItem(_VisualScriptItem):

    def update(self, quantity, stage, timeRemaining, totalTime):
        prevQuantity = self._prevQuantity
        super(_RoleSkillVSItem, self).update(quantity, stage, timeRemaining, totalTime)
        self._prevQuantity = prevQuantity
        self._quantity = self.getQuantity()

    def _getErrorMsg(self):
        if self._stage == EQUIPMENT_STAGES.UNAVAILABLE:
            return Comp7RoleSkillUnavailable(self._descriptor.userString)
        if self._stage == EQUIPMENT_STAGES.ACTIVE:
            return Comp7RoleSkillAlreadyActivated(self._descriptor.userString)
        return Comp7RoleSkillCooldown(self._descriptor.userString) if self._stage == EQUIPMENT_STAGES.COOLDOWN else super(_RoleSkillVSItem, self)._getErrorMsg()

    def getQuantity(self):
        component = self._getComponent()
        if component is None:
            return 0
        else:
            available, _ = self.canActivate()
            return int(available)

    def canActivate(self, entityName=None, avatar=None):
        return (False, self._getErrorMsg()) if self._stage in (EQUIPMENT_STAGES.COOLDOWN, EQUIPMENT_STAGES.ACTIVE, EQUIPMENT_STAGES.UNAVAILABLE) else super(_RoleSkillVSItem, self).canActivate(entityName, avatar)


class _DeferredRoleSkillVSItem(_RoleSkillVSItem):
    _ACTIVATION_COOLDOWN = 0.2
    _lastActivationTime = 0

    def __init__(self, *args):
        super(_DeferredRoleSkillVSItem, self).__init__(*args)
        g_playerEvents.onRoundFinished += self.__onRoundFinished

    def clear(self):
        super(_DeferredRoleSkillVSItem, self).clear()
        g_playerEvents.onRoundFinished -= self.__onRoundFinished

    def canActivate(self, entityName=None, avatar=None):
        result, error = super(_DeferredRoleSkillVSItem, self).canActivate(entityName, avatar)
        if result and avatar:
            currentTime = BigWorld.time()
            if currentTime - self._lastActivationTime < self._ACTIVATION_COOLDOWN:
                return (False, None)
            self._lastActivationTime = currentTime
        return (result, error)

    def __onRoundFinished(self, *_):
        from AvatarInputHandler import MapCaseMode
        MapCaseMode.turnOffMapCase(self.getEquipmentID(), self._getAimingControlMode())


class _RoleSkillReconVSItem(_DeferredRoleSkillVSItem):

    def _getAimingControlMode(self):
        from AvatarInputHandler.MapCaseMode import MapCaseControlMode
        return MapCaseControlMode


class _RoleSkillArtyVSItem(_DeferredRoleSkillVSItem):

    def _getAimingControlMode(self):
        from AvatarInputHandler.MapCaseMode import MapCaseControlMode
        return MapCaseControlMode

    def getMarker(self):
        pass

    def getMarkerColor(self):
        return BATTLE_MARKERS_CONSTS.COLOR_GREEN


class _GameplayConsumableItem(_TriggerItem):

    def getTags(self):
        pass

    def getEntitiesIterator(self, avatar=None):
        return []


class _RepairPointItem(_TriggerItem):

    def getTags(self):
        pass

    def getEntitiesIterator(self, avatar=None):
        return []


def _isBattleRoyaleBattle():
    return BigWorld.player().arena.bonusType in ARENA_BONUS_TYPE.BATTLE_ROYALE_RANGE if BigWorld.player() is not None else False


def _triggerItemFactory(descriptor, quantity, stage, timeRemaining, totalTime, tags=None):
    if descriptor.name.startswith('arcade_artillery'):
        return _ArcadeArtilleryItem(descriptor, quantity, stage, timeRemaining, totalTime, tags)
    if descriptor.name.startswith('arcade_bomber'):
        return _ArcadeBomberItem(descriptor, quantity, stage, timeRemaining, totalTime, tags)
    if descriptor.name.startswith('arcade_minefield_epic_battle'):
        return _ArcadeMineFieldEpicBattleItem(descriptor, quantity, stage, timeRemaining, totalTime, tags)
    if descriptor.name.startswith('arcade_minefield'):
        return _ArcadeMineFieldItem(descriptor, quantity, stage, timeRemaining, totalTime, tags)
    if descriptor.name.startswith('artillery_epic'):
        return _EpicArtilleryItem(descriptor, quantity, stage, timeRemaining, totalTime, tags)
    if descriptor.name.startswith('artillery_aoe_fort'):
        return _ArtilleryAOEFort(descriptor, quantity, stage, timeRemaining, totalTime, tags)
    if descriptor.name.startswith('artillery'):
        return _ArtilleryItem(descriptor, quantity, stage, timeRemaining, totalTime, tags)
    if descriptor.name.startswith('bomber'):
        return _getBomberItem(descriptor, quantity, stage, timeRemaining, totalTime, tags)
    if descriptor.name.startswith('smoke'):
        return _getSmokeItem(descriptor, quantity, stage, timeRemaining, totalTime, tags)
    if descriptor.name.startswith('inspire'):
        return _InspireItem(descriptor, quantity, stage, timeRemaining, totalTime, tags)
    if descriptor.name.startswith('arcade_smoke'):
        return _ArcadeSmokeItem(descriptor, quantity, stage, timeRemaining, totalTime, tags)
    if descriptor.name.startswith('recon'):
        return _ReconItem(descriptor, quantity, stage, timeRemaining, totalTime, tags)
    if descriptor.name.startswith('afterburning'):
        return _AfterburningItem(descriptor, quantity, stage, timeRemaining, totalTime, tags)
    return _StealthRadarItem(descriptor, quantity, stage, timeRemaining, totalTime, tags) if descriptor.name.startswith('stealth_radar') else _TriggerItem(descriptor, quantity, stage, timeRemaining, totalTime, tags)


def _comp7ItemFactory(descriptor, quantity, stage, timeRemaining, totalTime, tag=None):
    if descriptor.name.startswith('comp7_recon'):
        itemClass = _RoleSkillReconVSItem
    elif descriptor.name.startswith('comp7_redline'):
        itemClass = _RoleSkillArtyVSItem
    else:
        itemClass = _RoleSkillVSItem
    return itemClass(descriptor, quantity, stage, timeRemaining, totalTime, tag)


def _poiItemFactory(descriptor, quantity, stage, timeRemaining, totalTime, tag=None):
    if descriptor.name.startswith('poi_artillery_aoe'):
        itemClass = _PoiArtilleryItem
    else:
        itemClass = _PoiEquipmentItemVS
    return itemClass(descriptor, quantity, stage, timeRemaining, totalTime, tag)


def _getBomberItem(descriptor, quantity, stage, timeRemaining, totalTime, tags=None):
    isBattleRoyaleMode = _isBattleRoyaleBattle()
    return _BattleRoyaleBomber(descriptor, quantity, stage, timeRemaining, totalTime, tags) if isBattleRoyaleMode else _BomberItem(descriptor, quantity, stage, timeRemaining, totalTime, tags)


def _getSmokeItem(descriptor, quantity, stage, timeRemaining, totalTime, tags=None):
    isBattleRoyaleMode = _isBattleRoyaleBattle()
    return _BattleRoyaleSmokeItem(descriptor, quantity, stage, timeRemaining, totalTime, tags) if isBattleRoyaleMode else _SmokeItem(descriptor, quantity, stage, timeRemaining, totalTime, tags)


_EQUIPMENT_TAG_TO_ITEM = {('fuel',): _AutoItem,
 ('stimulator',): _AutoItem,
 ('trigger',): _triggerItemFactory,
 ('extinguisher',): _ExtinguisherItem,
 ('medkit',): _MedKitItem,
 ('repairkit',): _RepairKitItem,
 ('regenerationKit',): _RegenerationKitItem,
 ('medkit', 'repairkit'): _RepairCrewAndModules,
 ('dynComponentsGroup',): DynComponentsGroupItem,
 ('dynComponentsGroup', 'passive'): DynComponentsGroupPassiveItem,
 (ROLE_EQUIPMENT_TAG,): _comp7ItemFactory,
 (POI_EQUIPMENT_TAG,): _poiItemFactory}

class _DAMAGE_PANEL_EQUIPMENT(CONST_CONTAINER):
    EXTINGUISHER = 'extinguisher'
    MEDKIT = 'medkit'
    REPAIRKIT = 'repairkit'


def _getInitialTagsAndClass(descriptor, tagsToItems):
    descrTags = descriptor.tags
    tagsCandidate, clazzCandidate = tuple(), None
    for requiredTags, itemClass in tagsToItems.iteritems():
        for tag in requiredTags:
            if tag not in descrTags:
                break
        else:
            if len(requiredTags) > len(tagsCandidate):
                tagsCandidate = requiredTags
                clazzCandidate = itemClass

    return (tagsCandidate, clazzCandidate)


class EquipmentsController(MethodsRules, IBattleController):
    __slots__ = ('_eManager', '__arena', '_order', '_equipments', '__preferredPosition', '__equipmentCount', 'onEquipmentAdded', 'onEquipmentUpdated', 'onEquipmentMarkerShown', 'onEquipmentCooldownInPercent', 'onEquipmentCooldownTime', 'onCombatEquipmentUsed', 'onEquipmentReset', 'onEquipmentsCleared')

    def __init__(self, setup):
        super(EquipmentsController, self).__init__()
        self._eManager = Event.EventManager()
        self.onEquipmentAdded = Event.Event(self._eManager)
        self.onSlotWaited = Event.Event(self._eManager)
        self.onSlotBlocked = Event.Event(self._eManager)
        self.onEquipmentUpdated = Event.Event(self._eManager)
        self.onEquipmentReset = Event.Event(self._eManager)
        self.onEquipmentsCleared = Event.Event(self._eManager)
        self.onEquipmentMarkerShown = Event.Event(self._eManager)
        self.onEquipmentAreaCreated = Event.Event(self._eManager)
        self.onEquipmentCooldownInPercent = Event.Event(self._eManager)
        self.onEquipmentCooldownTime = Event.Event(self._eManager)
        self.onCombatEquipmentUsed = Event.Event(self._eManager)
        self._order = []
        self._equipments = {}
        self._equipmentsIdxSlot = {}
        self.__preferredPosition = None
        self.__equipmentCount = 0
        self.__arena = setup.arenaEntity
        return

    def __repr__(self):
        return 'EquipmentsController({0!r:s})'.format(self._equipments)

    def getControllerID(self):
        return BATTLE_CTRL_ID.EQUIPMENTS

    def startControl(self, *args):
        self.__arena.onCombatEquipmentUsed += self.onCombatEquipmentUsed

    def stopControl(self):
        self.__arena.onCombatEquipmentUsed -= self.onCombatEquipmentUsed
        self.__arena = None
        self.clear(leave=True)
        return

    @classmethod
    def _findExtendItem(cls, isReplay, name, *args):
        return collectEquipmentItem(name, isReplay, args)

    @classmethod
    def createItem(cls, descriptor, quantity, stage, timeRemaining, totalTime):
        item = cls._findExtendItem(False, descriptor.name, descriptor, quantity, stage, timeRemaining, totalTime)
        if item:
            return item
        tags, clazz = _getInitialTagsAndClass(descriptor, _EQUIPMENT_TAG_TO_ITEM)
        if tags:
            item = clazz(descriptor, quantity, stage, timeRemaining, totalTime, tags)
        else:
            item = _EquipmentItem(descriptor, quantity, stage, timeRemaining, totalTime, tags)
        return item

    def clear(self, leave=True):
        super(EquipmentsController, self).clear(True)
        _logger.debug('EquipmentsController CLEARED')
        if leave:
            self._eManager.clear()
        self._order = []
        while self._equipments:
            _, item = self._equipments.popitem()
            item.clear()

        self.__equipmentCount = 0
        self._equipmentsIdxSlot.clear()
        if not leave:
            self.onEquipmentsCleared()

    def cancel(self):
        item = findFirst(lambda item: item.getStage() == EQUIPMENT_STAGES.PREPARING and item.canDeactivate(), self._equipments.itervalues())
        if item is not None:
            item.deactivate()
            return True
        else:
            return False

    def hasEquipment(self, intCD):
        return intCD in self._equipments

    def iterEquipmentsByTag(self, tag, condition=None):
        return ((intCD, item) for intCD, item in self._equipments.iteritems() if tag in item.getTags() and (condition is None or condition(item)))

    def getEquipmentNameByID(self, itemID):
        item = vehicles.g_cache.equipments().get(itemID, None)
        return item.name if item is not None else None

    def getEquipment(self, intCD):
        try:
            item = self._equipments[intCD]
        except KeyError:
            _logger.error('Equipment is not found by CD. %d', intCD)
            item = None

        return item

    def getEquipmentByIDx(self, idx):
        item = self._equipmentsIdxSlot.get(idx)
        return item[0] if item else None

    def getOrderedEquipmentsLayout(self):
        return [ (intCD, self._equipments[intCD]) for intCD in self._order if intCD ]

    def getOrderedEquipments(self):
        return [ self._equipments[intCD] for intCD in self._order if intCD in self._equipments ]

    @MethodsRules.delayable()
    def notifyPlayerVehicleSet(self, vID):
        vehicle = BigWorld.entity(vID)
        if vehicle is not None:
            self.__equipmentCount = vehicle.typeDescriptor.type.supplySlots.getAmountForType(ITEM_TYPES.equipment, EQUIPMENT_TYPES.regular)
        else:
            self.__equipmentCount = 0
        return

    @MethodsRules.delayable('notifyPlayerVehicleSet')
    def setEquipment(self, intCD, quantity, stage, timeRemaining, totalTime, index=0):
        _logger.debug('Equipment added: intCD=%d, quantity=%d, stage=%s, timeRemaining=%d, totalTime=%d', intCD, quantity, stage, timeRemaining, totalTime)
        index -= 1
        slot = self._equipmentsIdxSlot.get(index, None)
        equipmentItem = slot[0] if slot and slot[1] == intCD else None
        slotIdx = len(self._equipmentsIdxSlot)
        if not intCD:
            if len(self._order) < self.__equipmentCount:
                self._order.append(0)
                self.onEquipmentAdded(0, None)
        elif intCD in self._equipments and index < 0 or equipmentItem:
            item = equipmentItem if equipmentItem else self._equipments[intCD]
            item.update(quantity, stage, timeRemaining, totalTime)
            if item.isValid():
                self.onEquipmentUpdated(intCD, item)
        else:
            descriptor = vehicles.getItemByCompactDescr(intCD)
            if descriptor.equipmentType in (EQUIPMENT_TYPES.regular, EQUIPMENT_TYPES.battleAbilities):
                item = self.createItem(descriptor, quantity, stage, timeRemaining, totalTime)
                if not item:
                    return
                self._equipments[intCD] = item
                self._order.append(intCD)
                item.updateMapCase()
                if index >= 0:
                    item.setIndex(index + 1)
                    self._equipmentsIdxSlot[index] = (item, intCD, slotIdx)
                self.onEquipmentAdded(intCD, item)
                item.setServerPrevStage(None)
        return

    def updateMapCase(self):
        for item in self._equipments.itervalues():
            item.updateMapCase()

    @MethodsRules.delayable('notifyPlayerVehicleSet')
    def resetEquipment(self, oldIntCD, newIntCD, quantity, stage, timeRemaining, totalTime, index):
        if oldIntCD not in self._order:
            return
        else:
            index -= 1
            slot = self._equipmentsIdxSlot.get(index, None)
            equipmentItem = slot if slot else None
            if oldIntCD in self._equipments:
                del self._equipments[oldIntCD]
            _logger.debug('Equipment reset: oldIntCD=%d, newIntCD=%d, quantity=%d, stage=%s, timeRemaining=%d,totalTime=%d, index=%d', oldIntCD, newIntCD, quantity, stage, timeRemaining, totalTime, index)
            descriptor = vehicles.getItemByCompactDescr(newIntCD)
            item = self.createItem(descriptor, quantity, stage, timeRemaining, totalTime)
            if equipmentItem:
                item.setIndex(index + 1)
                self._equipmentsIdxSlot[index] = (item, newIntCD, equipmentItem[2])
            self._equipments[newIntCD] = item
            self._order[self._order.index(oldIntCD)] = newIntCD
            self.onEquipmentReset(oldIntCD, newIntCD, item)
            return

    def setServerPrevStage(self, **kwargs):
        compactDescr = kwargs.get('compactDescr')
        prevStage = kwargs.get('previousStage')
        if compactDescr in self._equipments:
            self._equipments[compactDescr].setServerPrevStage(prevStage)

    def getEquipments(self):
        return self._equipments

    def getActivationCode(self, intCD, entityName=None, avatar=None):
        code = None
        item = self.getEquipment(intCD)
        if item:
            code = item.getActivationCode(entityName, avatar)
        return code

    def canActivate(self, intCD, entityName=None, avatar=None):
        result, error = False, None
        item = self.getEquipment(intCD)
        if item:
            result, error = item.canActivate(entityName, avatar)
        return (result, error)

    def changeSetting(self, intCD, entityName=None, avatar=None, idx=None):
        if not avatar_getter.isVehicleAlive(avatar):
            return (False, None)
        else:
            result, error = False, None
            if idx is not None and idx >= 0:
                item = self.getEquipmentByIDx(idx)
            else:
                item = self.getEquipment(intCD)
            if item:
                result, error = self.__doChangeSetting(item, entityName, avatar)
            return (result, error)

    def changeSettingByTag(self, tag, entityName=None, avatar=None):
        if not avatar_getter.isVehicleAlive(avatar):
            return (False, None)
        else:
            result, error = True, None
            for _, item in self._equipments.iteritems():
                if tag in item.getTags() and _DAMAGE_PANEL_EQUIPMENT.hasValue(tag):
                    result, error = self.__doChangeSetting(item, entityName, avatar)
                    break

            return (result, error)

    def showMarker(self, eq, pos, direction, time, team=None):
        item = findFirst(lambda e: e.getEquipmentID() == eq.id[1], self._equipments.itervalues())
        if item is None:
            item = self.createItem(eq, 0, -1, 0, 0)
        self.onEquipmentMarkerShown(item, pos, direction, time, team)
        return

    def consumePreferredPosition(self):
        value = self.__preferredPosition
        self.__preferredPosition = None
        return value

    def __doChangeSetting(self, item, entityName=None, avatar=None):
        result, error = item.canActivate(entityName, avatar)
        if result and avatar_getter.isPlayerOnArena(avatar):
            if item.getStage() == EQUIPMENT_STAGES.PREPARING:
                item.deactivate()
            else:
                avatar = BigWorld.player()
                curCtrl = avatar.inputHandler.ctrl
                if curCtrl is not None and curCtrl.isEnabled:
                    desiredShotPoint = curCtrl.getDesiredShotPoint(ignoreAimingMode=True)
                    vehicle = avatar.getVehicleAttached()
                    gunRotator = avatar.gunRotator
                    if gunRotator:
                        hitPoint, _ = getShotTargetInfo(vehicle, desiredShotPoint, gunRotator)
                        if vehicle and vehicle.position.distTo(hitPoint) < vehicle.position.distTo(desiredShotPoint):
                            desiredShotPoint = hitPoint
                    self.__preferredPosition = desiredShotPoint
                forEach(lambda e: e.deactivate(), [ e for e in self._equipments.itervalues() if e.getStage() == EQUIPMENT_STAGES.PREPARING ])
                item.activate(entityName, avatar)
        return (result, error)


class _ReplayItem(_EquipmentItem):
    __slots__ = ('__cooldownTime',)

    def __init__(self, descriptor, quantity, stage, timeRemaining, totalTime, tags=None):
        super(_ReplayItem, self).__init__(descriptor, quantity, stage, timeRemaining, totalTime, tags)
        self.__cooldownTime = BigWorld.serverTime() + timeRemaining

    def update(self, quantity, stage, timeRemaining, totalTime):
        super(_ReplayItem, self).update(quantity, stage, timeRemaining, totalTime)
        self.__cooldownTime = BigWorld.serverTime() + timeRemaining

    def getEntitiesIterator(self, avatar=None):
        return []

    def getGuiIterator(self, avatar=None):
        return []

    def canActivate(self, entityName=None, avatar=None):
        return (False, None)

    def getReplayTimeRemaining(self):
        return max(0, self.__cooldownTime - BigWorld.serverTime())

    def getCooldownPercents(self):
        totalTime = self.getTotalTime()
        timeRemaining = self.getReplayTimeRemaining()
        return round(float(totalTime - timeRemaining) / totalTime * 100.0) if totalTime > 0 else 0.0


class _ReplayMedKitItem(_ReplayItem):
    __slots__ = ('__cooldownTime',)

    def getEntitiesIterator(self, avatar=None):
        return vehicle_getter.TankmenStatesIterator(avatar_getter.getVehicleDeviceStates(avatar), avatar_getter.getVehicleTypeDescriptor(avatar))


class _ReplayRepairKitItem(_ReplayItem):
    __slots__ = ('__cooldownTime',)

    def getEntitiesIterator(self, avatar=None):
        return vehicle_getter.VehicleDeviceStatesIterator(avatar_getter.getVehicleDeviceStates(avatar), avatar_getter.getVehicleTypeDescriptor(avatar))


class _ReplayOrderItem(_ReplayItem):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def deactivate(self):
        if self._descriptor is not None:
            super(_ReplayOrderItem, self).deactivate()
        return

    def getAimingControlMode(self):
        from AvatarInputHandler.MapCaseMode import MapCaseControlMode
        return MapCaseControlMode

    def update(self, quantity, stage, timeRemaining, totalTime):
        from AvatarInputHandler import MapCaseMode
        if stage == EQUIPMENT_STAGES.PREPARING and self._stage != stage and self._needActivateMapCase():
            MapCaseMode.activateMapCase(self.getEquipmentID(), partial(self.deactivate), self.getAimingControlMode())
        elif self._stage == EQUIPMENT_STAGES.PREPARING and self._stage != stage:
            if self._needActivateMapCase():
                MapCaseMode.turnOffMapCase(self.getEquipmentID(), self.getAimingControlMode())
            else:
                self.deactivate()
        super(_ReplayOrderItem, self).update(quantity, stage, timeRemaining, totalTime)

    def _needActivateMapCase(self):
        inputHandler = avatar_getter.getInputHandler()
        arenaVisitor = self.__sessionProvider.arenaVisitor
        return not (inputHandler.ctrlModeName == CTRL_MODE_NAME.POSTMORTEM and arenaVisitor.getArenaBonusType() in ARENA_BONUS_TYPE.BATTLE_ROYALE_RANGE) if inputHandler is not None and arenaVisitor is not None else True


class _ReplayArtilleryItem(_ReplayOrderItem):

    def getMarker(self):
        pass

    def getMarkerColor(self):
        return BATTLE_MARKERS_CONSTS.COLOR_YELLOW


class _ReplayArtilleryAOEFort(_ReplayArtilleryItem):

    def getMarker(self):
        pass

    def getMarkerColor(self):
        return BATTLE_MARKERS_CONSTS.COLOR_GREEN

    def getEnemyMarker(self):
        pass

    def getEnemyMarkerColor(self):
        return BATTLE_MARKERS_CONSTS.COLOR_RED


class _ReplayArcadeArtilleryItem(_ReplayOrderItem):

    def getMarker(self):
        pass


class _ReplayBomberItem(_ReplayOrderItem):

    def getAimingControlMode(self):
        from AvatarInputHandler.MapCaseMode import ArcadeMapCaseControlMode
        return ArcadeMapCaseControlMode

    def getMarker(self):
        pass


class _ReplayReconItem(_ReplayOrderItem):

    def getMarker(self):
        pass


class _ReplaySmokeItem(_ReplayOrderItem):

    def getMarker(self):
        pass


class _ReplayAfterburningItem(_ReplayItem):
    __slots__ = ('__totalDeployingTime', '__totalConsumingTime', '__totalRechargingTime', '__totalCooldownTime', '_prevTimeRemaining', '__fullyChargedSoundCbId', '__almostChargedSoundCbId', '__almostChargedSound', '__playingSoundObj', '_animationType', '_totalTime')
    _FULL_CHARGE_DELAY_SOUND_TIME = 5.0
    _ALMOST_CHARGED_SOUND_ID = 'be_pre_replenishment'
    _EXAUSTED_SOUND_ID = 'be_nitro_empty'
    _STOPPED_BY_USER_SOUND_ID = 'be_nitro_stop'
    _ACTIVATED_SOUND_ID = 'be_nitro_activating'

    def __init__(self, descriptor, quantity, stage, timeRemaining, totalTime, tags=None):
        self.__totalDeployingTime = descriptor.deploySeconds
        self.__totalConsumingTime = descriptor.consumeSeconds
        self.__totalRechargingTime = descriptor.rechargeSeconds
        self.__totalCooldownTime = descriptor.cooldownSeconds
        self._prevTimeRemaining = -1
        self.__fullyChargedSoundCbId = None
        self.__almostChargedSoundCbId = None
        self.__almostChargedSound = None
        self.__playingSoundObj = None
        super(_ReplayAfterburningItem, self).__init__(descriptor, quantity, stage, timeRemaining, totalTime, tags)
        return

    def getTags(self):
        pass

    def clear(self):
        super(_ReplayAfterburningItem, self).clear()
        if self.__playingSoundObj and self.__playingSoundObj.isPlaying:
            self.__playingSoundObj.stop()
        self.__playingSoundObj = None
        if self.__fullyChargedSoundCbId is not None:
            BigWorld.cancelCallback(self.__fullyChargedSoundCbId)
        if self.__almostChargedSoundCbId is not None:
            BigWorld.cancelCallback(self.__almostChargedSoundCbId)
        return

    def update(self, quantity, stage, timeRemaining, totalTime):
        self._prevTimeRemaining = self._timeRemaining
        if self._stage != stage and self._stage in (EQUIPMENT_STAGES.READY, EQUIPMENT_STAGES.PREPARING):
            self._cleanReadyStageSounds()
        super(_ReplayAfterburningItem, self).update(quantity, stage, timeRemaining, totalTime)
        if stage == EQUIPMENT_STAGES.ACTIVE and self._prevStage != EQUIPMENT_STAGES.ACTIVE:
            self._animationType = ANIMATION_TYPES.MOVE_GREEN_BAR_DOWN | ANIMATION_TYPES.CENTER_COUNTER | ANIMATION_TYPES.GREEN_GLOW_SHOW | ANIMATION_TYPES.DARK_COLOR_TRANSFORM
            totalTime = self.__totalConsumingTime
            self.__createAndPlaySound(self._ACTIVATED_SOUND_ID)
        elif stage == EQUIPMENT_STAGES.PREPARING:
            self._animationType = ANIMATION_TYPES.MOVE_GREEN_BAR_UP | ANIMATION_TYPES.SHOW_COUNTER_GREEN
            if self._prevStage != stage and self._prevStage != EQUIPMENT_STAGES.COOLDOWN:
                self._animationType |= ANIMATION_TYPES.GREEN_GLOW_HIDE
            totalTime = self.__totalRechargingTime
            self.__processReadyStateSounds(timeRemaining)
            if self._prevStage == EQUIPMENT_STAGES.ACTIVE:
                self.__playSoundOnce(self._STOPPED_BY_USER_SOUND_ID)
        elif stage == EQUIPMENT_STAGES.DEPLOYING:
            self._animationType = ANIMATION_TYPES.MOVE_ORANGE_BAR_UP | ANIMATION_TYPES.SHOW_COUNTER_ORANGE
            totalTime = self.__totalDeployingTime
        elif stage == EQUIPMENT_STAGES.COOLDOWN:
            self._animationType = ANIMATION_TYPES.MOVE_ORANGE_BAR_UP | ANIMATION_TYPES.SHOW_COUNTER_ORANGE | ANIMATION_TYPES.FILL_PARTIALLY
            totalTime = self.__totalCooldownTime
            if self._prevStage == EQUIPMENT_STAGES.ACTIVE:
                self.__playSoundOnce(self._EXAUSTED_SOUND_ID)
        elif stage == EQUIPMENT_STAGES.READY and self.becomeReady:
            self.__processReadyStateSounds(timeRemaining)
        self._totalTime = totalTime

    def canActivate(self, entityName=None, avatar=None):
        result, error = False, None
        if self._stage in (EQUIPMENT_STAGES.READY, EQUIPMENT_STAGES.PREPARING, EQUIPMENT_STAGES.ACTIVE):
            result = True
        elif self._stage == EQUIPMENT_STAGES.COOLDOWN:
            error = InCooldownError(self._descriptor.userString)
        elif self._stage == EQUIPMENT_STAGES.DEPLOYING:
            error = NotReadyError(self._descriptor.userString)
        return (result, error)

    def getEntitiesIterator(self, avatar=None):
        return []

    @property
    def becomeReady(self):
        return super(_ReplayAfterburningItem, self).becomeReady

    def _soundUpdate(self, prevQuantity, quantity):
        pass

    def _cleanReadyStageSounds(self):
        self.__cleanFullReadySound()
        self.__cleanAlmostReadySound()

    def _playChargedSound(self):
        EquipmentSound.playReady(self)
        self.__fullyChargedSoundCbId = None
        return

    def _playAlmostChargedSound(self):
        if self.__almostChargedSound is None:
            self.__almostChargedSound = SoundGroups.g_instance.getSound2D(self._ALMOST_CHARGED_SOUND_ID)
        else:
            self.__almostChargedSound.stop()
        self.__almostChargedSound.play()
        self.__almostChargedSoundCbId = None
        return

    def __processReadyStateSounds(self, timeRemaining):
        if timeRemaining > -1:
            self.__cleanFullReadySound()
            self.__fullyChargedSoundCbId = BigWorld.callback(timeRemaining, self._playChargedSound)
            if timeRemaining >= self._FULL_CHARGE_DELAY_SOUND_TIME:
                self.__cleanAlmostReadySound()
                if self.__almostChargedSound is not None:
                    self.__almostChargedSound.stop()
                self.__almostChargedSoundCbId = BigWorld.callback(timeRemaining - self._FULL_CHARGE_DELAY_SOUND_TIME, self._playAlmostChargedSound)
        elif self.becomeReady:
            self.__cleanFullReadySound()
            self._playChargedSound()
        return

    def __cleanAlmostReadySound(self):
        if self.__almostChargedSoundCbId is not None:
            BigWorld.cancelCallback(self.__almostChargedSoundCbId)
            self.__almostChargedSoundCbId = None
        return

    def __cleanFullReadySound(self):
        if self.__fullyChargedSoundCbId is not None:
            BigWorld.cancelCallback(self.__fullyChargedSoundCbId)
            self.__fullyChargedSoundCbId = None
        return

    def __playSoundOnce(self, sound):
        SoundGroups.g_instance.getSound2D(sound)

    def __createAndPlaySound(self, sound):
        self.__playingSoundObj = SoundGroups.g_instance.getSound2D(sound)
        self.__playingSoundObj.play()


class _ReplayLargeRepairKitBattleRoyaleItem(_ReplayItem):
    __slots__ = ('__totalCooldownTime',)

    def __init__(self, descriptor, quantity, stage, timeRemaining, totalTime, tags=None):
        self.__totalCooldownTime = descriptor.cooldownSeconds
        super(_ReplayLargeRepairKitBattleRoyaleItem, self).__init__(descriptor, quantity, stage, timeRemaining, totalTime, tags)

    def update(self, quantity, stage, timeRemaining, totalTime):
        super(_ReplayLargeRepairKitBattleRoyaleItem, self).update(quantity, stage, timeRemaining, totalTime)
        if stage == EQUIPMENT_STAGES.COOLDOWN:
            totalTime = self.__totalCooldownTime
        self._totalTime = totalTime


class _ReplayRegenerationKitBattleRoyaleItem(_ReplayItem):
    __slots__ = ('__totalCooldownTime', '__healTime')

    def __init__(self, descriptor, quantity, stage, timeRemaining, totalTime, tags=None):
        self.__totalCooldownTime = descriptor.cooldownSeconds
        self.__healTime = descriptor.healTime
        super(_ReplayRegenerationKitBattleRoyaleItem, self).__init__(descriptor, quantity, stage, timeRemaining, totalTime, tags)

    def update(self, quantity, stage, timeRemaining, totalTime):
        super(_ReplayRegenerationKitBattleRoyaleItem, self).update(quantity, stage, timeRemaining, totalTime)
        if stage == EQUIPMENT_STAGES.COOLDOWN:
            totalTime = self.__totalCooldownTime
            self._animationType = ANIMATION_TYPES.MOVE_ORANGE_BAR_UP | ANIMATION_TYPES.SHOW_COUNTER_ORANGE | ANIMATION_TYPES.FILL_PARTIALLY
        elif stage == EQUIPMENT_STAGES.ACTIVE:
            totalTime = self.__healTime
            self._animationType = ANIMATION_TYPES.MOVE_GREEN_BAR_DOWN | ANIMATION_TYPES.SHOW_COUNTER_GREEN | ANIMATION_TYPES.FILL_PARTIALLY
        self._totalTime = totalTime


class DynComponentsGroupReplayItem(DynComponentsGroupItem):
    __slots__ = ('__cooldownTime',)

    def __init__(self, descriptor, quantity, stage, timeRemaining, totalTime, tags=None):
        super(DynComponentsGroupReplayItem, self).__init__(descriptor, quantity, stage, timeRemaining, totalTime, tags)
        self.__cooldownTime = BigWorld.serverTime() + timeRemaining

    def update(self, quantity, stage, timeRemaining, totalTime):
        super(DynComponentsGroupReplayItem, self).update(quantity, stage, timeRemaining, totalTime)
        self.__cooldownTime = BigWorld.serverTime() + timeRemaining

    def getReplayTimeRemaining(self):
        return max(0, self.__cooldownTime - BigWorld.serverTime())

    def getCooldownPercents(self):
        totalTime = self.getTotalTime()
        timeRemaining = self.getReplayTimeRemaining()
        return round(float(totalTime - timeRemaining) / totalTime * 100.0) if totalTime > 0 else 0.0


class DynComponentsGroupPassiveReplayItem(_ReplayItem):
    pass


class _ReplayPoiEquipmentItemVS(_ReplayItem, _PoiEquipmentItemVS):

    def _getErrorMsg(self):
        return _PoiEquipmentItemVS._getErrorMsg(self)

    def getAnimationType(self):
        return _PoiEquipmentItemVS.getAnimationType(self)

    def update(self, quantity, stage, timeRemaining, totalTime):
        return _PoiEquipmentItemVS.update(self, quantity, stage, timeRemaining, totalTime)


class _ReplayPoiArtilleryItem(_ReplayItem, _PoiArtilleryItem):

    def _getErrorMsg(self):
        return _PoiArtilleryItem.getErrorMsg(self)

    def canActivate(self, entityName=None, avatar=None):
        return _PoiArtilleryItem.canActivate(entityName, avatar)


class _ReplayRoleSkillVSItem(_ReplayItem, _RoleSkillVSItem):

    def getAnimationType(self):
        return _RoleSkillVSItem.getAnimationType(self)

    def update(self, quantity, stage, timeRemaining, totalTime):
        _ReplayItem.update(self, quantity, stage, timeRemaining, totalTime)
        _RoleSkillVSItem.update(self, quantity, stage, timeRemaining, totalTime)

    def canActivate(self, entityName=None, avatar=None):
        return _RoleSkillVSItem.canActivate(self, entityName, avatar)

    def _getErrorMsg(self):
        return _RoleSkillVSItem._getErrorMsg(self)


class _ReplayRoleSkillArtyVSItem(_ReplayRoleSkillVSItem):

    def getMarker(self):
        pass


def _replayComp7ItemFactory(descriptor, quantity, stage, timeRemaining, totalTime, tag=None):
    if descriptor.name.startswith('comp7_redline'):
        itemClass = _ReplayRoleSkillArtyVSItem
    else:
        itemClass = _ReplayRoleSkillVSItem
    return itemClass(descriptor, quantity, stage, timeRemaining, totalTime, tag)


def _replayPoiItemFactory(descriptor, quantity, stage, timeRemaining, totalTime, tag=None):
    if descriptor.name.startswith('poi_artillery_aoe'):
        itemClass = _ReplayPoiArtilleryItem
    else:
        itemClass = _ReplayPoiEquipmentItemVS
    return itemClass(descriptor, quantity, stage, timeRemaining, totalTime, tag)


def _replayTriggerItemFactory(descriptor, quantity, stage, timeRemaining, totalTime, tags=None):
    if descriptor.name.startswith('arcade_artillery'):
        return _ReplayArcadeArtilleryItem(descriptor, quantity, stage, timeRemaining, totalTime, tags)
    if descriptor.name.startswith('artillery_epic'):
        return _ReplayArcadeArtilleryItem(descriptor, quantity, stage, timeRemaining, totalTime, tags)
    if descriptor.name.startswith('artillery_aoe_fort'):
        return _ReplayArtilleryAOEFort(descriptor, quantity, stage, timeRemaining, totalTime, tags)
    if descriptor.name.startswith('arcade_bomber'):
        return _ReplayBomberItem(descriptor, quantity, stage, timeRemaining, totalTime, tags)
    if descriptor.name.startswith('arcade_minefield'):
        return _ReplayOrderItem(descriptor, quantity, stage, timeRemaining, totalTime, tags)
    if descriptor.name.startswith('artillery'):
        return _ReplayArtilleryItem(descriptor, quantity, stage, timeRemaining, totalTime, tags)
    if descriptor.name.startswith('bomber'):
        return _ReplayBomberItem(descriptor, quantity, stage, timeRemaining, totalTime, tags)
    if descriptor.name.startswith('recon'):
        return _ReplayReconItem(descriptor, quantity, stage, timeRemaining, totalTime, tags)
    if descriptor.name.startswith('smoke'):
        return _ReplaySmokeItem(descriptor, quantity, stage, timeRemaining, totalTime, tags)
    if descriptor.name.startswith('arcade_smoke'):
        return _ReplaySmokeItem(descriptor, quantity, stage, timeRemaining, totalTime, tags)
    if descriptor.name.endswith('afterburning'):
        return _ReplayAfterburningItem(descriptor, quantity, stage, timeRemaining, totalTime, tags)
    if descriptor.name.startswith('large_repairkit_battle_royale'):
        return _ReplayLargeRepairKitBattleRoyaleItem(descriptor, quantity, stage, timeRemaining, totalTime, tags)
    if descriptor.name.startswith('regenerationKit'):
        return _ReplayRegenerationKitBattleRoyaleItem(descriptor, quantity, stage, timeRemaining, totalTime, tags)
    return _ReplayOrderItem(descriptor, quantity, stage, timeRemaining, totalTime, tags) if descriptor.name.startswith('spawn_kamikaze') else _ReplayItem(descriptor, quantity, stage, timeRemaining, totalTime, tags)


_REPLAY_EQUIPMENT_TAG_TO_ITEM = {('fuel',): _ReplayItem,
 ('stimulator',): _ReplayItem,
 ('trigger',): _replayTriggerItemFactory,
 ('extinguisher',): _ReplayItem,
 ('medkit',): _ReplayMedKitItem,
 ('repairkit',): _ReplayRepairKitItem,
 ('regenerationKit',): _replayTriggerItemFactory,
 ('medkit', 'repairkit'): _replayTriggerItemFactory,
 ('dynComponentsGroup',): DynComponentsGroupReplayItem,
 ('dynComponentsGroup', 'passive'): DynComponentsGroupPassiveReplayItem,
 (ROLE_EQUIPMENT_TAG,): _replayComp7ItemFactory,
 (POI_EQUIPMENT_TAG,): _replayPoiItemFactory}

class EquipmentsReplayPlayer(EquipmentsController):
    __slots__ = ('__callbackID', '__callbackTimeID', '__percentGetters', '__percents', '__timeGetters', '__times')

    def __init__(self, setup):
        super(EquipmentsReplayPlayer, self).__init__(setup)
        self.__callbackID = None
        self.__callbackTimeID = None
        self.__percentGetters = {}
        self.__percents = {}
        self.__timeGetters = {}
        self.__times = {}
        return

    def clear(self, leave=True):
        if leave:
            if self.__callbackID is not None:
                BigWorld.cancelCallback(self.__callbackID)
                self.__callbackID = None
            if self.__callbackTimeID is not None:
                BigWorld.cancelCallback(self.__callbackTimeID)
                self.__callbackTimeID = None
            self.__percents.clear()
            self.__percentGetters.clear()
            self.__times.clear()
            self.__timeGetters.clear()
        super(EquipmentsReplayPlayer, self).clear(leave)
        return

    @MethodsRules.delayable('notifyPlayerVehicleSet')
    def setEquipment(self, intCD, quantity, stage, timeRemaining, totalTime, index=0):
        super(EquipmentsReplayPlayer, self).setEquipment(intCD, quantity, stage, timeRemaining, totalTime, index)
        self.__percents.pop(intCD, None)
        self.__percentGetters.pop(intCD, None)
        self.__times.pop(intCD, None)
        self.__timeGetters.pop(intCD, None)
        if stage in (EQUIPMENT_STAGES.DEPLOYING,
         EQUIPMENT_STAGES.COOLDOWN,
         EQUIPMENT_STAGES.SHARED_COOLDOWN,
         EQUIPMENT_STAGES.ACTIVE) or stage == EQUIPMENT_STAGES.READY and self.getEquipment(intCD).getTimeRemaining():
            equipment = self._equipments[intCD]
            self.__percentGetters[intCD] = equipment.getCooldownPercents
            if self.__callbackID is not None:
                BigWorld.cancelCallback(self.__callbackID)
                self.__callbackID = None
            if equipment.getTotalTime() > 0:
                self.__timeGetters[intCD] = equipment.getReplayTimeRemaining
                if self.__callbackTimeID is not None:
                    BigWorld.cancelCallback(self.__callbackTimeID)
                    self.__callbackTimeID = None
            self.__timeLoop()
            self.__timeLoopInSeconds()
        return

    @classmethod
    def createItem(cls, descriptor, quantity, stage, timeRemaining, totalTime):
        item = cls._findExtendItem(True, descriptor.name, descriptor, quantity, stage, timeRemaining, totalTime)
        if item:
            return item
        tags, clazz = _getInitialTagsAndClass(descriptor, _REPLAY_EQUIPMENT_TAG_TO_ITEM)
        if tags:
            item = clazz(descriptor, quantity, stage, timeRemaining, totalTime, tags)
        else:
            item = _ReplayItem(descriptor, quantity, stage, timeRemaining, totalTime, tags)
        return item

    def getActivationCode(self, intCD, entityName=None, avatar=None):
        return None

    def canActivate(self, intCD, entityName=None, avatar=None):
        return (False, None)

    def changeSetting(self, intCD, entityName=None, avatar=None, idx=None):
        return (False, None)

    def changeSettingByTag(self, tag, entityName=None, avatar=None):
        return (False, None)

    def __timeLoop(self):
        self.__callbackID = None
        self.__tick()
        self.__callbackID = BigWorld.callback(0.1, self.__timeLoop)
        return

    def __timeLoopInSeconds(self):
        self.__callbackTimeID = None
        self.__tickInSeconds()
        self.__callbackTimeID = BigWorld.callback(1, self.__timeLoopInSeconds)
        return

    def __tick(self):
        for intCD, percentGetter in self.__percentGetters.iteritems():
            percent = percentGetter()
            currentPercent = self.__percents.get(intCD)
            if currentPercent != percent:
                self.__percents[intCD] = percent
                self.onEquipmentCooldownInPercent(intCD, percent)

    def __tickInSeconds(self):
        for intCD, timeGetter in self.__timeGetters.iteritems():
            time = timeGetter()
            currentTime = self.__times.get(intCD)
            if currentTime != time:
                isBaseTime = False
                if self._equipments.has_key(intCD):
                    isBaseTime = self._equipments[intCD].getStage() == EQUIPMENT_STAGES.ACTIVE
                self.__times[intCD] = time
                self.onEquipmentCooldownTime(intCD, time, isBaseTime, time == 0)


__all__ = ('EquipmentsController', 'EquipmentsReplayPlayer')
