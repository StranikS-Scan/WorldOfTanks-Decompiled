# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/crew2/conversion.py
from collections import namedtuple
import typing
import calendar
import time
import ResMgr
from crew2.settings_locator import Crew2Settings
from crew2.skillsConversion import SkillsConversion
from items import _xml, ITEM_DEFS_PATH, tankmen, vehicles
import nations
from items.components import detachment_constants
from items.components.detachment_constants import DETACHMENT_DEFAULT_PRESET
if typing.TYPE_CHECKING:
    from crew2.detachment.detachment_preset import DetachmentPreset
    from crew2.instructor.instructor_settings import InstructorSettings
    from items.tankmen import TankmanDescr
DEF_CONVERSION_CFG_PATH = ITEM_DEFS_PATH + 'crew2/conversion.xml'
ConvertableTankman = namedtuple('ConvertableTankman', 'obligatoryPart optionalPart')
CTObligatory = namedtuple('CTObligatory', 'group')
CTOptional = namedtuple('CTOptional', 'isPremiumGroup nationID firstNameID lastNameID iconID hasFreeSkills')
TankmanToDetachment = namedtuple('TankmanToDetachment', ('tankman', 'detachment'))
TankmanToInstructor = namedtuple('TankmanToInstructor', ('tankman', 'instructor', 'isToken'))
UnremovableInstructor = namedtuple('UnremovableInstructor', ('tankman', 'instructor', 'detachment'))

class ConversionSettings(object):

    def __init__(self, configPath, settingsLocator=None):
        self._settingsLocator = settingsLocator
        self._detachments = {}
        self._instructors = {}
        self._importantTankmen = {}
        self._tankmenToSkins = {}
        self._unremovableInstructor = {}
        self._skillsConversion = None
        self._endConversion = 0
        self._load(configPath)
        return

    @property
    def endConversion(self):
        return self._endConversion

    @property
    def skillsConversion(self):
        return self._skillsConversion

    def getDetachmentForTankman(self, tankman):
        if tankman is None:
            return
        else:
            key = self._makeConvertableTankmanKey(tankman)
            ttdList = self._detachments.get(key)
            if ttdList is None:
                return
            for ttd in ttdList:
                if self._compareTankman(tankman, ttd.tankman):
                    return self._settingsLocator.detachmentSettings.presets.getDetachmentPreset(ttd.detachment)

            return

    def getDetachmentForCrew(self, crew):
        for tankman in crew:
            preset = self.getDetachmentForTankman(tankman)
            if preset:
                return preset

        return self._settingsLocator.detachmentSettings.presets.getDetachmentPreset(DETACHMENT_DEFAULT_PRESET)

    def getInstructorForTankman(self, tankman):
        key = self._makeConvertableTankmanKey(tankman)
        ttiList = self._instructors.get(key)
        if ttiList is None:
            return (None, None)
        else:
            for tti in ttiList:
                if self._compareTankman(tankman, tti.tankman):
                    return (self._settingsLocator.instructorSettingsProvider.getInstructorByID(tti.instructor), tti.isToken)

            return (None, None)

    def getSkinIDForTankman(self, tankman):
        key = self._makeConvertableTankmanKey(tankman)
        return self._tankmenToSkins.get(key)

    def getInstructorForToken(self, tokenDict):
        if tokenDict is None:
            return (None, None)
        else:
            key = CTObligatory(tokenDict['group'])
            ttiList = self._instructors.get(key)
            if ttiList is None:
                return (None, None)
            for tti in ttiList:
                if self._compareToken(tokenDict, tti.tankman):
                    return (self._settingsLocator.instructorSettingsProvider.getInstructorByID(tti.instructor), tti.isToken)

            return (None, None)

    def getSkinIDForToken(self, tokenDict):
        if tokenDict is None:
            return
        else:
            key = CTObligatory(tokenDict['group'])
            return self._tankmenToSkins.get(key)

    def getUnremovableInstructorForTankman(self, tankman):
        key = self._makeConvertableTankmanKey(tankman)
        ttiList = self._unremovableInstructor.get(key)
        if ttiList is None:
            return (None, None)
        else:
            for tti in ttiList:
                if self._compareTankman(tankman, tti.tankman):
                    return (tti.detachment, tti.instructor)

            return (None, None)

    def validateCrewToConvertIntoDetachment(self, crew, vehTypeCompDescr, barracksNotEmpty):
        resultMask = detachment_constants.DetachmentConvertationPropertiesMasks.EMPTY_MASK
        resultMsg = ''
        _, nationID, vehTypeID = vehicles.parseIntCompactDescr(vehTypeCompDescr)
        prevPreset = None
        for tmanDescr in crew:
            if tmanDescr is None:
                if barracksNotEmpty:
                    if not resultMask & detachment_constants.DetachmentConvertationPropertiesMasks.FULL_CREW:
                        resultMsg += 'Vehicle has not full crew; '
                    resultMask = resultMask | detachment_constants.DetachmentConvertationPropertiesMasks.FULL_CREW
                continue
            if vehTypeID != tmanDescr.vehicleTypeID:
                if not resultMask & detachment_constants.DetachmentConvertationPropertiesMasks.SPECIALIZATION:
                    resultMsg += 'One of crew members has specialization not compatible with current vehicle;'
                resultMask = resultMask | detachment_constants.DetachmentConvertationPropertiesMasks.SPECIALIZATION
            preset = self.getDetachmentForTankman(tmanDescr)
            if preset:
                if prevPreset:
                    resultMsg += 'Two or more tankmen are special ({}, {})'.format(preset.name, prevPreset.name)
                    resultMask = resultMask | detachment_constants.DetachmentConvertationPropertiesMasks.PRESET
                prevPreset = preset

        return (resultMask == 0, resultMask, resultMsg)

    def isImportantTankman(self, tankman):
        key = self._makeConvertableTankmanKey(tankman)
        itList = self._importantTankmen.get(key)
        if itList is None:
            return False
        else:
            for it in itList:
                if self._compareTankman(tankman, it):
                    return True

            return False

    @staticmethod
    def getTimestampByStrDate(dateStr, timeFormat='%d.%m.%Y %H:%M'):
        return calendar.timegm(time.strptime(dateStr, timeFormat))

    def _getTankmanGroup(self, tankman):
        groups = tankmen.getNationGroups(tankman.nationID, tankman.isPremium)
        return groups.get(tankman.gid)

    def _makeConvertableTankmanKey(self, tankmanDescr):
        group = self._getTankmanGroup(tankmanDescr)
        return CTObligatory(group.name)

    def _compareTankman(self, tankman, convertable):
        if convertable.isPremiumGroup is not None and convertable.isPremiumGroup != tankman.isPremium:
            return False
        elif convertable.nationID is not None and convertable.nationID != tankman.nationID:
            return False
        elif convertable.firstNameID is not None and convertable.firstNameID != tankman.firstNameID:
            return False
        elif convertable.lastNameID is not None and convertable.lastNameID != tankman.lastNameID:
            return False
        elif convertable.iconID is not None and convertable.iconID != tankman.iconID:
            return False
        else:
            return False if convertable.hasFreeSkills is not None and convertable.hasFreeSkills != (tankman.freeSkillsNumber > 0) else True

    def _compareToken(self, token, convertable):
        if convertable.isPremiumGroup is not None and convertable.isPremiumGroup != token['isPremium']:
            return False
        elif convertable.nationID is not None and convertable.nationID not in token['nations']:
            return False
        else:
            return False if convertable.hasFreeSkills is not None and convertable.hasFreeSkills != (len(token['freeSkills']) > 0) else True

    def _load(self, path):
        section = ResMgr.openSection(path)
        if section is None:
            _xml.raiseWrongSection(path, 'can not open or read')
        xmlCtx = (None, path)
        self._endConversion = self._readEndConversion(xmlCtx, section)
        self._detachments = self._readDetachments(xmlCtx, section)
        self._instructors = self._readInstructors(xmlCtx, section)
        self._importantTankmen = self._readImportantTankmen(xmlCtx, section)
        self._tankmenToSkins = self._readTankmanToSkin(xmlCtx, section)
        self._unremovableInstructor = self._readUnremovableInstructors(xmlCtx, section)
        self._skillsConversion = SkillsConversion(self._settingsLocator, xmlCtx, section)
        self._validate(xmlCtx)
        ResMgr.purge(path)
        return

    def _readEndConversion(self, xmlCtx, section):
        date = _xml.readString(xmlCtx, section, 'endConversion')
        if date is None:
            _xml.raiseWrongXml(xmlCtx, '', 'Date of end conversion does not exist')
        return self.getTimestampByStrDate(date, '%Y-%m-%d')

    def _readConvertableTankman(self, xmlCtx, section):
        group = _xml.readString(xmlCtx, section, 'group')
        obligatoryPart = CTObligatory(group)
        isPremiumGroup = _xml.readBoolOrNone(xmlCtx, section, 'isPremiumGroup')
        nation = _xml.readStringOrNone(xmlCtx, section, 'nation')
        nationID = None
        if nation is not None:
            nationID = nations.INDICES[nation]
        IDs = _xml.readIntOrNone(xmlCtx, section, 'characterIDs')
        if IDs is not None:
            firstNameID = lastNameID = iconID = IDs
        else:
            firstNameID = _xml.readIntOrNone(xmlCtx, section, 'firstNameID')
            lastNameID = _xml.readIntOrNone(xmlCtx, section, 'lastNameID')
            iconID = _xml.readIntOrNone(xmlCtx, section, 'iconID')
        hasFreeSkills = _xml.readBoolOrNone(xmlCtx, section, 'hasFreeSkills')
        optionalPart = CTOptional(isPremiumGroup, nationID, firstNameID, lastNameID, iconID, hasFreeSkills)
        return ConvertableTankman(obligatoryPart, optionalPart)

    def _readDetachments(self, xmlCtx, section):
        localCtx = (xmlCtx, 'tankmanToDetachment')
        detachments = {}
        for _, convSec in _xml.getChildren(xmlCtx, section, 'tankmanToDetachment'):
            self._readDetachment(localCtx, convSec, detachments)

        return detachments

    def _readDetachment(self, xmlCtx, section, detachments):
        convertable = self._readConvertableTankman(xmlCtx, section['tankman'])
        detachment = _xml.readString(xmlCtx, section, 'detachment')
        ttd = TankmanToDetachment(convertable.optionalPart, detachment)
        detachments.setdefault(convertable.obligatoryPart, []).append(ttd)

    def _readUnremovableInstructors(self, xmlCtx, section):
        localCtx = (xmlCtx, 'unremovableInstructor')
        unremovableInstructors = {}
        for _, convSec in _xml.getChildren(xmlCtx, section, 'unremovableInstructor'):
            self._readUnremovableInstructor(localCtx, convSec, unremovableInstructors)

        return unremovableInstructors

    def _readUnremovableInstructor(self, xmlCtx, section, unremovableInstructors):
        detachment = _xml.readString(xmlCtx, section, 'detachment')
        localCtx = (xmlCtx, 'crewMembers')
        for _, memberSec in _xml.getChildren(xmlCtx, section, 'crewMembers'):
            self._readCrewMembers(localCtx, memberSec, unremovableInstructors, detachment)

    def _readCrewMembers(self, xmlCtx, section, unremovableInstructors, detachment):
        convertable = self._readConvertableTankman(xmlCtx, section['tankman'])
        instructor = _xml.readString(xmlCtx, section, 'instructor')
        tti = UnremovableInstructor(convertable.optionalPart, instructor, detachment)
        unremovableInstructors.setdefault(convertable.obligatoryPart, []).append(tti)

    def _readInstructors(self, xmlCtx, section):
        localCtx = (xmlCtx, 'tankmanToInstructor')
        instructors = {}
        for _, convSec in _xml.getChildren(xmlCtx, section, 'tankmanToInstructor'):
            self._readInstructor(localCtx, convSec, instructors)

        return instructors

    def _readInstructor(self, xmlCtx, section, instructors):
        convertable = self._readConvertableTankman(xmlCtx, section['tankman'])
        instructorName = _xml.readString(xmlCtx, section, 'instructor')
        instructorID = self._settingsLocator.instructorSettingsProvider.getIDbyName(instructorName)
        if instructorID is None:
            _xml.raiseWrongXml(xmlCtx, '', 'Instructor with name {} does not exist'.format(instructorName))
        isToken = _xml.readBool(xmlCtx, section, 'isToken')
        tti = TankmanToInstructor(convertable.optionalPart, instructorID, isToken)
        instructors.setdefault(convertable.obligatoryPart, []).append(tti)
        return

    def _readImportantTankmen(self, xmlCtx, section):
        localCtx = (xmlCtx, 'importantTankmen')
        importantTankmen = {}
        for _, tmanSec in _xml.getChildren(xmlCtx, section, 'importantTankmen'):
            ct = self._readConvertableTankman(localCtx, tmanSec)
            importantTankmen.setdefault(ct.obligatoryPart, []).append(ct.optionalPart)

        return importantTankmen

    def _readTankmanToSkin(self, xmlCtx, section):
        localCtx = (xmlCtx, 'tankmanToCrewSkin')
        tankmenToSkins = {}
        for _, convSec in _xml.getChildren(xmlCtx, section, 'tankmanToCrewSkin'):
            ct = self._readConvertableTankman(localCtx, convSec['tankman'])
            skinID = _xml.readInt(xmlCtx, convSec, 'skinID')
            if ct.obligatoryPart in tankmenToSkins:
                _xml.raiseWrongXml(xmlCtx, '', 'group {} is not unique in the section tankmanToCrewSkin'.format(ct.obligatoryPart))
            tankmenToSkins[ct.obligatoryPart] = skinID

        return tankmenToSkins

    def _validate(self, xmlCtx):
        for ttdList in self._detachments.itervalues():
            for ttd in ttdList:
                if self._settingsLocator.detachmentSettings.presets.getDetachmentPreset(ttd.detachment) is None:
                    _xml.raiseWrongXml(xmlCtx, '', "detachment preset '{}' does not exist".format(ttd.detachment))

        for ttiList in self._instructors.itervalues():
            for tti in ttiList:
                if self._settingsLocator.instructorSettingsProvider.getInstructorByID(tti.instructor) is None:
                    _xml.raiseWrongXml(xmlCtx, '', "instructor settings '{}' do not exist".format(tti.instructor))

        return
