# Embedded file name: scripts/client/tutorial/doc_loader/sub_parsers/chains.py
from collections import namedtuple
from helpers.html import translation
from items import _xml
from tutorial.control.chains import triggers
from tutorial.data import chapter, effects
from tutorial.doc_loader import sub_parsers
from tutorial.doc_loader.sub_parsers import lobby
_AVAILABLE_DIRECTIONS = ('L', 'T', 'R', 'B')
_ArrowProps = namedtuple('_ArrowProps', ('direction', 'loop'))
_Padding = namedtuple('_Padding', ('left', 'top', 'right', 'bottom'))

def _readHintSection(xmlCtx, section, flags):
    hintID = sub_parsers.parseID(xmlCtx, section, 'Specify a hint ID')
    if 'item-id' in section.keys():
        itemID = sub_parsers.parseID(xmlCtx, section['item-id'], 'Specify a item ID')
    else:
        _xml.raiseWrongXml(xmlCtx, section.name, 'Specify a item ID')
        return
    tags = section.keys()
    text = translation(_xml.readString(xmlCtx, section, 'text'))
    if 'arrow' in tags:
        subSec = section['arrow']
        direction = _xml.readString(xmlCtx, subSec, 'direction')
        if direction not in _AVAILABLE_DIRECTIONS:
            _xml.raiseWrongXml(xmlCtx, section, 'Arrow direction {} is invalid.'.format(direction))
        arrow = _ArrowProps(direction, _xml.readBool(xmlCtx, subSec, 'loop'))
    else:
        arrow = None
    if 'padding' in tags:
        subSec = section['padding']
        padding = _Padding(_xml.readFloat(xmlCtx, subSec, 'left'), _xml.readFloat(xmlCtx, subSec, 'top'), _xml.readFloat(xmlCtx, subSec, 'right'), _xml.readFloat(xmlCtx, subSec, 'bottom'))
    else:
        padding = None
    hint = chapter.ChainHint(hintID, itemID, text, section.readBool('has-box', True), arrow, padding)
    hint.setActions(sub_parsers.parseActions(xmlCtx, _xml.getSubsection(xmlCtx, section, 'actions'), flags))
    return hint


def _readSwitchToRandomSection(xmlCtx, section, flags, conditions):
    return effects.SimpleEffect(effects.EFFECT_TYPE.ENTER_QUEUE, conditions=conditions)


def _readSimpleDialogTriggerSection(xmlCtx, section, chapter, triggerID):
    return triggers.SimpleDialogTrigger(triggerID)


def _readBuyNextLevelVehicleTriggerSection(xmlCtx, section, _, triggerID):
    return sub_parsers.readValidateVarTriggerSection(xmlCtx, section, triggerID, triggers.BuyNextLevelVehicleTrigger, validateUpdateOnly='validate-update-only' in section.keys())


def _readVehicleRequiredLevelTriggerSection(xmlCtx, section, _, triggerID):
    return sub_parsers.readValidateVarTriggerSection(xmlCtx, section, triggerID, triggers.CurrentVehicleRequiredLevelTrigger, validateUpdateOnly='validate-update-only' in section.keys())


def _readTankmanPriceDiscountTriggerSection(xmlCtx, section, _, triggerID):
    return sub_parsers.readValidateVarTriggerSection(xmlCtx, section, triggerID, triggers.TankmanPriceDiscountTrigger, validateUpdateOnly='validate-update-only' in section.keys())


def _readPremiumVehiclesTriggerSection(xmlCtx, section, _, triggerID):
    return triggers.CurrentPremiumVehicleTrigger(triggerID)


def _readMaintenanceStateTrigger(xmlCtx, section, _, triggerID):
    return triggers.CurrentVehicleMaintenanceStateTrigger(triggerID)


def _readOptionalDevicesStateTrigger(xmlCtx, section, _, triggerID):
    return triggers.CurrentVehicleOptionalDevicesStateTrigger(triggerID)


def _readLockedStateTrigger(xmlCtx, section, _, triggerID):
    return triggers.CurrentVehicleLockedTrigger(triggerID)


def readQueueTrigger(xmlCtx, section, _, triggerID):
    return triggers.QueueTrigger(triggerID)


def init():
    sub_parsers.setEntitiesParsers({'hint': _readHintSection})
    sub_parsers.setEffectsParsers({'switch-to-random': _readSwitchToRandomSection})
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
     'tankmanDiscount': _readTankmanPriceDiscountTriggerSection,
     'premiumVehicles': _readPremiumVehiclesTriggerSection,
     'maintenanceState': _readMaintenanceStateTrigger,
     'optionalDevicesState': _readOptionalDevicesStateTrigger,
     'lockedState': _readLockedStateTrigger})
    sub_parsers.setWindowsParsers({'awardWindow': sub_parsers.readQuestAwardWindowSection})
