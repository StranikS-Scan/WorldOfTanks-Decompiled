# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/crew2/detachment/detachment_preset.py
from collections import namedtuple
import typing
import ResMgr
from constants import VEHICLE_CLASS_INDICES
from crew2.detachment.commander_preset import CommanderPreset
from crew2.crew2_consts import BOOL_TO_GENDER, GENDER_TO_TAG
from crew2.settings_locator import Crew2Settings
from items import _xml
from items.components.detachment_constants import DetachmentMaxValues, DetachmentLockMaskBits, DetachmentOperationsMaskBits
from items.vehicles import makeVehicleTypeCompDescrByName, getVehicleType
import nations
VehicleSlot = namedtuple('VehicleSlot', 'vehicleCD canRespecialize')
InstructorSlot = namedtuple('InstructorSlot', 'instructorID, classID, canRemove')

class DetachmentPreset(object):
    __slots__ = ('_id', '_name', '_nationID', '_matrixID', '_progressionID', '_classID', '_experience', '_image', '_lockMask', '_operationsMask', '_commander', '_instructorSlots', '_maxVehicleSlots', '_vehicleSlots')
    STR_TO_LOCK_BIT = {'dissolve': DetachmentLockMaskBits.DISSOLVE,
     'post_progression': DetachmentLockMaskBits.POST_PROGRESSION,
     'build': DetachmentLockMaskBits.BUILD,
     'vehicle_slots': DetachmentLockMaskBits.VEHICLE_SLOTS,
     'instructors': DetachmentLockMaskBits.INSTRUCTORS,
     'commander_customization': DetachmentLockMaskBits.COMMANDER_CUSTOMIZATION,
     'drop_skill': DetachmentLockMaskBits.DROP_SKILL}
    STR_TO_OPERATION_BIT = {'first_drop_skill_special_price': DetachmentOperationsMaskBits.FIRST_DROP_SKILL_PRICE,
     'free_drop_skill_once': DetachmentOperationsMaskBits.NEXT_DROP_SKILL_PRICE}

    def __init__(self, xmlCtx, section, settingsLocator):
        self._id = None
        self._name = None
        self._nationID = None
        self._matrixID = None
        self._progressionID = None
        self._classID = None
        self._experience = None
        self._image = None
        self._lockMask = None
        self._operationsMask = None
        self._commander = None
        self._instructorSlots = None
        self._maxVehicleSlots = settingsLocator.detachmentSettings.maxVehicleSlots
        self._vehicleSlots = None
        self.__load(xmlCtx, section, settingsLocator)
        self.__validate(xmlCtx, settingsLocator)
        return

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def nationID(self):
        return self._nationID

    @property
    def matrixID(self):
        return self._matrixID

    @property
    def progressionID(self):
        return self._progressionID

    @property
    def classID(self):
        return self._classID

    @property
    def experience(self):
        return self._experience

    @property
    def image(self):
        return self._image

    @property
    def lockMask(self):
        return self._lockMask

    @property
    def operationMask(self):
        return self._operationsMask

    @property
    def commander(self):
        return self._commander

    @property
    def instructorSlots(self):
        return self._instructorSlots

    @property
    def maxVehicleSlots(self):
        return self._maxVehicleSlots

    @property
    def vehicleSlots(self):
        return self._vehicleSlots

    def __load(self, xmlCtx, section, settingsLocator):
        self._id = _xml.readPositiveInt(xmlCtx, section, 'id')
        self._name = _xml.readString(xmlCtx, section, 'name')
        nation = _xml.readStringOrNone(xmlCtx, section, 'nation')
        self._nationID = nations.INDICES.get(nation)
        self._matrixID = _xml.readPositiveInt(xmlCtx, section, 'matrixID')
        self._progressionID = _xml.readPositiveInt(xmlCtx, section, 'progressionID')
        self._classID = _xml.readIntOrNone(xmlCtx, section, 'classID')
        classTag = _xml.readStringOrNone(xmlCtx, section, 'class')
        if not self._classID and classTag:
            if classTag not in VEHICLE_CLASS_INDICES:
                _xml.raiseWrongXml(xmlCtx, '', "Detachment '{}' class tag {} is wrong".format(self._name, classTag))
            self._classID = VEHICLE_CLASS_INDICES.get(classTag)
        self._experience = _xml.readIntOrNone(xmlCtx, section, 'experience')
        self._image = _xml.readStringOrNone(xmlCtx, section, 'image')
        self._lockMask = self.__loadMask(xmlCtx, section, 'customizeLock', self.STR_TO_LOCK_BIT)
        self._operationsMask = self.__loadMask(xmlCtx, section, 'operationMask', self.STR_TO_OPERATION_BIT)
        self._maxVehicleSlots = _xml.readIntOrNone(xmlCtx, section, 'maxVehicleSlots') or self._maxVehicleSlots
        self.__loadVehicles(xmlCtx, section)
        self.__loadInstructors(xmlCtx, section, settingsLocator)
        commanderSec = section['commander']
        if commanderSec is not None:
            self._commander = CommanderPreset(xmlCtx, commanderSec, settingsLocator)
        return

    def __loadMask(self, xmlCtx, section, subSectionName, strToBit):
        lockString = section.readString(subSectionName)
        if not lockString:
            return
        else:
            lockMask = 0
            items = [ x.strip() for x in lockString.split(',') ]
            for item in items:
                bit = strToBit.get(item)
                if bit is None:
                    _xml.raiseWrongXml(xmlCtx, '', "Detachment '{}' unknown {} value '{}'. Supported values: {}".format(self._name, subSectionName, item, strToBit.keys()))
                lockMask |= bit

            return lockMask

    def __loadVehicles(self, xmlCtx, section):
        if section['vehicleSlots'] is None:
            return
        else:
            self._vehicleSlots = []
            vehXmlCtx = (xmlCtx, 'vehicle')
            vehicleSections = _xml.getChildren(xmlCtx, section, 'vehicleSlots', throwIfMissing=False)
            if len(vehicleSections) > self._maxVehicleSlots:
                _xml.raiseWrongXml(xmlCtx, '', "Detachment '{}' cannot have more than {} vehicle slots".format(self._name, self._maxVehicleSlots))
            for _, vehSec in vehicleSections:
                name = _xml.readStringOrNone(vehXmlCtx, vehSec, 'vehicleName')
                if name is None:
                    vehicleTypeCD = None
                else:
                    vehicleTypeCD = makeVehicleTypeCompDescrByName(name)
                canRespecialize = _xml.readBool(xmlCtx, vehSec, 'canRespecialize', True)
                if vehicleTypeCD is None and not canRespecialize:
                    _xml.raiseWrongXml(xmlCtx, '', "Detachment '{}'. Detachments cannot have empty unlocked vehicle slots, which cannot be respecialized".format(self._name))
                slot = VehicleSlot(vehicleTypeCD, canRespecialize)
                self._vehicleSlots.append(slot)

            return

    def __loadInstructors(self, xmlCtx, section, settingsLocator):
        if section['instructorSlots'] is None:
            return
        else:
            self._instructorSlots = []
            instrXmlCtx = (xmlCtx, 'instructor')
            instructorSections = _xml.getChildren(xmlCtx, section, 'instructorSlots', throwIfMissing=False)
            maxInstructorSlots = settingsLocator.detachmentSettings.maxInstructorSlots
            if len(instructorSections) > maxInstructorSlots:
                _xml.raiseWrongXml(xmlCtx, '', "Detachment '{}'. Detachments cannot have more than {} instructor slots".format(self._name, maxInstructorSlots))
            slotsCount = 0
            for _, instrSec in instructorSections:
                name = _xml.readStringOrNone(instrXmlCtx, instrSec, 'instructorName')
                if name is None:
                    instructor = None
                else:
                    instructor = settingsLocator.instructorSettingsProvider.getInstructorByName(name)
                    if instructor is None:
                        _xml.raiseWrongXml(xmlCtx, '', "Detachment '{}'. Detachment instructor {} settings not found".format(self._name, name))
                canRemove = _xml.readBool(xmlCtx, instrSec, 'canRemove', True)
                if instructor is None and not canRemove:
                    _xml.raiseWrongXml(xmlCtx, '', "Detachment '{}'. Detachments cannot have empty unlocked instructor slots, from which instructors cannot be removed".format(self._name))
                classID = instructor.classID if instructor else None
                instrSlot = InstructorSlot(instructor.id if instructor else None, classID, canRemove)
                slotsCount += settingsLocator.instructorSettingsProvider.classes.getClassByID(classID).slotsCount if classID else 1
                self._instructorSlots.append(instrSlot)

            if slotsCount > maxInstructorSlots:
                _xml.raiseWrongXml(xmlCtx, '', "Detachment '{}'. Detachments cannot have more than {} instructor slots (capacity={})".format(self._name, maxInstructorSlots, slotsCount))
            return

    def __validate(self, xmlCtx, settingsLocator):
        self.__validateMatrix(xmlCtx, settingsLocator)
        self.__validateProgression(xmlCtx, settingsLocator)
        self.__validateCommander(xmlCtx, settingsLocator)
        self.__validateInstructors(xmlCtx, settingsLocator)
        self.__validateVehicles(xmlCtx, settingsLocator)

    def __validateMatrix(self, xmlCtx, settingsLocator):
        perkMatrix = settingsLocator.perkSettings.matrices.getMatrix(self._matrixID)
        if perkMatrix is None:
            _xml.raiseWrongXml(xmlCtx, '', "Detachment '{}'. matrixID {} does not exist".format(self._name, self._matrixID))
        return

    def __validateProgression(self, xmlCtx, settingsLocator):
        prog = settingsLocator.detachmentSettings.progression.getProgressionByID(self._progressionID)
        if not prog:
            _xml.raiseWrongXml(xmlCtx, '', "Detachment '{}' specifies non-existing 'progressionID'".format(self._name))

    def __validateCommander(self, xmlCtx, settingsLocator):
        if self._commander is None:
            return
        else:
            if self._nationID is None:
                self.__validateCommanderNoNation(xmlCtx)
            else:
                self.__validateCommanderWithNation(xmlCtx, settingsLocator)
            return

    def __validateCommanderNoNation(self, xmlCtx):
        cmdr = self._commander
        if cmdr.firstNameID is not None or cmdr.secondNameID is not None or cmdr.portraitID is not None:
            _xml.raiseWrongXml(xmlCtx, '', "Detachment '{}' commander without nation must not have firstNameID/secondNameID or portraitID specified".format(self._name))
        return

    def __validateCommanderWithNation(self, xmlCtx, settingsLocator):
        cmdr = self._commander
        cmdrPool = settingsLocator.characterProperties
        cmdrGender = BOOL_TO_GENDER.get(cmdr.isFemale)
        genderTag = GENDER_TO_TAG[cmdrGender]
        if cmdrGender is None and (cmdr.firstNameID is not None or cmdr.secondNameID is not None or cmdr.portraitID is not None):
            _xml.raiseWrongXml(xmlCtx, '', "Detachment '{}' commander must have its gender specified, because it has firstNameID, secondNameID or portraitID".format(self._name))
        if cmdr.firstNameID is not None:
            if cmdrPool.getFirstNameByID(self._nationID, cmdr.firstNameID, gender=cmdrGender) is None:
                _xml.raiseWrongXml(xmlCtx, '', "Detachment '{}'. Commander. FirstNameID {} of gender '{}' does not exist".format(self._name, cmdr.firstNameID, genderTag))
        if cmdr.secondNameID is not None:
            if cmdrPool.getSecondNameByID(self._nationID, cmdr.secondNameID, gender=cmdrGender) is None:
                _xml.raiseWrongXml(xmlCtx, '', "Detachment '{}'. Commander. SecondNameID {} of gender '{}' does not exist".format(self._name, cmdr.secondNameID, genderTag))
        if cmdr.portraitID is not None:
            if cmdrPool.getPortraitByID(self._nationID, cmdr.portraitID, gender=cmdrGender) is None:
                _xml.raiseWrongXml(xmlCtx, '', "Detachment '{}'. Commander. PortraitID {} of gender '{}' does not exist".format(self._name, cmdr.portraitID, genderTag))
        return

    def __validateInstructors(self, xmlCtx, settingsLocator):
        if self._instructorSlots is None:
            return
        else:
            hasFilledSlots = any((x.instructorID is not None for x in self._instructorSlots))
            if hasFilledSlots and self._nationID is None:
                _xml.raiseWrongXml(xmlCtx, '', "Detachment '{}'. Specifying instructors is not allowed without specifying detachment nation".format(self._name))
            if self._lockMask is not None and self._lockMask & DetachmentLockMaskBits.INSTRUCTORS:
                hasEmptyUnlockedSlots = any((x.instructorID is None for x in self._instructorSlots))
                if hasEmptyUnlockedSlots:
                    _xml.raiseWrongXml(xmlCtx, '', "Detachment '{}'. Locking empty instructor slots with <customizeLock>instructors</> is not allowed".format(self._name))
            prov = settingsLocator.instructorSettingsProvider
            for slot in self._instructorSlots:
                if slot.instructorID is None:
                    continue
                instrSetting = prov.getInstructorByID(slot.instructorID)
                if self._nationID not in instrSetting.getAvailableNations():
                    _xml.raiseWrongXml(xmlCtx, '', "Detachment '{}'. Instructor '{}' not allowed for nation '{}'".format(self._name, instrSetting.name, nations.NAMES[self._nationID]))

            return

    def __validateVehicles(self, xmlCtx, settingsLocator):
        maxVehSlots = settingsLocator.detachmentSettings.maxVehicleSlots
        if maxVehSlots < self._maxVehicleSlots < 1:
            _xml.raiseWrongXml(xmlCtx, '', "Detachment '{}', maxVehicleSlots out of range [1, {}]".format(self._name, maxVehSlots))
        if self._vehicleSlots is None:
            return
        else:
            hasFilledSlots = any((x.vehicleCD is not None for x in self._vehicleSlots))
            if hasFilledSlots and self._nationID is None:
                _xml.raiseWrongXml(xmlCtx, '', "Detachment '{}'. Specifying vehicles is not allowed without specifying detachment nation".format(self._name))
            if self._lockMask is not None and self._lockMask & DetachmentLockMaskBits.VEHICLE_SLOTS:
                hasEmptyUnlockedSlots = any((x.vehicleCD is None for x in self.vehicleSlots))
                if hasEmptyUnlockedSlots:
                    _xml.raiseWrongXml(xmlCtx, '', "Detachment '{}'. Locking empty vehicle slots with <customizeLock>vehicle_slots</> is not allowed".format(self._name))
            for slot in self._vehicleSlots:
                if slot.vehicleCD is None:
                    continue
                vehicleType = getVehicleType(slot.vehicleCD)
                if vehicleType.isPremium():
                    _xml.raiseWrongXml(xmlCtx, '', "Detachment '{}'. Vehicle '{}' is premium ".format(self._name, vehicleType.name))
                if self._nationID != vehicleType.nation:
                    _xml.raiseWrongXml(xmlCtx, '', "Detachment '{}'. Vehicle '{}' nation does not match detachment nation '{}'".format(self._name, vehicleType.name, nations.NAMES[self._nationID]))

            return
