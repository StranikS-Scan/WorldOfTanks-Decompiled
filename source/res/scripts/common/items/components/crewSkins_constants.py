# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/crewSkins_constants.py
CREW_SKINS_XML_FILE = 'crewSkins.xml'
CREW_SKINS_PRICE_GROUPS_XML_FILE = 'priceGroups.xml'
NO_CREW_SKIN_ID = 0
NO_CREW_SKIN_SOUND_SET = '-'

class CREW_SKIN_PROPERTIES_MASKS:
    ROLE = 1
    SEX = 2
    NATION = 4
    EMPTY_MASK = 0


class CrewSkinType:
    CREW_SKIN = 1
    ITEM_GROUP = 2
    RANGE = {CREW_SKIN, ITEM_GROUP}


class TANKMAN_SEX:
    NONE = ''
    MALE = 'male'
    FEMALE = 'female'
    ALL = (MALE, FEMALE)
    AVAILABLE = (NONE, MALE, FEMALE)

    @staticmethod
    def getTankmanSex(tmanDescr):
        return TANKMAN_SEX.FEMALE if tmanDescr.isFemale else TANKMAN_SEX.MALE


class CREW_SKIN_RARITY:
    COMMON = 1
    RARE = 2
    EPIC = 3
    ALL = (COMMON, RARE, EPIC)
