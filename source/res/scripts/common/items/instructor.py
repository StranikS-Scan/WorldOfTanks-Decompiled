# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/instructor.py
import struct
from itertools import izip
import nations
import random
from typing import Optional, Dict, List
from crew2 import settings_globals
from items import ITEM_TYPES
from items.components.detachment_constants import InstructorAttrs, INSTRUCTOR_VOLATILE_PROPERTIES_COUNT, INSTRUCTOR_VOLATILE_PROPERTIES
from items.components.detachment_components import validate, generate, convertAndGetPropertyValues, convertAndApplyPropertyValues, packIDs, unpackIDs
from items.utils.common import spliceCompDescr, SoftAssert, getEnumValues
from items.utils.instructor import generateNation, INSTRUCTOR_VALIDATORS, INSTRUCTOR_GENERATORS

class InstructorDescr(object):
    __slots__ = getEnumValues(InstructorAttrs)

    def __init__(self, settingsID=None, nationID=nations.NONE_INDEX, setDefPerks=False):
        self._settingsID = settingsID
        self._nationID = nationID
        self._perksIDs = []
        self._professionID = 0
        self.firstNameID = None
        self.secondNameID = None
        self.portraitID = None
        self._classID = None
        self._isFemale = False
        self._voiceOverID = None
        self._pageBackground = None
        self.__isInited = False
        if self._settingsID is not None:
            self.initBySettings(settingsID, nationID, setDefPerks=setDefPerks)
        return

    @property
    def settingsID(self):
        return self._settingsID

    @property
    def perksIDs(self):
        return self._perksIDs

    @property
    def professionID(self):
        return self._professionID

    @property
    def nationID(self):
        return self._nationID

    @property
    def classID(self):
        return self._classID

    @property
    def isFemale(self):
        return self._isFemale

    @property
    def voiceOverID(self):
        return self._voiceOverID

    @property
    def pageBackground(self):
        return self._pageBackground

    @property
    def inited(self):
        return self.__isInited

    def isNationSet(self):
        return self.nationID != nations.NONE_INDEX

    def isToken(self):
        return not self.isNationSet() or not self.perksIDs

    def initBySettings(self, settingsID, nationID=nations.NONE_INDEX, setMainNation=False, setDefPerks=False):
        self._settingsID = settingsID
        self._nationID = nationID
        nationIsSet = nationID != nations.NONE_INDEX
        SoftAssert(nationIsSet ^ setMainNation or not (nationIsSet and setMainNation), 'set nation or use main nation')
        self._loadStaticProperties(setMainNation, setDefPerks)

    def generate(self):
        SoftAssert(self.__isInited, 'descriptor not inited')
        settings = self.getInstructorSettings()
        if not self.isNationSet():
            self._nationID = generateNation(settings)
        nationalSetting = settings.getNationSettings(self._nationID)
        generate(INSTRUCTOR_GENERATORS, self, {}, nationalSetting)

    def generateByNation(self, nationID):
        SoftAssert(self.__isInited, 'descriptor not inited')
        SoftAssert(self._settingsID, 'settings ID not set')
        SoftAssert(nationID in nations.MAP or nationID == nations.NONE_INDEX, 'incorrect nationID {}'.format(nationID))
        self._nationID = nationID
        self.generate()

    def getPerks(self):
        SoftAssert(self.perksIDs is not None, 'perksID is not set')
        instSettingsProvider = settings_globals.g_instructorSettingsProvider
        perksPoints = instSettingsProvider.classes.getClassByID(self.classID).perkPoints
        return {perkID:points for perkID, points in izip(self.perksIDs, perksPoints)}

    def setPerksIDs(self, perksIDs):
        self._perksIDs = perksIDs[:]

    def setProfessionID(self, professionID):
        self._professionID = professionID

    def setIsFemale(self, value):
        self._isFemale = value

    @staticmethod
    def createByCompDescr(compDescr):
        instructorDescr = InstructorDescr()
        instructorDescr._initByCompDescr(compDescr)
        return instructorDescr

    @staticmethod
    def createByPreset(presetName, nationID=nations.NONE_INDEX, firstNameID=None, secondNameID=None, portraitID=None, professionID=None, perksIDs=None, token=False):

        def validateAndGetProperty(propertyName, val, IDs, nationName, randomChoice=True):
            if val is not None:
                SoftAssert(val in IDs, "'{}' with value '{}' is not in instructor '{} : {}' settings".format(propertyName, val, presetName, nationName))
                return val
            else:
                return random.choice(IDs) if randomChoice else IDs[0]

        instructorSettingsProvider = settings_globals.g_instructorSettingsProvider
        instructorSettID = instructorSettingsProvider.getIDbyName(presetName)
        SoftAssert(instructorSettID is not None, 'preset not exist in settings: {}'.format(presetName))
        settings = instructorSettingsProvider.getInstructorByID(instructorSettID)
        availableNations = settings.getAvailableNations()
        if nationID != nations.NONE_INDEX:
            SoftAssert(nationID in nations.MAP, 'incorrect nationID {}'.format(nationID))
            SoftAssert(nationID in availableNations, "nation '{}' not available for instructor '{}'".format(nations.MAP[nationID], presetName))
        elif not token:
            SoftAssert(len(availableNations) == 1, 'can not create instructor(not token) with multi-nation: {}'.format(presetName))
            nationID = availableNations[0]
        instrDescr = InstructorDescr()
        if nationID != nations.NONE_INDEX:
            nationalSett = settings.getNationSettings(nationID)
            nation = nations.MAP[nationID]
            instrDescr.firstNameID = validateAndGetProperty('firstNameID', firstNameID, nationalSett.firstNameIDs, nation)
            instrDescr.secondNameID = validateAndGetProperty('secondNameID', secondNameID, nationalSett.secondNameIDs, nation)
            instrDescr.portraitID = validateAndGetProperty('portraitID', portraitID, nationalSett.portraitIDs, nation)
        if perksIDs:
            SoftAssert(professionID is not None, 'unspecified profession id')
            profession = instructorSettingsProvider.professions.getProfession(professionID)
            SoftAssert(profession, 'incorrect profession id: {}'.format(professionID))
            SoftAssert(profession.isPerksMatchToProfession(perksIDs), 'perks dont match to one profession={}'.format(professionID))
            instrDescr._professionID = professionID
            instrDescr._perksIDs = perksIDs
        elif not token:
            instrDescr._professionID = getDefaultProfessionIDByPerks(settings.defaultPerksIDs)
            instrDescr._perksIDs = settings.defaultPerksIDs
        instrDescr.initBySettings(instructorSettID, nationID)
        SoftAssert(instrDescr.isToken() == token, "wrong token parameter. Parameter: '{}'; instructor token: '{}'; preset: {}".format(token, instrDescr.isToken(), presetName))
        return instrDescr

    @staticmethod
    def createByRecruit(tankmanDescr, settingsID):
        instrDescr = InstructorDescr(settingsID)
        instrDescr._nationID = tankmanDescr.nationID
        instrDescr.firstNameID = tankmanDescr.firstNameID
        instrDescr.secondNameID = tankmanDescr.lastNameID
        instrDescr.portraitID = tankmanDescr.iconID
        instrDescr._isFemale = tankmanDescr.isFemale
        return instrDescr

    def makeCompDescr(self, validate=True):
        if validate:
            self._validate()
        header = 0
        cd = struct.pack('<4B', header, ITEM_TYPES.instructor, self._nationID, self._professionID)
        cd += struct.pack('<H', self._settingsID)
        cd += packIDs(self.perksIDs or [])
        cd += struct.pack(('<' + str(INSTRUCTOR_VOLATILE_PROPERTIES_COUNT) + 'H'), *convertAndGetPropertyValues(self, INSTRUCTOR_VOLATILE_PROPERTIES))
        return cd

    def getInstructorSettings(self):
        SoftAssert(self._settingsID, 'settings ID not set')
        return settings_globals.g_instructorSettingsProvider.getInstructorByID(self._settingsID)

    def getSlotsCount(self):
        instrSettingsProvider = settings_globals.g_instructorSettingsProvider
        instructorClass = instrSettingsProvider.classes.getClassByID(self.classID)
        return instructorClass.slotsCount

    def _validate(self):
        SoftAssert(self.__isInited, 'instructor descriptor not inited')
        settings = self.getInstructorSettings()
        validate(INSTRUCTOR_VALIDATORS, self, True, settings)

    def _initByCompDescr(self, compDescr):
        cdPart, offset = spliceCompDescr(compDescr, 0, 4)
        header, itemType, self._nationID, self._professionID = struct.unpack('<4B', cdPart)
        SoftAssert(itemType == ITEM_TYPES.instructor, 'not suitable compact descriptor')
        cdPart, offset = spliceCompDescr(compDescr, offset, 2)
        self._settingsID = struct.unpack('<H', cdPart)
        self._perksIDs, offset = unpackIDs(compDescr, offset)
        cdPart, offset = spliceCompDescr(compDescr, offset, INSTRUCTOR_VOLATILE_PROPERTIES_COUNT * 2)
        values = struct.unpack('<' + str(INSTRUCTOR_VOLATILE_PROPERTIES_COUNT) + 'H', cdPart)
        convertAndApplyPropertyValues(self, INSTRUCTOR_VOLATILE_PROPERTIES, values)
        self._loadStaticProperties()

    def _loadStaticProperties(self, setMainNation=False, setDefPerks=False):
        instrSettings = self.getInstructorSettings()
        SoftAssert(instrSettings, 'instructors settings #{} not found in instructors/settings.xml'.format(self._settingsID))
        availableNations = instrSettings.getAvailableNations()
        if not self.isNationSet():
            if setMainNation:
                SoftAssert(len(availableNations) == 1, 'instructor settings has more than one nation')
                self._nationID = availableNations[0]
        else:
            SoftAssert(self._nationID in availableNations, 'nation is not available for current instructor settings')
        self._classID = instrSettings.classID
        self._isFemale = instrSettings.isFemale
        self._voiceOverID = instrSettings.voiceover
        if instrSettings.backgrounds is not None:
            self._pageBackground = instrSettings.backgrounds.page
        if setDefPerks:
            self._perksIDs = instrSettings.defaultPerksIDs
            self._professionID = getDefaultProfessionIDByPerks(self._perksIDs)
        self.__isInited = True
        return


def getDefaultProfessionIDByPerks(perksIDs):
    instrSettingsProvider = settings_globals.g_instructorSettingsProvider
    professionID = None
    if perksIDs:
        professionID = instrSettingsProvider.professions.getProfessionIDByPerk(perksIDs[0])
    SoftAssert(professionID, 'invalidate default profession')
    return professionID
