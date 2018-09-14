# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/doc_loader/sub_parsers/quests.py
from items import _xml
from tutorial.control.quests import triggers
from tutorial.data import chapter
from tutorial.data import effects
from tutorial.doc_loader import sub_parsers
from tutorial.doc_loader.sub_parsers import chains, readVarValue
from tutorial.doc_loader.sub_parsers import lobby
_EFFECT_TYPE = effects.EFFECT_TYPE

def _readAllTurorialBonusesTriggerSection(xmlCtx, section, chapter, triggerID):
    return sub_parsers.readValidateVarTriggerSection(xmlCtx, section, triggerID, triggers.AllTutorialBonusesTrigger)


def _readInvalidateFlagsTriggerSection(xmlCtx, section, chapter, triggerID):
    return triggers.InvalidateFlagsTrigger(triggerID)


def _readRandomBattlesCountTriggerSection(xmlCtx, section, chapter, triggerID):
    return triggers.RandomBattlesCountTrigger(triggerID)


def _readResearchModuleTriggerSection(xmlCtx, section, chapter, triggerID):
    return triggers.ResearchModuleTrigger(triggerID)


def _readInstallModuleTriggerSection(xmlCtx, section, chapter, triggerID):
    return triggers.InstallModuleTrigger(triggerID)


def _readResearchVehicleTriggerSection(xmlCtx, section, chapter, triggerID):
    return sub_parsers.readValidateVarTriggerSection(xmlCtx, section, triggerID, triggers.ResearchVehicleTrigger)


def _readBuyVehicleTriggerSection(xmlCtx, section, chapter, triggerID):
    return sub_parsers.readValidateVarTriggerSection(xmlCtx, section, triggerID, triggers.BuyVehicleTrigger)


def _readInventoryVehicleTriggerSection(xmlCtx, section, chapter, triggerID):
    return sub_parsers.readValidateVarTriggerSection(xmlCtx, section, triggerID, triggers.InventoryVehicleTrigger)


def _readPermanentVehicleOwnTriggerSection(xmlCtx, section, chapter, triggerID):
    return sub_parsers.readValidateVarTriggerSection(xmlCtx, section, triggerID, triggers.PermanentVehicleOwnTrigger)


def _readXpExchangeTriggerSection(xmlCtx, section, chapter, triggerID):
    return triggers.XpExchangeTrigger(triggerID)


def _readVehicleBattlesCountTriggerSection(xmlCtx, section, chapter, triggerID):
    return sub_parsers.readValidateVarTriggerSection(xmlCtx, section, triggerID, triggers.VehicleBattleCountTrigger)


def readTutorialIntSettingTriggerSection(xmlCtx, section, _, triggerID):
    return sub_parsers.readValidateVarTriggerSection(xmlCtx, section, triggerID, triggers.TutorialIntSettingsTrigger)


def readTutorialAccountSettingTriggerSection(xmlCtx, section, _, triggerID):
    return sub_parsers.readValidateVarTriggerSection(xmlCtx, section, triggerID, triggers.TutorialAccountSettingsTrigger)


def _readChapterBonusTriggerSection(xmlCtx, section, _, triggerID):
    return sub_parsers.readValidateVarTriggerSection(xmlCtx, section, triggerID, triggers.ChapterBonusTrigger)


def _readItemsInstallTriggerSection(xmlCtx, section, _, triggerID):
    return sub_parsers.readValidateVarTriggerSection(xmlCtx, section, triggerID, triggers.InstallItemsTrigger)


def readSaveTutorialSettingSection(xmlCtx, section, _, conditions):
    settingID = sub_parsers.parseID(xmlCtx, section, 'Specify a setting ID')
    return effects.HasTargetEffect(settingID, _EFFECT_TYPE.SAVE_TUTORIAL_SETTING, conditions=conditions)


def readSaveAccountSettingSection(xmlCtx, section, _, conditions):
    settingID = sub_parsers.parseID(xmlCtx, section, 'Specify a setting ID')
    return effects.HasTargetEffect(settingID, _EFFECT_TYPE.SAVE_ACCOUNT_SETTING, conditions=conditions)


def readTutorialSettingSection(xmlCtx, section, flags):
    settingID = sub_parsers.parseID(xmlCtx, section, 'Specify a setting ID')
    settingName = None
    if 'setting-name' in section.keys():
        settingName = _xml.readString(xmlCtx, section, 'setting-name')
    else:
        _xml.raiseWrongXml(xmlCtx, section.name, 'Specify a setting name')
    settingValue = None
    if 'setting-value' in section.keys():
        settingValue = _xml.readBool(xmlCtx, section, 'setting-value')
    else:
        _xml.raiseWrongXml(xmlCtx, section.name, 'Specify a setting value')
    return chapter.TutorialSetting(settingID, settingName, settingValue)


def readQuestConditions(section):
    result = []
    valuesSec = section['quest-conditions']
    if valuesSec is not None:
        for name, conditionsSection in valuesSec.items():
            valueType, valueSec = conditionsSection.items()[0]
            result.append(readVarValue(valueType, valueSec))

    return result


def _readSimpleWindowCloseTriggerSection(xmlCtx, section, _, triggerID):
    return sub_parsers.readValidateVarTriggerSection(xmlCtx, section, triggerID, triggers.SimpleWindowCloseTrigger, validateUpdateOnly='validate-update-only' in section.keys())


def _readSimpleWindowProcessTriggerSection(xmlCtx, section, _, triggerID):
    return sub_parsers.readValidateVarTriggerSection(xmlCtx, section, triggerID, triggers.SimpleWindowProcessTrigger, validateUpdateOnly='validate-update-only' in section.keys())


def _readSelectVehicleInHangarSection(xmlCtx, section, flags, conditions):
    targetID = section.asString
    return effects.HasTargetEffect(targetID, effects.EFFECT_TYPE.SELECT_VEHICLE_IN_HANGAR, conditions=conditions)


def init():
    sub_parsers.setEffectsParsers({'save-setting': readSaveTutorialSettingSection,
     'save-account-setting': readSaveAccountSettingSection,
     'show-unlocked-chapter': chains.readShowUnlockedChapterSection,
     'switch-to-random': lobby.readSwitchToRandomSection,
     'select-in-hangar': _readSelectVehicleInHangarSection})
    sub_parsers.setEntitiesParsers({'hint': chains.readHintSection,
     'tutorial-setting': readTutorialSettingSection})
    sub_parsers.setTriggersParsers({'bonus': lobby.readBonusTriggerSection,
     'premiumDiscount': lobby.readPremiumDiscountsUseTriggerSection,
     'timer': lobby.readTimerTriggerSection,
     'tankmanAcademyDiscount': chains.readTankmanPriceDiscountTriggerSection,
     'allTutorialBonuses': _readAllTurorialBonusesTriggerSection,
     'randomBattlesCount': _readRandomBattlesCountTriggerSection,
     'researchModule': _readResearchModuleTriggerSection,
     'installModule': _readInstallModuleTriggerSection,
     'researchVehicle': _readResearchVehicleTriggerSection,
     'buyVehicle': _readBuyVehicleTriggerSection,
     'inventoryVehicle': _readInventoryVehicleTriggerSection,
     'permanentOwnVehicle': _readPermanentVehicleOwnTriggerSection,
     'buySlot': lobby.readFreeVehicleSlotTriggerSection,
     'vehicleBattlesCount': _readVehicleBattlesCountTriggerSection,
     'xpExchange': _readXpExchangeTriggerSection,
     'tutorialIntSetting': readTutorialIntSettingTriggerSection,
     'tutorialAccountSetting': readTutorialAccountSettingTriggerSection,
     'chapterBonus': _readChapterBonusTriggerSection,
     'installItems': _readItemsInstallTriggerSection,
     'invalidateFlags': _readInvalidateFlagsTriggerSection,
     'fightBtn': chains.readFightBtnDisableTriggerSection,
     'windowClosed': _readSimpleWindowCloseTriggerSection,
     'windowProcessed': _readSimpleWindowProcessTriggerSection,
     'isInSandbox': chains.readIsInSandBoxPreQueueTriggerSection,
     'queue': chains.readQueueTrigger,
     'isInSandboxOrRandom': chains.readIsInSandBoxOrRandomPreQueueTriggerSection})
    sub_parsers.setWindowsParsers({'awardWindow': sub_parsers.readQuestAwardWindowSection})
