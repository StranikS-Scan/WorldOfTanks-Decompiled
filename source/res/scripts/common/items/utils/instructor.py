# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/utils/instructor.py
import random
import nations
from typing import TYPE_CHECKING
from crew2 import settings_globals
from items.components.detachment_constants import InstructorAttrs, InstructorMaxValues
if TYPE_CHECKING:
    from items.instructor import InstructorDescr
    from crew2.instructor.instructor_settings import InstructorSettings, InstructorNationSettings

def isNationValid(_, nationID, settings):
    return nationID == nations.NONE_INDEX or nationID in settings.nations and nationID <= InstructorMaxValues.NATION_ID


def isFirstNameValid(instructor, nameID, settings):
    return nameID is None or nameID <= InstructorMaxValues.FIRST_NAME_ID and nameID in settings.getNationSettings(instructor.nationID).firstNameIDs


def isSecondNameValid(instructor, snameID, settings):
    return snameID is None or snameID <= InstructorMaxValues.SECOND_NAME_ID and snameID in settings.getNationSettings(instructor.nationID).secondNameIDs


def isPortraitIDValid(instructor, portraitID, settings):
    return portraitID is None or portraitID <= InstructorMaxValues.PORTRAIT_ID and settings.getNationSettings(instructor.nationID).portraitIDs


def generateNation(settings):
    return random.choice(settings.getAvailableNations())


def generateFirstName(nationSettings):
    return random.choice(nationSettings.firstNameIDs)


def generateSecondName(nationSettings):
    return random.choice(nationSettings.secondNameIDs)


def generatePortrait(nationSettings):
    return random.choice(nationSettings.portraitIDs)


INSTRUCTOR_GENERATORS = ((InstructorAttrs.FIRST_NAME_ID, generateFirstName), (InstructorAttrs.SECOND_NAME_ID, generateSecondName), (InstructorAttrs.PORTRAIT_ID, generatePortrait))
INSTRUCTOR_VALIDATORS = ((InstructorAttrs.NATION_ID, isNationValid),
 (InstructorAttrs.FIRST_NAME_ID, isFirstNameValid),
 (InstructorAttrs.SECOND_NAME_ID, isSecondNameValid),
 (InstructorAttrs.PORTRAIT_ID, isPortraitIDValid))
