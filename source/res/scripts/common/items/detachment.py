# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/detachment.py
import struct
import weakref
from collections import namedtuple
from bisect import bisect_right
from itertools import izip_longest
from typing import TYPE_CHECKING, Tuple, List, Dict, Any, Iterable, Optional
from cache import cached_property
from crew2.crew2_consts import BOOL_TO_GENDER
from items.components.detachment_slots_traits import VehiclesSlotsTraits, InstructorsSlotsTraits
from items.components.perks_constants import PERKS_TYPE
from items.instructor import InstructorDescr
from items import ITEM_TYPES, vehicles
from items.utils.common import SoftAssert, getEnumValues
from crew2 import settings_globals
from items.components.detachment_constants import DetachmentAttrs, DetachmentLockMaskBits, DetachmentSlotType, PerksOperationResultCode, DropSkillPaymentOption, INVALID_INSTRUCTOR_SLOT_ID, DROP_SKILL_PAYMENT_OPTIONS, BADGE_TOKEN_TMPL, SpecializationPaymentType, NO_INSTRUCTOR_ID, RewardTypes, MAX_LONG
from items.components.detachment_components import generate, validate, validatePropertyLock, addPerksToBuild, packPerks, unpackPerks, packIDs, unpackIDs, getVehicleIdentification, setCtxAttrIfNotNone, isPerksRepartition, getBranchPointsAndTalents, getFilteredBuild
from items.utils.common import spliceCompDescr, setBit, getBit
from items.utils.detachment import DETACHMENT_VALIDATORS, DETACHMENT_GENERATORS
from crew2.detachment.progression_record import ProgressionState
if TYPE_CHECKING:
    from items.components.detachment_constants import PerksOperationResult
    from crew2.detachment.progression_record import ProgressionRecord
    from items.tankmen import TankmanDescr
SlotInfo = namedtuple('SlotInfo', ['available', 'locked', 'typeCompDescr'])

class DetachmentDescr(object):
    __slots__ = getEnumValues(DetachmentAttrs) + ['__dict__', '__weakref__']

    def __init__(self):
        self._presetID = None
        self._nationID = None
        self._progressionLayoutID = None
        self._perksMatrixID = None
        self._classID = None
        self._lockMask = None
        self._operationsMask = None
        self._maxVehicleSlots = None
        self._vehicleSlots = None
        self._instructorSlots = None
        self._activeInstructorSlotID = None
        self._build = None
        self._experience = None
        self._isFemale = None
        self._cmdrFirstNameID = None
        self._cmdrSecondNameID = None
        self._cmdrPortraitID = None
        self.__slotsTraits = [VehiclesSlotsTraits(weakref.proxy(self)), InstructorsSlotsTraits(weakref.proxy(self))]
        return

    @property
    def presetID(self):
        return self._presetID

    @property
    def nationID(self):
        return self._nationID

    @property
    def progressionLayoutID(self):
        return self._progressionLayoutID

    @cached_property
    def progression(self):
        progressionSettings = settings_globals.g_detachmentSettings.progression
        return progressionSettings.getProgressionByID(self._progressionLayoutID)

    @cached_property
    def rawLevel(self):
        return self.progression.getRawLevelByXP(self._experience)

    @property
    def perksMatrixID(self):
        return self._perksMatrixID

    @property
    def lockMask(self):
        return self._lockMask

    @property
    def operationsMask(self):
        return self._operationsMask

    @property
    def build(self):
        return self._build

    @property
    def experience(self):
        return self._experience

    @property
    def isGarbage(self):
        return self.experience < settings_globals.g_detachmentSettings.garbageThreshold

    @property
    def level(self):
        return min(self.rawLevel, self.progression.maxLevel)

    @property
    def masteryLevel(self):
        return max(0, self.rawLevel - self.progression.maxLevel)

    @property
    def hasMaxLevel(self):
        return self.level == self.progression.maxLevel

    @property
    def hasMaxMasteryLevel(self):
        return self.masteryLevel == self.progression.maxMasteryLevel

    @property
    def milestone(self):
        return self.progression.getMilestone(self.rawLevel)

    @property
    def levelIcon(self):
        return self.progression.getLevelIconByXP(self._experience)

    @property
    def rank(self):
        return self.progression.getRankByXP(self._experience)

    @property
    def badgeToken(self):
        badgeID = self.progression.badgeID
        return BADGE_TOKEN_TMPL.format(badgeID) if badgeID else None

    @property
    def badgeLevel(self):
        return self.progression.getBadgeLevelByXP(self._experience)

    @property
    def autoPerks(self):
        return self.progression.getAutoPerksByXP(self._experience)

    @property
    def classID(self):
        return self._classID

    @property
    def maxVehicleSlots(self):
        return self._maxVehicleSlots

    @property
    def cmdrFirstNameID(self):
        return self._cmdrFirstNameID

    @property
    def cmdrSecondNameID(self):
        return self._cmdrSecondNameID

    @property
    def cmdrPortraitID(self):
        return self._cmdrPortraitID

    @property
    def isFemale(self):
        return self._isFemale

    @property
    def maxInstructorsCount(self):
        return len(self.progression.instructorUnlockLevels)

    def getFilteredBuild(self, select=PERKS_TYPE.ANY):
        return getFilteredBuild(self.getPerksMatrix(), self._build, select)

    def getLockMaskBit(self, flag):
        return False if self._lockMask is None else self._lockMask & flag != 0

    def getSlotsCount(self, slotType):
        return len(self.__slotsTraits[slotType].getSlots())

    def isSlotAvailable(self, slotType, slotIndex):
        return slotIndex < self.getSlotsCount(slotType)

    def isSlotLocked(self, slotsType, slotIndex):
        slotsTraits = self.__slotsTraits[slotsType]
        return getBit(self.lockMask, slotsTraits.getMask(), slotIndex)

    def getSlotValue(self, slotsType, slotIndex):
        slots = self.__slotsTraits[slotsType].getSlots()
        SoftAssert(slotIndex < len(slots), 'wrong slot ID %s' % slotIndex)
        return slots[slotIndex]

    def getDropSkillPaymentOption(self):
        paymentOption = (0, DropSkillPaymentOption.DEFAULT)
        for option in DROP_SKILL_PAYMENT_OPTIONS:
            if getBit(self.operationsMask, option[0]):
                paymentOption = option

        return paymentOption

    def getSpecializeVehicleSlotFineXP(self, xpMult):
        level = min(self.rawLevel, self.progression.maxLevel)
        nextLevelXP = self.progression.getLevelStartingXP(level + 1)
        fine = int(round((nextLevelXP - self.progression.getLevelStartingXP(level)) * xpMult))
        return min(self._experience, fine)

    def iterSlots(self, slotsType, getLockFlag=False, skipNone=False, skipDuplicated=False):
        slotsTraits = self.__slotsTraits[slotsType]
        slots = slotsTraits.getSlots()
        for i, val in enumerate(slots):
            if val is None and skipNone:
                continue
            if skipDuplicated and i > 0 and slots[i] is not None and slots[i - 1] == slots[i]:
                continue
            if getLockFlag:
                yield (val, getBit(self.lockMask, slotsTraits.getMask(), i))
            yield val

        return

    def isValueInSlotsLocked(self, slotType, val):
        return any((val == slotVal and self.isSlotLocked(slotType, i) for i, slotVal in enumerate(self.iterSlots(slotType))))

    def getAllSlotsInfo(self, slotsType):
        res = []
        slotsMax = self.__slotsTraits[slotsType].getMax()
        for _, info in izip_longest(xrange(slotsMax), self.iterSlots(slotsType, getLockFlag=True), fillvalue=None):
            if info:
                res.append(SlotInfo(True, info[1], info[0]))
            res.append(SlotInfo(False, None, None))

        return tuple(res)

    @staticmethod
    def createByCompDescr(compDescr):
        newDetachment = DetachmentDescr()
        newDetachment._initByCompDescr(compDescr)
        return newDetachment

    @staticmethod
    def createByCtx(ctx):
        newDetachment = DetachmentDescr()
        newDetachment._generateByCtx(ctx)
        return newDetachment

    @staticmethod
    def createByPreset(presetName, vehCompDescr=None, instIDStartsFrom=0, overrideDetachmentCtx=None):
        vehTypeCompDescr = vehCompDescr
        if vehTypeCompDescr and not vehicles.isVehicleTypeCompactDescr(vehTypeCompDescr):
            vehTypeCompDescr = vehicles.getVehicleTypeCompactDescr(vehTypeCompDescr)
        detSettings = settings_globals.g_detachmentSettings.presets.getDetachmentPreset(presetName)
        SoftAssert(detSettings is not None, "detachment preset '{}' not found".format(presetName))
        detCtx = {DetachmentAttrs.PRESET_ID: detSettings.id,
         DetachmentAttrs.PROGRESSION_LAYOUT_ID: detSettings.progressionID,
         DetachmentAttrs.PERKS_MATRIX_ID: detSettings.matrixID}
        classID = detSettings.classID
        setCtxAttrIfNotNone(detCtx, DetachmentAttrs.EXPERIENCE, detSettings.experience)
        setCtxAttrIfNotNone(detCtx, DetachmentAttrs.MAX_VEHICLE_SLOTS, detSettings.maxVehicleSlots)
        lockMask = detSettings.lockMask or 0
        nationID = detSettings.nationID
        if detSettings.vehicleSlots:
            vehCDs = []
            for i, vehSlot in enumerate(detSettings.vehicleSlots):
                vehCDs.append(vehSlot.vehicleCD)
                lockMask = setBit(lockMask, DetachmentLockMaskBits.VEHICLE_SLOTS, i, not vehSlot.canRespecialize)
                if vehSlot.vehicleCD:
                    vehIdent = getVehicleIdentification(vehSlot.vehicleCD)
                    SoftAssert(classID is None or classID == vehIdent.classID, 'vehicle classes is different or not equal to passed classID')
                    classID = vehIdent.classID

            detCtx[DetachmentAttrs.CLASS_ID] = classID
            detCtx[DetachmentAttrs.VEHICLE_SLOTS] = vehCDs
            SoftAssert(vehTypeCompDescr is None or vehTypeCompDescr in vehCDs, "binding vehicle is not in detachment preset '{}'".format(presetName))
        elif vehTypeCompDescr is not None:
            vehIdent = getVehicleIdentification(vehTypeCompDescr)
            if not vehIdent.isPremium:
                detCtx[DetachmentAttrs.VEHICLE_SLOTS] = [vehTypeCompDescr]
            SoftAssert(nationID is None or nationID == vehIdent.nationID, 'preset nation and vehicle nation not equal (preset: {})'.format(presetName))
            SoftAssert(classID is None or classID == vehIdent.classID, 'preset class and vehicle class not equal (preset: {})'.format(presetName))
            nationID = vehIdent.nationID
            classID = vehIdent.classID
        else:
            SoftAssert(False, "can't create detachment with no vehicles (preset: {})".format(presetName))
        SoftAssert(nationID is not None, "can't create detachment with no nation (preset: {})".format(presetName))
        detCtx[DetachmentAttrs.NATION_ID] = nationID
        SoftAssert(classID is not None, "can't create detachment with no class (preset: {})".format(presetName))
        detCtx[DetachmentAttrs.CLASS_ID] = classID
        instructorsCount = len(detSettings.instructorSlots) if detSettings.instructorSlots is not None else 0
        slots = 0
        if instructorsCount > 0:
            instrSettingsProvider = settings_globals.g_instructorSettingsProvider
            maxInstructorSlots = settings_globals.g_detachmentSettings.maxInstructorSlots
            index = 0
            for instructor in detSettings.instructorSlots:
                instructorClass = instrSettingsProvider.classes.getClassByID(instructor.classID)
                capacitySlot = instructorClass.slotsCount if instructorClass else 1
                slots += capacitySlot
                SoftAssert(maxInstructorSlots >= slots, "can't create detachment, because numbers of instructor slots more then maxInstructorSlots")
                for _ in xrange(capacitySlot):
                    lockMask = setBit(lockMask, DetachmentLockMaskBits.INSTRUCTORS, index, not instructor.canRemove)
                    index += 1

        detCtx[DetachmentAttrs.INSTRUCTOR_SLOTS] = [None] * slots
        detCtx[DetachmentAttrs.LOCK_MASK] = lockMask
        setCtxAttrIfNotNone(detCtx, DetachmentAttrs.OPERATIONS_MASK, detSettings.operationMask)
        commander = detSettings.commander
        setCtxAttrIfNotNone(detCtx, DetachmentAttrs.IS_FEMALE, getattr(commander, 'isFemale', None))
        setCtxAttrIfNotNone(detCtx, DetachmentAttrs.CMDR_FIRST_NAME_ID, getattr(commander, 'firstNameID', None))
        setCtxAttrIfNotNone(detCtx, DetachmentAttrs.CMDR_SECOND_NAME_ID, getattr(commander, 'secondNameID', None))
        setCtxAttrIfNotNone(detCtx, DetachmentAttrs.CMDR_PORTRAIT_ID, getattr(commander, 'portraitID', None))
        if overrideDetachmentCtx:
            detCtx.update(overrideDetachmentCtx)
        detDescr = DetachmentDescr.createByCtx(detCtx)
        detInstructors = []
        if instructorsCount > 0:
            indexSlot = idx = 0
            for instSlot in detSettings.instructorSlots:
                instSettID = instSlot.instructorID
                if instSettID is None:
                    continue
                instSettings = settings_globals.g_instructorSettingsProvider.getInstructorByID(instSettID)
                SoftAssert(instSettings is not None, 'instructor settings #{} not found.(detachment preset: {}'.format(instSettID, presetName))
                instrDescr = InstructorDescr.createByPreset(instSettings.name, nationID=nationID)
                instInvID = instIDStartsFrom + idx
                idx += 1
                detInstructors.append((instInvID, instrDescr))
                detDescr.setSlotValue(DetachmentSlotType.INSTRUCTORS, indexSlot, (instInvID, instrDescr), skipLockMask=True)
                indexSlot += instrDescr.getSlotsCount()

        return (detDescr, detInstructors)

    def makeCompactDescr(self):
        self._validateDetachment()
        xpIsLongLong = self.experience > MAX_LONG
        header = ITEM_TYPES.detachment + (self._nationID << 4)
        flags = int(self.isFemale) | int(xpIsLongLong) << 1
        cd = struct.pack('<7B', header, flags, self._presetID, self._perksMatrixID, self._classID, self._operationsMask, self._maxVehicleSlots)
        cd += struct.pack('<2H', self._lockMask, self._progressionLayoutID)
        cd += struct.pack('<3H', self._cmdrFirstNameID, self._cmdrSecondNameID, self._cmdrPortraitID)
        if xpIsLongLong:
            cd += struct.pack('<Qb', self._experience, self._activeInstructorSlotID)
        else:
            cd += struct.pack('<Lb', self._experience, self._activeInstructorSlotID)
        cd += packPerks(self._build)
        cd += packIDs(self._vehicleSlots, slots=True)
        cd += packIDs(self._instructorSlots, slots=True)
        return cd

    def unlockNextSlot(self, slotType, quiet=False):
        slotTraits = self.__slotsTraits[slotType]
        slots = slotTraits.getSlots()
        count = len(slots)
        overMaxCount = count + 1 > slotTraits.getMax()
        if overMaxCount and quiet:
            return
        else:
            SoftAssert(not overMaxCount, 'maximum slots reached (type: {})'.format(slotType))
            nextSlotLocked = getBit(self.lockMask, slotTraits.getMask(), count)
            if nextSlotLocked and quiet:
                return
            SoftAssert(not nextSlotLocked, "slot #'{}' is locked".format(count))
            slots.append(None)
            return count

    def setSlotValue(self, slotType, slotID, value, validate=True, skipLockMask=False):
        slotTraits = self.__slotsTraits[slotType]
        slotTraits.setSlotValue(slotID, value, validate=validate, skipLockMask=skipLockMask)

    def canSetSlotValue(self, slotType, slotID, value, skipLockMask=False):
        slotTraits = self.__slotsTraits[slotType]
        return slotTraits.canSetSlotValue(slotID, value, skipLockMask=skipLockMask)

    def setActiveInstructorSlotID(self, slotID):
        if self.isSlotAvailable(DetachmentSlotType.INSTRUCTORS, slotID):
            self._activeInstructorSlotID = slotID
        else:
            SoftAssert(False, 'slot #{} is not available'.format(slotID))

    def resetClassAndVehicleSlots(self, classID=None):
        self._vehicleSlots = [None] * len(self._vehicleSlots)
        self._classID = classID
        return

    def swapSlotsValues(self, slotsType, slotIndex1, slotIndex2):
        slotTraits = self.__slotsTraits[slotsType]
        slotTraits.swapSlotsValues(slotIndex1, slotIndex2, self.getAllSlotsInfo(slotsType))

    def moveInstructor(self, slotIndex1, steps):
        slotTraits = self.__slotsTraits[DetachmentSlotType.INSTRUCTORS]
        slotTraits.move(slotIndex1, steps)

    def areClassesEquals(self, vehTypeCompDescr):
        return self.classID == getVehicleIdentification(vehTypeCompDescr).classID

    def addPerks(self, perksDict):
        validatePropertyLock(self, DetachmentLockMaskBits.BUILD)
        if isPerksRepartition(self._build, perksDict):
            validatePropertyLock(self, DetachmentLockMaskBits.DROP_SKILL)
        res = addPerksToBuild(self._build, self._perksMatrixID, self.level, perksDict)
        if res.code == PerksOperationResultCode.NO_ERROR:
            self._build = res.build
        return res

    def dropPerks(self):
        validatePropertyLock(self, DetachmentLockMaskBits.BUILD)
        validatePropertyLock(self, DetachmentLockMaskBits.DROP_SKILL)
        self._build = {}

    def addXP(self, xp):
        return self._modifyXP(xp)

    def addXPByPercent(self, expMult):
        xp = int(round(self._experience * expMult))
        return self._modifyXP(xp)

    def subXP(self, xp):
        return self._modifyXP(-xp)

    def subXPByPercent(self, expMult):
        xp = int(round(self._experience * expMult))
        return self._modifyXP(-xp)

    def getCurrentLevelXP(self):
        return self._experience - self.progression.getLevelStartingXP(self.rawLevel)

    def getNextLevelXPGoal(self):
        if self.hasMaxMasteryLevel:
            return 1
        nextLevelXP = self.progression.getLevelStartingXP(self.rawLevel + 1)
        return nextLevelXP - self.progression.getLevelStartingXP(self.rawLevel)

    def getCurrentLevelXPProgress(self):
        return 1.0 if self.hasMaxMasteryLevel else float(self.getCurrentLevelXP()) / self.getNextLevelXPGoal()

    def getProgressionRewards(self, prevState, nextState=None):
        prevState = prevState or self.progressionState
        nextState = nextState or self.progressionState
        return {RewardTypes.SKILL_POINTS: nextState.level - prevState.level,
         RewardTypes.RANK: nextState.rank if nextState.rank != prevState.rank else None,
         RewardTypes.BADGE_LEVEL: nextState.badgeLevel if nextState.badgeLevel != prevState.badgeLevel else None,
         RewardTypes.AUTO_PERKS: (prevState.autoPerks, nextState.autoPerks),
         RewardTypes.INSTRUCTOR_SLOTS: (max(0, nextState.instructorSlots - prevState.instructorSlots), max(nextState.instructorSlots, prevState.instructorSlots)),
         RewardTypes.VEHICLE_SLOTS: (max(0, nextState.vehicleSlots - prevState.vehicleSlots), max(nextState.vehicleSlots, prevState.vehicleSlots)),
         RewardTypes.SCHOOL_DISCOUNT: nextState.schoolDiscount if nextState.schoolDiscount != prevState.schoolDiscount else None,
         RewardTypes.ACADEMY_DISCOUNT: nextState.academyDiscount if nextState.academyDiscount != prevState.academyDiscount else None}

    @property
    def progressionState(self):
        xp = self._experience
        return ProgressionState(level=self.level, rank=self.rank, badgeLevel=self.badgeLevel, autoPerks=self.autoPerks, instructorSlots=self.getSlotsCount(DetachmentSlotType.INSTRUCTORS), vehicleSlots=self.getSlotsCount(DetachmentSlotType.VEHICLES), schoolDiscount=self.progression.getSpecializationDiscountByXP(SpecializationPaymentType.SILVER, xp), academyDiscount=self.progression.getSpecializationDiscountByXP(SpecializationPaymentType.GOLD, xp))

    def getPerksMatrix(self):
        return settings_globals.g_perkSettings.matrices.getMatrix(self.perksMatrixID)

    def getBuildLevel(self):
        points = getBranchPointsAndTalents(self.getPerksMatrix(), self._build)
        return points.totalPoints

    @staticmethod
    def getDetachmentXPFromVehicleCrew(crew):
        sumXP = 0
        tmenXP = {}
        crewLen = len(crew)
        for tmanDescr in crew:
            if tmanDescr is not None:
                xp = tmanDescr.getConvertibleXP(cutMinRoleLevel=True) / crewLen
                tmenXP[tmanDescr.compactDescr] = xp
                sumXP += xp

        return (sumXP, tmenXP)

    def getInstructorSlotIDByInvID(self, instInvID):
        return self._instructorSlots.index(instInvID) if instInvID in self._instructorSlots else INVALID_INSTRUCTOR_SLOT_ID

    def getActiveInstructorInvID(self):
        return self.getSlotValue(DetachmentSlotType.INSTRUCTORS, self._activeInstructorSlotID) if self._activeInstructorSlotID != INVALID_INSTRUCTOR_SLOT_ID and self.isSlotAvailable(DetachmentSlotType.INSTRUCTORS, self._activeInstructorSlotID) else NO_INSTRUCTOR_ID

    def changeOperationsMask(self, bit, value):
        self._operationsMask = setBit(self._operationsMask, bit, positive=value)
        return self._operationsMask

    def getOperationMaskBit(self, bit):
        return getBit(self._operationsMask, bit)

    def setOperationsMask(self, value):
        self._operationsMask = value

    def setLockMask(self, lockMask):
        self._lockMask = lockMask

    def changeIsFemale(self, isFemale):
        self._isFemale = isFemale

    def changeFirstName(self, nameID):
        gender = BOOL_TO_GENDER[self.isFemale]
        SoftAssert(nameID in settings_globals.g_characterProperties.getCommonFirstNameIDs(self.nationID, gender), "First name isn't in names list")
        validatePropertyLock(self, DetachmentLockMaskBits.COMMANDER_CUSTOMIZATION)
        self._cmdrFirstNameID = nameID

    def changeSecondName(self, nameID):
        gender = BOOL_TO_GENDER[self.isFemale]
        SoftAssert(nameID in settings_globals.g_characterProperties.getCommonSecondNameIDs(self.nationID, gender), "Second name isn't in names list")
        validatePropertyLock(self, DetachmentLockMaskBits.COMMANDER_CUSTOMIZATION)
        self._cmdrSecondNameID = nameID

    def changePortrait(self, portraitID):
        gender = BOOL_TO_GENDER[self.isFemale]
        SoftAssert(portraitID in settings_globals.g_characterProperties.getCommonPortraitIDs(self.nationID, gender), "Portrait id isn't in names list")
        validatePropertyLock(self, DetachmentLockMaskBits.COMMANDER_CUSTOMIZATION)
        self._cmdrPortraitID = portraitID

    def _modifyXP(self, xpVal):
        SoftAssert(isinstance(xpVal, (int, long)), 'experience can not be float')
        resXp = self._experience + xpVal
        SoftAssert(resXp >= 0, 'experience can not be negative')
        oldRawLevel = self.rawLevel
        self._experience = resXp
        self._invalidateCachedProperties(self.__class__.rawLevel)
        levelChanged = cmp(self.rawLevel, oldRawLevel)
        if levelChanged:
            self._unlockSlotsByLevel()
        return levelChanged

    def _initByCompDescr(self, compDescr):
        SoftAssert(compDescr is not None, 'compact descriptor is None')
        cdPart, offset = spliceCompDescr(compDescr, 0, 1)
        header = struct.unpack('<B', cdPart)
        SoftAssert(header & 15 == ITEM_TYPES.detachment, 'not suitable compact descriptor')
        self._nationID = header >> 4 & 15
        cdPart, offset = spliceCompDescr(compDescr, offset, 4)
        flags, self._presetID, self._perksMatrixID, self._classID = struct.unpack('<4B', cdPart)
        cdPart, offset = spliceCompDescr(compDescr, offset, 2)
        self._operationsMask, self._maxVehicleSlots = struct.unpack('<2B', cdPart)
        self._isFemale = bool(flags & 1)
        xpIsLongLong = bool(flags >> 1 & 1)
        cdPart, offset = spliceCompDescr(compDescr, offset, 4)
        self._lockMask, self._progressionLayoutID = struct.unpack('<2H', cdPart)
        cdPart, offset = spliceCompDescr(compDescr, offset, 6)
        self._cmdrFirstNameID, self._cmdrSecondNameID, self._cmdrPortraitID = struct.unpack('<3H', cdPart)
        if xpIsLongLong:
            cdPart, offset = spliceCompDescr(compDescr, offset, 9)
            self._experience, self._activeInstructorSlotID = struct.unpack('<Qb', cdPart)
        else:
            cdPart, offset = spliceCompDescr(compDescr, offset, 5)
            self._experience, self._activeInstructorSlotID = struct.unpack('<Lb', cdPart)
        self._build, offset = unpackPerks(compDescr, offset)
        self._vehicleSlots, offset = unpackIDs(compDescr, offset, slots=True)
        self._instructorSlots, offset = unpackIDs(compDescr, offset, slots=True)
        self._invalidateCachedProperties()
        return

    def _generateByCtx(self, ctx):
        generate(DETACHMENT_GENERATORS, self, ctx, self)
        self._invalidateCachedProperties()
        self._validateDetachment()

    def _invalidateCachedProperties(self, *args):
        props = args or (self.__class__.progression, self.__class__.rawLevel)
        for prop in props:
            SoftAssert(isinstance(prop, cached_property), 'only cached property could be invalidated')
            self.__dict__.pop(prop.name, None)

        return

    def _validateDetachment(self):
        validate(DETACHMENT_VALIDATORS, self, False)

    def _unlockSlotsByLevel(self):
        self._unlockSlotByLevel(DetachmentSlotType.INSTRUCTORS, self.progression.instructorUnlockLevels)
        self._unlockSlotByLevel(DetachmentSlotType.VEHICLES, self.progression.vehicleSlotUnlockLevels)

    def _unlockSlotByLevel(self, slotType, progressionLevels):
        slotsCount = self.getSlotsCount(slotType)
        newSlotsCount = bisect_right(progressionLevels, self.level)
        for i in range(slotsCount, newSlotsCount):
            self.unlockNextSlot(slotType, quiet=True)
