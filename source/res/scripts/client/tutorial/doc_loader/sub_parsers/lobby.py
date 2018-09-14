# Embedded file name: scripts/client/tutorial/doc_loader/sub_parsers/lobby.py
from helpers.html import translation
from items import _xml
from tutorial.control.lobby import triggers
from tutorial.data import chapter
from tutorial.doc_loader import sub_parsers

def readBonusTriggerSection(xmlCtx, section, chapter, triggerID):
    return triggers.BonusTrigger(triggerID, chapter.getBonusID())


def readBattleCountTriggerSection(xmlCtx, section, _, triggerID):
    return sub_parsers.readValidateVarTriggerSection(xmlCtx, section, triggerID, triggers.BattleCountRequester)


def readItemUnlockedTriggerSection(xmlCtx, section, _, triggerID):
    return sub_parsers.readValidateVarTriggerSection(xmlCtx, section, triggerID, triggers.ItemUnlockedTrigger, validateUpdateOnly='validate-update-only' in section.keys())


def _readVehicleItemsChangedTrigger(xmlCtx, section, triggerID, clazz):
    validateVarID = _xml.readString(xmlCtx, section, 'validate-var')
    vehicleVarID = _xml.readString(xmlCtx, section, 'vehicle-var')
    validateUpdateOnly = 'validate-update-only' in section.keys()
    return clazz(triggerID, validateVarID, vehicleVarID, validateUpdateOnly=validateUpdateOnly)


def readInventoryItemTriggerSection(xmlCtx, section, _, triggerID):
    return _readVehicleItemsChangedTrigger(xmlCtx, section, triggerID, triggers.ItemInInventoryTrigger)


def readItemInstalledTriggerSection(xmlCtx, section, _, triggerID):
    return _readVehicleItemsChangedTrigger(xmlCtx, section, triggerID, triggers.ItemInstalledTrigger)


def readEquipmentInstalledTriggerSection(xmlCtx, section, _, triggerID):
    return _readVehicleItemsChangedTrigger(xmlCtx, section, triggerID, triggers.EquipmentInstalledTrigger)


def readFreeVehicleSlotTriggerSection(xmlCtx, section, chapter, triggerID):
    return triggers.FreeVehicleSlotChangedTrigger(triggerID)


def readCurrentVehicleChangedTriggerSection(xmlCtx, section, chapter, triggerID):
    return triggers.CurrentVehicleChangedTrigger(triggerID)


def readPremiumPeriodChangedTriggerSection(xmlCtx, section, chapter, triggerID):
    return triggers.PremiumPeriodChangedTrigger(triggerID)


def readPremiumDiscountsUseTriggerSection(xmlCtx, section, chapter, triggerID):
    return triggers.PremiumDiscountUseTrigger(triggerID)


def readFreeXPChangedTriggerSection(xmlCtx, section, chapter, triggerID):
    return triggers.FreeXPChangedTrigger(triggerID)


def _readBonusSection(xmlCtx, section, content):
    bonusSec = _xml.getSubsection(xmlCtx, section, 'bonus')
    content['bonusValue'] = translation(_xml.readString(xmlCtx, bonusSec, 'value'))
    content['bonusLabel'] = translation(_xml.readString(xmlCtx, bonusSec, 'label'))
    content['bonusImageUrl'] = _xml.readString(xmlCtx, bonusSec, 'background')
    return content


def _readGreetingDialogSection(xmlCtx, section, _, dialogID, type, content):
    content = _readBonusSection(xmlCtx, section, content)
    return chapter.PopUp(dialogID, type, content)


def _readQuestDialogSection(xmlCtx, section, _, dialogID, type, content):
    content = _readBonusSection(xmlCtx, section, content)
    content['questText'] = translation(_xml.readString(xmlCtx, section, 'quest'))
    return chapter.PopUp(dialogID, type, content)


def _readSubQuestDialogSection(xmlCtx, section, _, dialogID, type, content):
    content['questText'] = translation(_xml.readString(xmlCtx, section, 'quest'))
    return chapter.PopUp(dialogID, type, content)


def _readQuestAndHelpDialogSection(xmlCtx, section, _, dialogID, type, content):
    content = _readBonusSection(xmlCtx, section, content)
    content['questText'] = translation(_xml.readString(xmlCtx, section, 'quest'))
    content['helpSource'] = _xml.readString(xmlCtx, section, 'help')
    return chapter.PopUp(dialogID, type, content)


def _readQuestCompletedDialogSection(xmlCtx, section, _, dialogID, type, content):
    content = _readBonusSection(xmlCtx, section, content)
    content['hintText'] = translation(_xml.readString(xmlCtx, section, 'hint'))
    content['submitLabel'] = translation(_xml.readString(xmlCtx, section, 'submit-label'))
    return chapter.PopUp(dialogID, type, content)


def _readVarRefDialogSection(xmlCtx, section, _, dialogID, type, content):
    return chapter.PopUp(dialogID, type, content, _xml.readString(xmlCtx, section, 'var-ref'))


def init():
    sub_parsers.setTriggersParsers({'bonus': readBonusTriggerSection,
     'battleCount': readBattleCountTriggerSection,
     'unlocked': readItemUnlockedTriggerSection,
     'inventory': readInventoryItemTriggerSection,
     'installed': readItemInstalledTriggerSection,
     'eqInstalled': readEquipmentInstalledTriggerSection,
     'freeSlot': readFreeVehicleSlotTriggerSection,
     'currentVehicle': readCurrentVehicleChangedTriggerSection,
     'premium': readPremiumPeriodChangedTriggerSection,
     'freeXP': readFreeXPChangedTriggerSection})
    sub_parsers.setDialogsParsers({'greeting': _readGreetingDialogSection,
     'quest': _readQuestDialogSection,
     'subQuest': _readSubQuestDialogSection,
     'questAndHelp': _readQuestAndHelpDialogSection,
     'questCompleted': _readQuestCompletedDialogSection,
     'finished': _readQuestCompletedDialogSection,
     'vehicleItemInfo': _readVarRefDialogSection,
     'tankmanSkill': _readVarRefDialogSection})
