# Embedded file name: scripts/client/tutorial/doc_loader/sub_parsers/chains.py
from items import _xml
from tutorial.control.chains import triggers
from tutorial.data import chapter, effects
from tutorial.doc_loader import sub_parsers
from tutorial.doc_loader.sub_parsers import lobby

def readHintSection(xmlCtx, section, flags):
    sectionInfo = sub_parsers.parseHint(xmlCtx, section)
    hint = chapter.ChainHint(sectionInfo['hintID'], sectionInfo['itemID'], sectionInfo['text'], sectionInfo['hasBox'], sectionInfo['arrow'], sectionInfo['padding'])
    hint.setActions(sub_parsers.parseActions(xmlCtx, _xml.getSubsection(xmlCtx, section, 'actions'), flags))
    return hint


def readFightBtnDisableTriggerSection(xmlCtx, section, _, triggerID):
    return triggers.FightButtonDisabledTrigger(triggerID)


def _readSwitchToRandomSection(xmlCtx, section, flags, conditions):
    return effects.SimpleEffect(effects.EFFECT_TYPE.ENTER_QUEUE, conditions=conditions)


def readShowUnlockedChapterSection(xmlCtx, section, flags, conditions):
    targetID = section.asString
    return effects.HasTargetEffect(targetID, effects.EFFECT_TYPE.SHOW_UNLOCKED_CHAPTER, conditions=conditions)


def _readSimpleDialogTriggerSection(xmlCtx, section, chapter, triggerID):
    return triggers.SimpleDialogTrigger(triggerID)


def _readBuyNextLevelVehicleTriggerSection(xmlCtx, section, _, triggerID):
    return sub_parsers.readValidateVarTriggerSection(xmlCtx, section, triggerID, triggers.BuyNextLevelVehicleTrigger, validateUpdateOnly='validate-update-only' in section.keys())


def _readVehicleRequiredLevelTriggerSection(xmlCtx, section, _, triggerID):
    return sub_parsers.readValidateVarTriggerSection(xmlCtx, section, triggerID, triggers.CurrentVehicleRequiredLevelTrigger, validateUpdateOnly='validate-update-only' in section.keys())


def readTankmanPriceDiscountTriggerSection(xmlCtx, section, _, triggerID):
    return sub_parsers.readValidateVarTriggerSection(xmlCtx, section, triggerID, triggers.TankmanPriceDiscountTrigger, validateUpdateOnly='validate-update-only' in section.keys())


def _readRentedVehiclesTriggerSection(xmlCtx, section, _, triggerID):
    return triggers.RentedVehicleTrigger(triggerID)


def _readMaintenanceStateTrigger(xmlCtx, section, _, triggerID):
    return triggers.CurrentVehicleMaintenanceStateTrigger(triggerID)


def _readNeedChangeCurrentVehicleTrigger(xmlCtx, section, _, triggerID):
    return triggers.CurrentVehicleNeedChangeTrigger(triggerID)


def _readOptionalDevicesStateTrigger(xmlCtx, section, _, triggerID):
    return triggers.CurrentVehicleOptionalDevicesStateTrigger(triggerID)


def _readLockedStateTrigger(xmlCtx, section, _, triggerID):
    return triggers.CurrentVehicleLockedTrigger(triggerID)


def readIsInSandBoxPreQueueTriggerSection(xmlCtx, section, chapter, triggerID):
    return triggers.IsInSandBoxPreQueueTrigger(triggerID)


def readIsInSandBoxOrRandomPreQueueTriggerSection(xmlCtx, section, chapter, triggerID):
    return triggers.IsInSandBoxOrRandomPreQueueTrigger(triggerID)


def readQueueTrigger(xmlCtx, section, _, triggerID):
    return triggers.QueueTrigger(triggerID)


def init():
    sub_parsers.setEntitiesParsers({'hint': readHintSection})
    sub_parsers.setEffectsParsers({'switch-to-random': _readSwitchToRandomSection,
     'show-unlocked-chapter': readShowUnlockedChapterSection})
    sub_parsers.setTriggersParsers({'simpleDialog': _readSimpleDialogTriggerSection,
     'unlocked': lobby.readItemUnlockedTriggerSection,
     'inventory': lobby.readInventoryItemTriggerSection,
     'installed': lobby.readItemInstalledTriggerSection,
     'eqInstalled': lobby.readEquipmentInstalledTriggerSection,
     'freeSlot': lobby.readFreeVehicleSlotTriggerSection,
     'currentVehicle': lobby.readCurrentVehicleChangedTriggerSection,
     'premiumDiscount': lobby.readPremiumDiscountsUseTriggerSection,
     'freeXP': lobby.readFreeXPChangedTriggerSection,
     'bonus': lobby.readBonusTriggerSection,
     'buyNextLevelVehicle': _readBuyNextLevelVehicleTriggerSection,
     'vehicleRequiredLevel': _readVehicleRequiredLevelTriggerSection,
     'tankmanDiscount': readTankmanPriceDiscountTriggerSection,
     'rentedVehicles': _readRentedVehiclesTriggerSection,
     'maintenanceState': _readMaintenanceStateTrigger,
     'optionalDevicesState': _readOptionalDevicesStateTrigger,
     'lockedState': _readLockedStateTrigger,
     'isInSandbox': readIsInSandBoxPreQueueTriggerSection,
     'isInSandboxOrRandom': readIsInSandBoxOrRandomPreQueueTriggerSection,
     'fightBtn': readFightBtnDisableTriggerSection,
     'needChangeCurrentVehicle': _readNeedChangeCurrentVehicleTrigger})
    sub_parsers.setWindowsParsers({'awardWindow': sub_parsers.readQuestAwardWindowSection})
