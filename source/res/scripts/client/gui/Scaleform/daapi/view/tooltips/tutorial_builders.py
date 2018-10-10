# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/tutorial_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts
from gui.shared.tooltips import tutorial
from gui.shared.tooltips.builders import DataBuilder
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.HANGAR_TUTORIAL_RESEARCH_VEHICLE_INFO, TOOLTIPS_CONSTANTS.HANGAR_TUTORIAL_RESEARCH_VEHICLE_INFO_UI, tutorial.ResearchVehicleInfoPacker(contexts.HangarTutorialContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.HANGAR_TUTORIAL_RESEARCH_MODULES_PREMIUM, TOOLTIPS_CONSTANTS.HANGAR_TUTORIAL_RESEARCH_MODULES_PREMIUM_UI, tutorial.ResearchModulesPacker(contexts.HangarTutorialContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.HANGAR_TUTORIAL_RESEARCH_MODULES, TOOLTIPS_CONSTANTS.HANGAR_TUTORIAL_RESEARCH_MODULES_UI, tutorial.ResearchModulesPackerEx(contexts.HangarTutorialContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.HANGAR_TUTORIAL_CUSTOMIZATION_TYPES, TOOLTIPS_CONSTANTS.HANGAR_TUTORIAL_CUSTOMIZATION_TYPES_UI, tutorial.CustomizationTypesPacker(contexts.HangarTutorialContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.HANGAR_TUTORIAL_NATIONS, TOOLTIPS_CONSTANTS.HANGAR_TUTORIAL_NATIONS_UI, tutorial.NationsPacker(contexts.HangarTutorialContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.HANGAR_TUTORIAL_RESEARCH_TREE, TOOLTIPS_CONSTANTS.HANGAR_TUTORIAL_RESEARCH_TREE_UI, tutorial.ResearchTreePacker(contexts.HangarTutorialContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.HANGAR_TUTORIAL_PERSONAL_CASE_SKILLS, TOOLTIPS_CONSTANTS.HANGAR_TUTORIAL_PERSONAL_CASE_SKILLS_UI, tutorial.PersonalCaseSkillsPacker(contexts.HangarTutorialContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.HANGAR_TUTORIAL_PERSONAL_CASE_PERKS, TOOLTIPS_CONSTANTS.HANGAR_TUTORIAL_PERSONAL_CASE_PERKS_UI, tutorial.PersonalCasePerksPacker(contexts.HangarTutorialContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.HANGAR_TUTORIAL_PERSONAL_CASE_ADDITIONAL, TOOLTIPS_CONSTANTS.HANGAR_TUTORIAL_PERSONAL_CASE_ADDITIONAL_UI, tutorial.PersonalCaseAdditionalPacker(contexts.HangarTutorialContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.HANGAR_TUTORIAL_AMMUNITION, TOOLTIPS_CONSTANTS.HANGAR_TUTORIAL_AMMUNITION_UI, tutorial.AmmunitionPacker(contexts.HangarTutorialContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.HANGAR_TUTORIAL_EQUPMENT, TOOLTIPS_CONSTANTS.HANGAR_TUTORIAL_EQUPMENT_UI, tutorial.EquipmentPacker(contexts.HangarTutorialContext())))
