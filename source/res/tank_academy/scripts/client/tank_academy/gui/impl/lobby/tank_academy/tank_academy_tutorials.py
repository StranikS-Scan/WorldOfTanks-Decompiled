# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tank_academy/scripts/client/tank_academy/gui/impl/lobby/tank_academy/tank_academy_tutorials.py
TANK_ACADEMY_MULTIPLIED_XP_CHAPTER_ID = 'tankAcademyMultipliedXP'
TANK_ACADEMY_RESEARCH_MODULE_CHAPTER_ID = 'tankAcademyResearchModule'
TANK_ACADEMY_RESEARCH_VEHICLE_4_CHAPTER_ID = 'tankAcademyResearchVehicle_4'
TANK_ACADEMY_RESEARCH_VEHICLE_5_CHAPTER_ID = 'tankAcademyResearchVehicle_5'
TANK_ACADEMY_ALL_EQUIPMENT_CHAPTER_ID = 'tankAcademyAllEquipment'
TANK_ACADEMY_OPTIONAL_DEVICES_CHAPTER_ID = 'tankAcademyOptionalDevices'
TANK_ACADEMY_ALL_AMMUNITION_CHAPTER_ID = 'tankAcademyAllAmmunition'
TANK_ACADEMY_CUSTOMIZATION_CHAPTER_ID = 'tankAcademyCustomization'
TANK_ACADEMY_PERSONAL_RESERVES_CHAPTER_ID = 'tankAcademyPersonalReserves'
QUEST_TUTORIAL_CHAPTER_BY_ID = {'tank_academy_2': TANK_ACADEMY_MULTIPLIED_XP_CHAPTER_ID,
 'tank_academy_3': TANK_ACADEMY_RESEARCH_MODULE_CHAPTER_ID,
 'tank_academy_5': TANK_ACADEMY_RESEARCH_VEHICLE_4_CHAPTER_ID,
 'tank_academy_6': TANK_ACADEMY_ALL_EQUIPMENT_CHAPTER_ID,
 'tank_academy_7': TANK_ACADEMY_OPTIONAL_DEVICES_CHAPTER_ID,
 'tank_academy_8': TANK_ACADEMY_ALL_AMMUNITION_CHAPTER_ID,
 'tank_academy_10': TANK_ACADEMY_RESEARCH_VEHICLE_5_CHAPTER_ID,
 'tank_academy_11': TANK_ACADEMY_CUSTOMIZATION_CHAPTER_ID,
 'tank_academy_26': TANK_ACADEMY_PERSONAL_RESERVES_CHAPTER_ID}

def getQuestTutorialChapterID(quest):
    return None if quest is None else QUEST_TUTORIAL_CHAPTER_BY_ID.get(quest.getID())


def hasQuestTutorial(quest):
    return getQuestTutorialChapterID(quest) is not None
