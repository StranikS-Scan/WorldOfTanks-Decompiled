# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/tank_setup_sounds.py
import SoundGroups
import WWISE
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_setup_model import BaseSetupModel
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from helpers import dependency
from shared_utils import CONST_CONTAINER, first
from skeletons.gui.shared import IItemsCache

class TankSetupSoundEvents(CONST_CONTAINER):
    STATE_PLACE = 'STATE_hangar_place'
    STATE_PLACE_ENTER = 'STATE_hangar_place_consumables'
    STATE_PLACE_GARAGE = 'STATE_hangar_place_garage'
    VIEW_ENTER = 'cons_enter'
    VIEW_EXIT = 'cons_exit'
    SELECT_VIEW = 'cons_select_view'
    ACCEPT = 'cons_accept'
    EQUIPMENT_SLOT_PREFIX = 'cons_equipment_slot_'
    EQUIPMENT_MOUNT = 'cons_equipment_mount'
    EQUIPMENT_DEMOUNT = 'cons_equipment_demount'
    EQUIPMENT_DEMOUNT_KIT = 'cons_equipment_demount_kit'
    EQUIPMENT_DESTROY = 'cons_equipment_destroy'
    EQUIPMENT_SWAP = 'cons_equipment_swipe'
    EQUIPMENT_BONUS = 'cons_equipment_bonus'
    CONSUMABLES_MOUNT = 'cons_consumables_mount'
    CONSUMABLES_DEMOUNT = 'cons_consumables_demount'
    INSTRUCTIONS_MOUNT = 'cons_instructions_mount'
    INSTRUCTIONS_DEMOUNT = 'cons_instructions_demount'
    INSTRUCTIONS_EQUIP_NOT_SUITABLE = 'cons_instructions_equip_not_suitable'
    RTPC_SHELLS_PROGRESS_BAR = 'RTPC_ext_ammo_progress_bar'
    AMMO_SINGLE_PLUS = 'cons_ammo_single_plus'
    AMMO_SINGLE_MINUS = 'cons_ammo_single_minus'


def playEnterTankSetupView():
    WWISE.WW_setState(TankSetupSoundEvents.STATE_PLACE, TankSetupSoundEvents.STATE_PLACE_ENTER)
    playSound(TankSetupSoundEvents.VIEW_ENTER)


def playExitTankSetupView():
    WWISE.WW_setState(TankSetupSoundEvents.STATE_PLACE, TankSetupSoundEvents.STATE_PLACE_GARAGE)
    playSound(TankSetupSoundEvents.VIEW_EXIT)


def playOptDeviceSlotEnter(vehicle, slotID):
    category = first(vehicle.optDevices.slots[slotID].categories)
    if category is None:
        return
    else:
        soundName = TankSetupSoundEvents.EQUIPMENT_SLOT_PREFIX + category
        playSound(soundName)
        return


def playSound(eventName):
    if eventName:
        SoundGroups.g_instance.playSound2D(eventName)


def playSectionSelectSound():
    playSound(TankSetupSoundEvents.SELECT_VIEW)


def playSlotActionSound(setupName, *args, **kwargs):
    if setupName == TankSetupConstants.CONSUMABLES or setupName == TankSetupConstants.BATTLE_ABILITIES:
        ConsumableActionSoundHelper.playActionSound(*args, **kwargs)
    elif setupName == TankSetupConstants.BATTLE_BOOSTERS:
        BattleBoostersActionSoundHelper.playActionSound(*args, **kwargs)
    else:
        if setupName == TankSetupConstants.OPT_DEVICES:
            return OptDeviceActionSound.playActionSound(*args, **kwargs)
        ActionSoundHelper.playActionSound(*args, **kwargs)


class ActionSoundHelper(object):
    _itemsCache = dependency.descriptor(IItemsCache)

    @classmethod
    def playActionSound(cls, actionType, vehicle, intCD=-1, leftIntCD=-1, rightIntCD=-1):
        if actionType == BaseSetupModel.SELECT_SLOT_ACTION:
            cls.playSelectSound(vehicle, intCD)
        elif actionType == BaseSetupModel.REVERT_SLOT_ACTION:
            cls.playRevertSound(vehicle)
        elif actionType == BaseSetupModel.SWAP_SLOTS_ACTION:
            cls.playSwapSound(vehicle, leftIntCD, rightIntCD)
        elif actionType == BaseSetupModel.DEMOUNT_SLOT_ACTION:
            cls.playDemountSound(vehicle, intCD)
        elif actionType == BaseSetupModel.DRAG_AND_DROP_SLOT_ACTION:
            cls.playDragAndDropSound(vehicle, leftIntCD, rightIntCD)
        elif actionType == BaseSetupModel.DESTROY_SLOT_ACTION:
            cls.playDestroySound(vehicle, intCD)

    @classmethod
    def playSelectSound(cls, vehicle, intCD):
        playSound(TankSetupSoundEvents.EQUIPMENT_MOUNT)

    @classmethod
    def playRevertSound(cls, vehicle):
        playSound(TankSetupSoundEvents.EQUIPMENT_DEMOUNT)

    @classmethod
    def playDemountSound(cls, vehicle, intCD):
        playSound(TankSetupSoundEvents.EQUIPMENT_DEMOUNT_KIT)

    @classmethod
    def playDestroySound(cls, vehicle, intCD):
        playSound(TankSetupSoundEvents.EQUIPMENT_DESTROY)

    @classmethod
    def playSwapSound(cls, vehicle, leftIntCD, rightIntCD):
        playSound(TankSetupSoundEvents.EQUIPMENT_SWAP)

    @classmethod
    def playDragAndDropSound(cls, vehicle, leftIntCD, rightIntCD):
        pass


class ConsumableActionSoundHelper(ActionSoundHelper):

    @classmethod
    def playSelectSound(cls, vehicle, intCD):
        playSound(TankSetupSoundEvents.CONSUMABLES_MOUNT)

    @classmethod
    def playRevertSound(cls, vehicle):
        playSound(TankSetupSoundEvents.CONSUMABLES_DEMOUNT)


class OptDeviceActionSound(ActionSoundHelper):

    @classmethod
    def playSelectSound(cls, vehicle, intCD):
        playSound(TankSetupSoundEvents.EQUIPMENT_MOUNT)
        if cls._isCategoryMatch(vehicle, intCD):
            playSound(TankSetupSoundEvents.EQUIPMENT_BONUS)

    @classmethod
    def playSwapSound(cls, vehicle, leftIntCD, rightIntCD):
        playSound(TankSetupSoundEvents.EQUIPMENT_SWAP)
        if cls._isCategoryMatch(vehicle, leftIntCD) or cls._isCategoryMatch(vehicle, rightIntCD):
            playSound(TankSetupSoundEvents.EQUIPMENT_BONUS)

    @classmethod
    def playDragAndDropSound(cls, vehicle, leftIntCD, rightIntCD):
        if cls._isCategoryMatch(vehicle, leftIntCD) or cls._isCategoryMatch(vehicle, rightIntCD):
            playSound(TankSetupSoundEvents.EQUIPMENT_BONUS)

    @classmethod
    def _isCategoryMatch(cls, vehicle, intCD):
        intCDs = vehicle.optDevices.layout.getIntCDs(default=None)
        if intCD in intCDs:
            slotID = intCDs.index(intCD)
            vehCategories = vehicle.optDevices.slots[slotID].categories
            itemCategories = vehicle.optDevices.layout[slotID].descriptor.categories
            return bool(vehCategories & itemCategories)
        else:
            return False


class BattleBoostersActionSoundHelper(ActionSoundHelper):
    _CREW_BOOSTER_SOUND = {'smoothTurretBattleBooster': 'cons_instructions_steady_hand',
     'lastEffortBattleBooster': 'cons_instructions_duty_first',
     'virtuosoBattleBooster': 'cons_instructions_combat_course',
     'pedantBattleBooster': 'cons_instructions_shell_organizer',
     'smoothDrivingBattleBooster': 'cons_instructions_gearbox_intricacy',
     'fireFightingBattleBooster': 'cons_instructions_firefighters',
     'rancorousBattleBooster': 'cons_instructions_focus_target',
     'sixthSenseBattleBooster': 'cons_instructions_increased_focus',
     'camouflageBattleBooster': 'cons_instructions_natural_cover'}

    @classmethod
    def playSelectSound(cls, vehicle, intCD):
        item = cls._itemsCache.items.getItemByCD(intCD)
        if item.isCrewBooster():
            cls._playCrewBoosterSelectSound(vehicle, item)
        else:
            cls._playOptDeviceBoosterSelectSound(vehicle, item)
        playSound(TankSetupSoundEvents.INSTRUCTIONS_MOUNT)

    @classmethod
    def playRevertSound(cls, vehicle):
        playSound(TankSetupSoundEvents.INSTRUCTIONS_DEMOUNT)

    @classmethod
    def _playCrewBoosterSelectSound(cls, vehicle, item):
        soundName = cls._CREW_BOOSTER_SOUND.get(item.name)
        if soundName:
            playSound(soundName)

    @classmethod
    def _playOptDeviceBoosterSelectSound(cls, vehicle, item):
        if not item.isAffectsOnVehicle(vehicle):
            playSound(TankSetupSoundEvents.INSTRUCTIONS_EQUIP_NOT_SUITABLE)
