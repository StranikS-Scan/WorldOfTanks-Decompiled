# Embedded file name: scripts/client/tutorial/doc_loader/sub_parsers/battle_quests.py
from tutorial.doc_loader import sub_parsers
from tutorial.doc_loader.sub_parsers import quests
from tutorial.control.quests.battle import triggers
from tutorial.data import effects
_EFFECT_TYPE = effects.EFFECT_TYPE

def _readUseItemsTriggerSection(xmlCtx, section, chapter, triggerID):
    return sub_parsers.readValidateVarTriggerSection(xmlCtx, section, triggerID, triggers.UseItemsTrigger)


def init():
    sub_parsers.setEffectsParsers({'save-setting': quests.readSaveTutorialSettingSection})
    sub_parsers.setEntitiesParsers({'tutorial-setting': quests.readTutorialSettingSection})
    sub_parsers.setTriggersParsers({'tutorialIntSetting': quests.readTutorialIntSettingTriggerSection,
     'useItem': _readUseItemsTriggerSection})
