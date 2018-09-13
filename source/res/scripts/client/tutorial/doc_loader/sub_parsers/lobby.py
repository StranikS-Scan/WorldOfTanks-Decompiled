# Embedded file name: scripts/client/tutorial/doc_loader/sub_parsers/lobby.py
from helpers.html import translation
from items import _xml
from tutorial.control.lobby import triggers
from tutorial.data import chapter
from tutorial.doc_loader import sub_parsers

def _readCloseHintSection(xmlCtx, section, _, conditions):
    hintID = sub_parsers._parseID(xmlCtx, section, 'Specify a hint ID')
    return chapter.HasTargetEffect(hintID, chapter.Effect.CLOSE_HINT, conditions=conditions)


def _readSetFilterSection(xmlCtx, section, _, conditions):
    filterID = sub_parsers._parseID(xmlCtx, section, 'Specify a filter ID')
    value = []
    for name, subSec in _xml.getChildren(xmlCtx, section, 'value'):
        value.append(sub_parsers._readVarValue(name, subSec))

    return chapter.SetFilter(filterID, tuple(value), conditions=conditions)


def _readBonusTriggerSection(xmlCtx, section, chapter, triggerID):
    return triggers.BonusTrigger(triggerID, chapter.getBonusID())


def _readBattleCountTriggerSection(xmlCtx, section, chapter, triggerID):
    return sub_parsers._readValidateVarTriggerSection(xmlCtx, section, triggerID, triggers.BattleCountRequester)


def _readItemUnlockedTriggerSection(xmlCtx, section, _, triggerID):
    return sub_parsers._readValidateVarTriggerSection(xmlCtx, section, triggerID, triggers.ItemUnlockedTrigger, validateUpdateOnly='validate-update-only' in section.keys())


def _readItemInstalledTriggerSection(xmlCtx, section, chapter, triggerID):
    return sub_parsers._readValidateVarTriggerSection(xmlCtx, section, triggerID, triggers.ItemInstalledTrigger)


def _readVehicleSettingTriggerSection(xmlCtx, section, chapter, triggerID):
    return sub_parsers._readValidateVarTriggerSection(xmlCtx, section, triggerID, triggers.VehicleSettingTrigger)


def _readEliteVehicleTriggerSection(xmlCtx, section, chapter, triggerID):
    return sub_parsers._readValidateVarTriggerSection(xmlCtx, section, triggerID, triggers.EliteVehicleTrigger)


def _readAccountCreditsTriggerSection(xmlCtx, section, chapter, triggerID):
    return sub_parsers._readValidateVarTriggerSection(xmlCtx, section, triggerID, triggers.AccountCreditsTrigger)


def _readItemPriceTriggerSection(xmlCtx, section, chapter, triggerID):
    return sub_parsers._readValidateVarTriggerSection(xmlCtx, section, triggerID, triggers.ItemPriceTrigger)


def _readEqInstalledTriggerSection(xmlCtx, section, chapter, triggerID):
    return sub_parsers._readValidateVarTriggerSection(xmlCtx, section, triggerID, triggers.EquipmentInstalledTrigger)


def _readInventoryItemTriggerSection(xmlCtx, section, _, triggerID):
    itemTypeID = _xml.readInt(xmlCtx, section, 'item-type-id')
    return sub_parsers._readValidateVarTriggerSection(xmlCtx, section, triggerID, triggers.InventoryItemTrigger, itemTypeID=itemTypeID)


def _readCurrentVehicleTriggerSection(xmlCtx, section, _, triggerID):
    isLockedFlagID = section.readString('locked')
    if not len(isLockedFlagID):
        isLockedFlagID = None
    isCrewFullFlagID = section.readString('crew-full')
    if not len(isCrewFullFlagID):
        isCrewFullFlagID = None
    return sub_parsers._readValidateVarTriggerSection(xmlCtx, section, triggerID, triggers.CurrentVehicleTrigger, isLockedFlagID=isLockedFlagID, isCrewFullFlagID=isCrewFullFlagID)


def _readCurVehicleCrewTriggerSection(xmlCtx, section, chapter, triggerID):
    return triggers.CurVehicleCrewTrigger(triggerID)


def _readCurVehicleLockedTriggerSection(xmlCtx, section, chapter, triggerID):
    return triggers.CurVehicleLockedTrigger(triggerID)


def _readItemXPTriggerSection(xmlCtx, section, _, triggerID):
    vehicleVarID = _xml.readString(xmlCtx, section, 'vehicle-var')
    return sub_parsers._readValidateVarTriggerSection(xmlCtx, section, triggerID, triggers.ItemExperienceTrigger, vehicleVarID=vehicleVarID)


def _readTankmanLevelTriggerSection(xmlCtx, section, _, triggerID):
    role = _xml.readString(xmlCtx, section, 'role')
    roleLevel = _xml.readInt(xmlCtx, section, 'role-level')
    inVehicleFlagID = _xml.readString(xmlCtx, section, 'in-vehicle')
    specVehicleFlagID = section.readString('spec-vehicle')
    if not len(specVehicleFlagID):
        specVehicleFlagID = None
    setVarID = section.readString('set-var')
    if not len(setVarID):
        setVarID = None
    return triggers.TankmanLevelTrigger(triggerID, role, roleLevel, setVarID, inVehicleFlagID, specVehicleFlagID)


def _readTankmanSkillTriggerSection(xmlCtx, section, chapter, triggerID):
    return sub_parsers._readValidateVarTriggerSection(xmlCtx, section, triggerID, triggers.TankmanSkillTrigger)


def _readFreeVehicleSlotTriggerSection(xmlCtx, section, chapter, triggerID):
    return triggers.FreeVehicleSlotTrigger(triggerID)


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
    return chapter.VarRefPopUp(dialogID, type, content, _xml.readString(xmlCtx, section, 'var-ref'))


def _parseHint(xmlCtx, section, _):
    hintID = sub_parsers._parseID(xmlCtx, section, 'Specify a hint ID')
    targetID = _xml.readString(xmlCtx, section, 'gui-item-ref')
    containerID = section.readString('container-ref')
    if not len(containerID):
        containerID = None
    text = translation(_xml.readString(xmlCtx, section, 'text'))
    inPin = _xml.readString(xmlCtx, section, 'inPin')
    outPin = _xml.readString(xmlCtx, section, 'outPin')
    line = _xml.readString(xmlCtx, section, 'line')
    position = section.readVector2('position')
    topmostLevel = section.readBool('topmost-level', True)
    return chapter.ItemHint(hintID, targetID, containerID, position, text, inPin, outPin, line, topmostLevel)


def _parseChapterInfoCondition(xmlCtx, section, _):
    conditionID = sub_parsers._parseID(xmlCtx, section, 'Specify a charter info ID')
    return chapter.HasIDConditions(sub_parsers._parseID(xmlCtx, section, 'Specify a charter info condition ID'), sub_parsers._readConditions(xmlCtx, section, []))


def init():
    sub_parsers.setEffectsParsers({'close-hint': _readCloseHintSection,
     'set-filter': _readSetFilterSection})
    sub_parsers.setTriggersParsers({'bonus': _readBonusTriggerSection,
     'battleCount': _readBattleCountTriggerSection,
     'unlocked': _readItemUnlockedTriggerSection,
     'installed': _readItemInstalledTriggerSection,
     'vehicleSetting': _readVehicleSettingTriggerSection,
     'eliteVehicle': _readEliteVehicleTriggerSection,
     'accCredits': _readAccountCreditsTriggerSection,
     'itemPrice': _readItemPriceTriggerSection,
     'eqInstalled': _readEqInstalledTriggerSection,
     'inventory': _readInventoryItemTriggerSection,
     'currentVehicle': _readCurrentVehicleTriggerSection,
     'cVehCrew': _readCurVehicleCrewTriggerSection,
     'cVehLocked': _readCurVehicleLockedTriggerSection,
     'itemXP': _readItemXPTriggerSection,
     'tankmanLevel': _readTankmanLevelTriggerSection,
     'tankmanSkill': _readTankmanSkillTriggerSection,
     'freeVehSlot': _readFreeVehicleSlotTriggerSection})
    sub_parsers.setDialogsParsers({'greeting': _readGreetingDialogSection,
     'quest': _readQuestDialogSection,
     'subQuest': _readSubQuestDialogSection,
     'questAndHelp': _readQuestAndHelpDialogSection,
     'questCompleted': _readQuestCompletedDialogSection,
     'finished': _readQuestCompletedDialogSection,
     'vehicleItemInfo': _readVarRefDialogSection,
     'tankmanSkill': _readVarRefDialogSection})
    sub_parsers.setEntitiesParsers({'hint': _parseHint,
     'cinfo-condition': _parseChapterInfoCondition})
