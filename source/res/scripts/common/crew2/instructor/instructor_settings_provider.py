# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/crew2/instructor/instructor_settings_provider.py
import typing
import ResMgr
from crew2 import crew2_consts
from crew2.instructor.classes import InstructorClasses
from crew2.instructor.instructor_settings import InstructorSettings
from crew2.instructor.professions import InstructorProfessions
from items import _xml, ITEM_DEFS_PATH
import nations
if typing.TYPE_CHECKING:
    from crew2.settings_locator import Crew2Settings
DEF_INSTRUCTOR_SETTINGS_PATH = ITEM_DEFS_PATH + 'crew2/instructors/'

class InstructorSettingsProvider(object):

    def __init__(self, configsPath, settingsLocator=None):
        self._settingsLocator = settingsLocator
        settingsLocator.instructorSettingsProvider = self
        classesPath = configsPath + 'classes.xml'
        self._classes = InstructorClasses(classesPath)
        professionsPath = configsPath + 'professions.xml'
        self._professions = InstructorProfessions(professionsPath)
        self._instructors = {}
        self._nameToID = {}
        settingsPath = configsPath + 'settings.xml'
        self.__loadInstructors(settingsPath)

    @property
    def classes(self):
        return self._classes

    @property
    def professions(self):
        return self._professions

    @property
    def exclusionHours(self):
        return self._exclusionHours

    @property
    def instructors(self):
        return self._instructors

    def getInstructorByID(self, ID):
        return self._instructors.get(ID)

    def getInstructorByName(self, name):
        presetID = self._nameToID.get(name)
        return self.getInstructorByID(presetID)

    def getIDbyName(self, name):
        return self._nameToID.get(name)

    def getNameByID(self, ID):
        return next((k for k, v in self._nameToID.items() if v == ID), None)

    def __loadInstructors(self, path):
        section = ResMgr.openSection(path)
        if section is None:
            _xml.raiseWrongXml(None, path, 'can not open or read')
        xmlCtx = (None, path)
        self._loadParams((xmlCtx, 'params'), section['params'])
        settingsXmlCtx = (xmlCtx, 'settings')
        for _, instrSect in _xml.getChildren(xmlCtx, section, 'instructorSettingsList'):
            instrSet = InstructorSettings(settingsXmlCtx, instrSect, self._settingsLocator)
            if instrSet.id in self._instructors:
                _xml.raiseWrongXml(settingsXmlCtx, '', 'Duplicated instructor settings id {}'.format(instrSet.id))
            self._instructors[instrSet.id] = instrSet
            if instrSet.name in self._nameToID:
                _xml.raiseWrongXml(settingsXmlCtx, '', "Duplicated instructor settings name '{}'".format(instrSet.name))
            self._nameToID[instrSet.name] = instrSet.id

        ResMgr.purge(path)
        self.__validateInstructors(xmlCtx)
        return

    def _loadParams(self, xmlCtx, section):
        self._exclusionHours = _xml.readInt(xmlCtx, section, 'exclusionHours')

    def __validateInstructors(self, xmlCtx):
        for instrID, instrSettings in self._instructors.iteritems():
            self.__validateInstructorClass(xmlCtx, instrSettings)
            self.__validateProfessions(xmlCtx, instrSettings)
            self.__validateInstructorCharacterIDs(xmlCtx, instrSettings)

    def __validateInstructorClass(self, xmlCtx, instrSettings):
        instrClass = self._classes.getClassByID(instrSettings.classID)
        if instrClass is None:
            _xml.raiseWrongXml(xmlCtx, '', "Instructor settings '{}'. Class with ID = {} does not exist".format(instrSettings.name, instrSettings.classID))
        return

    def __validateProfessions(self, xmlCtx, instrSettings):
        if instrSettings.professionVariants is not None:
            for profID in instrSettings.professionVariants:
                if self._professions.getProfession(profID) is None:
                    _xml.raiseWrongXml(xmlCtx, '', 'profession by ID {} does not exist'.format(profID))

        return

    def __validateInstructorCharacterIDs(self, xmlCtx, instr):
        instrPool = self._settingsLocator.characterProperties
        eGender = crew2_consts.BOOL_TO_GENDER[instr.isFemale]
        genderTag = crew2_consts.GENDER_TO_TAG[eGender]
        for nationID, nationSettings in instr.nations.iteritems():
            for firstNameID in nationSettings.firstNameIDs:
                if instrPool.getFirstNameByID(nationID, firstNameID, gender=eGender) is None:
                    _xml.raiseWrongXml(xmlCtx, '', "Instructor settings '{}'. Nation '{}'. FirstNameID {} of gender '{}' does not exist".format(instr.name, nations.NAMES[nationID], firstNameID, genderTag))

            for secondNameID in nationSettings.secondNameIDs:
                if instrPool.getSecondNameByID(nationID, secondNameID, gender=eGender) is None:
                    _xml.raiseWrongXml(xmlCtx, '', "Instructor settings '{}'. Nation '{}'. SecondNameID {} of gender '{}' does not exist".format(instr.name, nations.NAMES[nationID], secondNameID, genderTag))

            for portraitID in nationSettings.portraitIDs:
                if instrPool.getPortraitByID(nationID, portraitID, gender=eGender) is None:
                    _xml.raiseWrongXml(xmlCtx, '', "Instructor settings '{}'. Nation '{}'. PortraitID {} of gender '{}' does not exist".format(instr.name, nations.NAMES[nationID], portraitID, genderTag))

        return
