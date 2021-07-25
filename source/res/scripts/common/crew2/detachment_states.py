# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/crew2/detachment_states.py
import math
import time
from itertools import izip
from typing import TYPE_CHECKING, Tuple, Optional, Set, Dict, List
from constants import VEHICLE_CLASS_INDICES
from crew2 import settings_globals
from items import vehicles
from items.components.detachment_components import getHours, isSuitableVehicleForSlotByType, mergePerks, applyBonusPerks, PerkBonusInfluenceItem, PerkBonusApplier
from items.components.detachment_constants import DetachmentSlotType
from items.detachment import DetachmentDescr
from items.instructor import InstructorDescr
if TYPE_CHECKING:
    from detachment_inventory_proxy import IInventoryProxy

class CanProcessDetachmentResult(object):
    OK = 0
    DETACHMENT_LOCKED = 1
    DETACHMENT_LOCKED_BY_LOCK_CREW = 2
    DETACHMENT_DISSOLVED = 3
    MAX = DETACHMENT_DISSOLVED


CAN_PROCESS_DETACHMENT_RESULT_TO_STR = {CanProcessDetachmentResult.OK: '',
 CanProcessDetachmentResult.DETACHMENT_LOCKED: 'detachment is locked',
 CanProcessDetachmentResult.DETACHMENT_LOCKED_BY_LOCK_CREW: 'detachment locked by lockCrew',
 CanProcessDetachmentResult.DETACHMENT_DISSOLVED: 'detachment is dissolved'}

class CanAddInstructorResult(CanProcessDetachmentResult):
    ALREADY_ASSIGNED = CanProcessDetachmentResult.MAX + 1
    INSTRUCTOR_IS_TOKEN = CanProcessDetachmentResult.MAX + 2


CAN_ADD_INSTRUCTOR_RESULT_STR = {CanAddInstructorResult.ALREADY_ASSIGNED: 'instructor already assigned to detachment',
 CanAddInstructorResult.INSTRUCTOR_IS_TOKEN: 'instructor is token'}
CAN_ADD_INSTRUCTOR_RESULT_STR.update(CAN_PROCESS_DETACHMENT_RESULT_TO_STR)

class CanRemoveInstructorResult(CanProcessDetachmentResult):
    INSTRUCTOR_NOT_IN_DETACHMENT = 4


CAN_REMOVE_INSTRUCTOR_RESULT_STR = {CanRemoveInstructorResult.INSTRUCTOR_NOT_IN_DETACHMENT: 'instructor not in given detachment'}
CAN_REMOVE_INSTRUCTOR_RESULT_STR.update(CAN_PROCESS_DETACHMENT_RESULT_TO_STR)

class CanAssignResult(CanProcessDetachmentResult):
    VEHICLE_LOCKED = CanProcessDetachmentResult.MAX + 1
    VEHICLE_HAS_LOCK_CREW = CanProcessDetachmentResult.MAX + 2
    VEHICLE_HAS_OLD_CREW = CanProcessDetachmentResult.MAX + 3
    WRONG_NATION = CanProcessDetachmentResult.MAX + 4
    WRONG_CLASS = CanProcessDetachmentResult.MAX + 5
    NON_SUITABLE_TYPE = CanProcessDetachmentResult.MAX + 6
    SAME_VEHICLE = CanProcessDetachmentResult.MAX + 7


CAN_ASSIGN_DETACHMENT_TO_VEHICLE_RESULT_STR = {CanAssignResult.VEHICLE_LOCKED: 'vehicle is locked',
 CanAssignResult.VEHICLE_HAS_LOCK_CREW: 'vehicle has lockCrew',
 CanAssignResult.VEHICLE_HAS_OLD_CREW: 'vehicle has old crew',
 CanAssignResult.WRONG_NATION: 'vehicle with non suitable nation',
 CanAssignResult.WRONG_CLASS: 'vehicle with non suitable class',
 CanAssignResult.NON_SUITABLE_TYPE: 'vehicle with non suitable type',
 CanAssignResult.SAME_VEHICLE: 'vehicle is the same'}
CAN_ASSIGN_DETACHMENT_TO_VEHICLE_RESULT_STR.update(CAN_PROCESS_DETACHMENT_RESULT_TO_STR)

class DetachmentStates(object):

    def __init__(self, proxy):
        super(DetachmentStates, self).__init__()
        self._proxy = proxy

    def canProcessDetachment(self, detInvID, checkLockCrew=True, lockVehicleReasonToIgnore=None):
        if self.isDetachmentLocked(detInvID, lockVehicleReasonToIgnore):
            return CanProcessDetachmentResult.DETACHMENT_LOCKED
        if checkLockCrew and self.isDetachmentLockedByLockCrew(detInvID):
            return CanProcessDetachmentResult.DETACHMENT_LOCKED_BY_LOCK_CREW
        return CanProcessDetachmentResult.DETACHMENT_DISSOLVED if self.isDetachmentDissolved(detInvID) else CanProcessDetachmentResult.OK

    def isDetachmentLocked(self, detInvID, lockVehicleReasonToIgnore=None):
        vehInvID = self.getDetachmentToVehicleLink(detInvID)
        return vehInvID is not None and self._proxy.isVehicleLocked(vehInvID, lockVehicleReasonToIgnore)

    def isDetachmentLockedByLockCrew(self, detInvID):
        vehCompDescr = self._proxy.getVehicleCompDescr(self.getDetachmentToVehicleLink(detInvID))
        return False if vehCompDescr is None else vehicles.getVehicleType(vehCompDescr).isLockCrew()

    def isDetachmentRestorable(self, detInvID, detDescr, sellVehicle):
        vehCompDescr = self._proxy.getVehicleCompDescr(self.getDetachmentToVehicleLink(detInvID))
        res = not detDescr.isGarbage
        return res and not vehicles.getVehicleType(vehCompDescr).isLockCrew() if vehCompDescr and sellVehicle else res

    def isDetachmentDissolved(self, detInvID):
        return detInvID in self._proxy.detsRecycleBin

    def canAssignDetachmentToVehicle(self, detInvID, vehInvID):
        res = self.canProcessDetachment(detInvID, checkLockCrew=True)
        if res != CanAssignResult.OK:
            return res
        return CanAssignResult.SAME_VEHICLE if vehInvID == self.getDetachmentToVehicleLink(detInvID) else self.canAssignDetachmentDescrToVehicle(self.__getDetachmentDescrByInvID(detInvID), vehInvID)

    def canAssignDetachmentDescrToVehicle(self, detDescr, vehInvID):
        proxy = self._proxy
        vehCompDescr = proxy.validateGetVehicle(vehInvID)
        if proxy.isVehicleLocked(vehInvID):
            return CanAssignResult.VEHICLE_LOCKED
        vehicleType = vehicles.getVehicleType(vehCompDescr)
        if vehicleType.isLockCrew():
            return CanAssignResult.VEHICLE_HAS_LOCK_CREW
        if proxy.isVehicleHasCrew(vehInvID):
            return CanAssignResult.VEHICLE_HAS_OLD_CREW
        if detDescr.nationID != vehicleType.nation:
            return CanAssignResult.WRONG_NATION
        if detDescr.classID != VEHICLE_CLASS_INDICES[vehicles.getVehicleClassFromVehicleType(vehicleType)]:
            return CanAssignResult.WRONG_CLASS
        return CanAssignResult.OK if vehicleType.isPremium() or isSuitableVehicleForSlotByType(vehCompDescr, detDescr) else CanAssignResult.NON_SUITABLE_TYPE

    def getDetachmentVehicleTags(self, detInvID):
        vehCompDescr = self._proxy.getVehicleCompDescr(self.getDetachmentToVehicleLink(detInvID))
        return vehicles.getVehicleType(vehCompDescr).tags if vehCompDescr else set()

    def getDetachmentToVehicleLink(self, detInvID):
        return next((vehID for vehID, detID in self._proxy.detsVehicle.iteritems() if detID == detInvID), None)

    def getDetachmentExpDate(self, detInvID):
        return self._proxy.detsRecycleBin.get(detInvID, 0.0)

    def getExcludedInstructorExpDate(self, instInvID):
        info = self._proxy.getExcludedInstructorInfo(instInvID)
        return None if info is None else info[0]

    def getExcludedInstructorDaysLeft(self, instInvID):
        info = self._proxy.getExcludedInstructorInfo(instInvID)
        if info is None:
            return
        else:
            hours = math.ceil(getHours(info[0] - time.time()))
            hours = hours if hours >= 0 else 0
            return (hours, info[1])

    def isInstructorExcluded(self, instInvID):
        return self.getExcludedInstructorExpDate(instInvID) is not None

    def canAddInstructor(self, detInvID, instInvID):
        res = self.canProcessDetachment(detInvID)
        if res != CanProcessDetachmentResult.OK:
            return res
        else:
            detInvID = self._proxy.getDetachmentInvIDByInstructor(instInvID)
            if detInvID is not None:
                return CanAddInstructorResult.ALREADY_ASSIGNED
            instDescr = self.__getInstructorDescrByInvID(instInvID)
            return CanAddInstructorResult.INSTRUCTOR_IS_TOKEN if instDescr.isToken() else CanAddInstructorResult.OK

    def canRemoveInstructor(self, detInvID, instInvID):
        res = self.canProcessDetachment(detInvID)
        if res != CanProcessDetachmentResult.OK:
            return res
        instDetInvID = self._proxy.getDetachmentInvIDByInstructor(instInvID)
        return CanRemoveInstructorResult.INSTRUCTOR_NOT_IN_DETACHMENT if detInvID != instDetInvID else CanRemoveInstructorResult.OK

    def getDatachmentsRecycleBin(self):
        return self._proxy.detsRecycleBin

    def isRecycleBinFull(self, withExpired=False):
        if withExpired:
            count = len(self.getDatachmentsRecycleBin())
        else:
            curTime = time.time()
            count = sum((1 for expDate in self.getDatachmentsRecycleBin().itervalues() if curTime <= expDate))
        return count >= settings_globals.g_detachmentSettings.recycleBinMaxSize

    def getAbilitiesForBattle(self, detInvID, vehInvID, bonusPerks=None, outApplyHistory=None):
        if not detInvID:
            return {}
        detDescr = DetachmentDescr.createByCompDescr(self._proxy.validateGetDetachment(detInvID))
        bonusCollection = []
        self.collectInstructorBonuses(bonusCollection, detDescr)
        if vehInvID:
            self.collectBoosterBonuses(bonusCollection, vehInvID)
        return self.getAbilitiesFromCollection(detInvID, bonusCollection, bonusPerks, outApplyHistory)

    def getAbilitiesFromCollection(self, detInvID, bonusCollection, bonusPerks=None, outApplyHistory=None):
        if not detInvID:
            return {}
        detDescr = DetachmentDescr.createByCompDescr(self._proxy.validateGetDetachment(detInvID))
        perksMatrix = detDescr.getPerksMatrix().perks
        perks = mergePerks(detDescr.autoPerks, detDescr.build, bonusPerks or {})
        perks = applyBonusPerks(perks, bonusCollection, perksMatrix, outApplyHistory)
        return perks

    def collectBoosterBonuses(self, collection, vehInvID):
        equipmentsCache = vehicles.g_cache.equipments()
        vehEqs = self._proxy.getVehicleEqs(vehInvID)
        for eqCompDescr in vehEqs:
            _, _, eqID = vehicles.parseIntCompactDescr(eqCompDescr)
            eq = equipmentsCache[eqID]
            if 'crewSkillBattleBooster' in eq.tags:
                collection.append(PerkBonusInfluenceItem(PerkBonusApplier.BOOSTER, eqCompDescr, eq.perkId, eq.levelIncrease, eq.levelOvercap))

    def collectInstructorBonuses(self, collection, detDescr, extraInstructorsIDs=None):
        instructorSettingsProvider = settings_globals.g_instructorSettingsProvider
        instructors = [ (instrInvID, InstructorDescr.createByCompDescr(self._proxy.validateGetInstructor(instrInvID))) for instrInvID in detDescr.iterSlots(DetachmentSlotType.INSTRUCTORS, skipNone=True, skipDuplicated=True) ]
        extraInstructors = []
        if extraInstructorsIDs:
            extraInstructors = [ (extraInstrID, InstructorDescr.createByCompDescr(self._proxy.validateGetInstructor(extraInstrID))) for extraInstrID in extraInstructorsIDs ]
        instructors.extend(extraInstructors)
        instructors = sorted(instructors, key=lambda (_, instrDescr): instrDescr.classID)
        for instrInvID, instrDescr in instructors:
            instructorClass = instructorSettingsProvider.classes.getClassByID(instrDescr.classID)
            collection.extend((PerkBonusInfluenceItem(PerkBonusApplier.INSTRUCTOR, instrInvID, perkID, perkPoints, overcapPoints) for perkID, perkPoints, overcapPoints in izip(instrDescr.perksIDs, instructorClass.perkPoints, instructorClass.overcapPoints)))

    def __getDetachmentDescrByInvID(self, detInvID):
        return DetachmentDescr.createByCompDescr(self._proxy.validateGetDetachment(detInvID))

    def __getInstructorDescrByInvID(self, instInvID):
        return InstructorDescr.createByCompDescr(self._proxy.validateGetInstructor(instInvID))
