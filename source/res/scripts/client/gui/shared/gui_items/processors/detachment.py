# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/detachment.py
from functools import partial
import logging
import BigWorld
from constants import RECRUIT_NO_INV_ID
from gui.impl import backport
from gui.impl.auxiliary.detachment_helper import getSpecializeOptionMoney, getSpecializeOption, getDetachmentVehicleSlotMoney
from gui.shared.formatters import formatPrice
from gui.SystemMessages import SM_TYPE, FIN_TO_SM_TYPE
from gui.shared.gui_items.processors import Processor, plugins, makeI18nSuccess, makeI18nError, ItemProcessor
from gui.shared.money import Money
from gui.shared.formatters import text_styles
from helpers import dependency
from items.components.detachment_components import getVehicleIdentification
from items.components.detachment_constants import DetachmentSlotType, TypeDetachmentAssignToVehicle
from skeletons.gui.game_control import IDetachmentController
_logger = logging.getLogger(__name__)

class DetachmentCreate(Processor):

    def __init__(self, vehInvID, detCompDescr=None, assignToVehicle=True):
        super(DetachmentCreate, self).__init__(plugins=[plugins.DormitoriesSlotsValidator()])
        self.vehInvID = vehInvID
        self.detCompDescr = detCompDescr
        self.assignToVehicle = assignToVehicle
        vehicle = self.itemsCache.items.getVehicle(vehInvID)
        self.vehicleHasDetachment = vehicle.hasDetachment if vehicle else False
        self.addPlugin(plugins.VehicleLockValidator(vehicle))
        if vehicle:
            self.addPlugin(plugins.VehicleCrewLockedValidator(vehicle))

    def _errorHandler(self, code, errStr='', ctx=None):
        sysMsgKey = self._getSysMsgBase()
        sysMsgKey += '/' + errStr if errStr else '/server_error'
        return makeI18nError(sysMsgKey=sysMsgKey, defaultSysMsgKey='detachment_create/server_error')

    def _successHandler(self, code, ctx=None):
        sysMsgKey = self._getSysMsgBase() + '/success'
        return makeI18nSuccess(sysMsgKey=sysMsgKey, type=SM_TYPE.Information)

    def _request(self, callback):
        BigWorld.player().inventory.createDetachment(self.vehInvID, self.assignToVehicle, self.detCompDescr, lambda code: self._response(code, callback))

    def _getSysMsgBase(self):
        prefix = 'detachment_create'
        if self.assignToVehicle:
            prefix += '/assign_to_vehicle'
        if self.vehicleHasDetachment:
            prefix += '/has_detachment'
        return prefix


class _ConvertIntoDetachment(Processor):

    def __init__(self):
        super(_ConvertIntoDetachment, self).__init__()
        self.addPlugin(plugins.DormitoriesSlotsValidator())

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='detachment_create/{}'.format(errStr), defaultSysMsgKey='detachment_create/server_error', auxData=ctx)


class ConvertVehicleCrewIntoDetachment(_ConvertIntoDetachment):

    def __init__(self, vehInvID, skinID, detCompDescr):
        super(ConvertVehicleCrewIntoDetachment, self).__init__()
        self._vehInvID = vehInvID
        self._skinID = skinID
        self._detCompDescr = detCompDescr

    def _request(self, callback):
        BigWorld.player().inventory.convertVehicleCrewIntoDetachment(self._vehInvID, self._skinID, self._detCompDescr, lambda code, errStr, ext: self._response(code, callback, errStr=errStr, ctx=ext))


class ConvertRecruitsIntoDetachment(_ConvertIntoDetachment):

    def __init__(self, recruitsWithSlots, vehicle, skinID, detCompDescr):
        super(ConvertRecruitsIntoDetachment, self).__init__()
        recruits = [ recruit for _, recruit in sorted(recruitsWithSlots, key=lambda (slotID, _): slotID) ]
        self._recruitsInvIDs = [ (recruit.invID if recruit else RECRUIT_NO_INV_ID) for recruit in recruits ]
        self._vehCompDescr = vehicle.descriptor.makeCompactDescr()
        self._skinID = skinID
        self._detCompDescr = detCompDescr
        self.addPlugin(plugins.VehicleLockValidator(vehicle))
        self.addPlugin(plugins.TankmenLockedValidator(recruits, checkLockCrew=False))

    def _request(self, callback):
        BigWorld.player().inventory.convertRecruitsIntoDetachment(self._recruitsInvIDs, self._skinID, self._vehCompDescr, self._detCompDescr, lambda code, errStr, ext: self._response(code, callback, errStr=errStr, ctx=ext))


class DetachmentAssignToVehicle(Processor):

    def __init__(self, detInvID, vehInvID, detType=TypeDetachmentAssignToVehicle.IS_NONE):
        super(DetachmentAssignToVehicle, self).__init__()
        self.detInvID = detInvID
        self.vehInvID = vehInvID
        self._detType = detType
        vehicle = self.itemsCache.items.getVehicle(vehInvID)
        self.vehicleHasDetachment = vehicle.hasDetachment if vehicle else False
        self.addPlugin(plugins.VehicleLockValidator(vehicle))
        if vehicle:
            self.addPlugin(plugins.VehicleCrewLockedValidator(vehicle))

    def _errorHandler(self, code, errStr='', ctx=None):
        sysMsgKey = self._getSysMsgBase()
        sysMsgKey += '/' + errStr if errStr else '/server_error'
        return makeI18nError(sysMsgKey=sysMsgKey, defaultSysMsgKey='detachment_assign_to_vehicle/server_error')

    def _successHandler(self, code, ctx=None):
        sysMsgKey = self._getSysMsgBase() + '/success'
        return makeI18nSuccess(sysMsgKey=sysMsgKey, type=SM_TYPE.Information)

    def _request(self, callback):
        BigWorld.player().inventory.assignDetachmentToVehicle(self.detInvID, self.vehInvID, lambda code: self._response(code, callback))

    def _getSysMsgBase(self):
        prefix = 'detachment_assign_to_vehicle'
        if self._detType == TypeDetachmentAssignToVehicle.IS_BEST:
            prefix += '/best'
        elif self._detType == TypeDetachmentAssignToVehicle.IS_LAST:
            prefix += '/last'
        elif self.vehicleHasDetachment:
            prefix += '/has_detachment'
        return prefix


class DetachmentUnlockVehicleSlot(Processor):

    def __init__(self, detInvID):
        super(DetachmentUnlockVehicleSlot, self).__init__(plugins=[plugins.DetachmentValidator(detInvID)])
        self.detInvID = detInvID
        unlockedSlots = len(self.detachmentCache.getDetachment(detInvID).getVehicleCDs())
        self.money = getDetachmentVehicleSlotMoney(detInvID, unlockedSlots, default=False)

    def _request(self, callback):
        BigWorld.player().inventory.unlockVehicleSlot(self.detInvID, lambda code: self._response(code, callback))

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(type=FIN_TO_SM_TYPE.get(self.money.getCurrency(), SM_TYPE.Information), sysMsgKey='buy_detachment_vehicle_slot/success', price=formatPrice(self.money, ignoreZeros=True))


class _SpecializeVehicleSlot(Processor):
    __detachmentController = dependency.descriptor(IDetachmentController)

    def __init__(self, detInvID, slotIdx, vehCD, paymentOptionIdx, resetSkills):
        super(_SpecializeVehicleSlot, self).__init__(plugins=[plugins.DetachmentValidator(detInvID)])
        self._detInvID = detInvID
        self._slotIdx = slotIdx
        self._vehCD = vehCD
        self._paymentOptionIdx = paymentOptionIdx
        self._resetSkills = resetSkills
        self._detachment = detachment = self.detachmentCache.getDetachment(self._detInvID)
        self._isSameClass = detachment.getDescriptor().classID == getVehicleIdentification(self._vehCD).classID
        self._isSlotFree = True
        if detachment.getDescriptor().isSlotAvailable(DetachmentSlotType.VEHICLES, slotIdx):
            self._isSlotFree = not detachment.getDescriptor().getSlotValue(DetachmentSlotType.VEHICLES, slotIdx)
        self._hasBuild = bool(detachment.build)
        self._hasUltimatePerks = self._checkUltimatePerks(detachment)
        specOption = getSpecializeOption(detInvID, paymentOptionIdx, default=False)
        self._currency, self._price = getSpecializeOptionMoney(self._detachment, specOption, paymentOptionIdx)
        if self._price > 0:
            self.addPlugin(plugins.MoneyValidator(Money.makeFrom(self._currency, self._price)))
        self._prevVehInvID = detachment.vehInvID
        if self._prevVehInvID:
            vehicle = self.itemsCache.items.getVehicle(detachment.vehInvID)
            self.addPlugin(plugins.VehicleLockValidator(vehicle))
            if vehicle:
                self.addPlugin(plugins.VehicleCrewLockedValidator(vehicle))

    def _checkUltimatePerks(self, detachment):
        if not detachment:
            return False
        detDescr = detachment.getDescriptor()
        perksMatrix = detDescr.getPerksMatrix()
        if not perksMatrix:
            return False
        perksMat = perksMatrix.perks
        for perkID in detachment.build:
            perk = perksMat.get(perkID)
            if not perk:
                continue
            if perk.ultimate:
                return True

        return False

    def _renewSlotsAnimation(self):
        if not self._isSameClass:
            self.__detachmentController.renewSlotsAnimation(self._detInvID, DetachmentSlotType.VEHICLES, xrange(self._detachment.vehicleSlotsCount))


class DetachmentSpecializeVehicleSlot(_SpecializeVehicleSlot):

    def _errorHandler(self, code, errStr='', ctx=None):
        sysMsgKey = self._errorKey()
        sysMsgKey += '/' + errStr if errStr else '/server_error'
        return makeI18nError(sysMsgKey=sysMsgKey, defaultSysMsgKey='specialize_vehicle_slot/server_error')

    def _successHandler(self, code, ctx=None):
        self._renewSlotsAnimation()
        makeMsg, sysMsgKey, smType = self._makeMsg(ctx)
        return makeMsg(sysMsgKey=sysMsgKey, type=smType)

    def _request(self, callback):
        BigWorld.player().inventory.specializeVehicleSlot(self._detInvID, self._slotIdx, self._vehCD, self._paymentOptionIdx, self._resetSkills, lambda code, ext: self._response(code, callback, ctx=ext))

    def _makeMsg(self, ctx=None):
        sysMsgKey = self._getSysMsgBase()
        smType = FIN_TO_SM_TYPE.get(self._currency, SM_TYPE.Information) if self._price > 0 else SM_TYPE.Information
        auxData = None
        detachment = self.detachmentCache.getDetachment(self._detInvID)
        if detachment:
            if self._prevVehInvID > 0 and not detachment.isInTank:
                auxData = makeI18nSuccess(sysMsgKey='detachment_reset_vehicle_link/success', type=SM_TYPE.Information)
            elif detachment.isInTank and (not self._prevVehInvID or self._prevVehInvID != detachment.vehInvID):
                auxData = makeI18nSuccess(sysMsgKey='detachment_assign_to_vehicle/success', type=SM_TYPE.Information)
                if self._prevVehInvID != detachment.vehInvID and ctx and ctx.get('oldCrewRemoved', False):
                    auxData = makeI18nSuccess(sysMsgKey='detachment_assign_to_vehicle/old_crew_removed', type=SM_TYPE.Information, auxData=auxData)
        makeMsg = partial(makeI18nSuccess, auxData=auxData)
        if detachment and self._hasBuild:
            makeMsg = partial(makeMsg, number=text_styles.perkYellow(str(detachment.level)))
        if self._price > 0:
            makeMsg = partial(makeMsg, price=formatPrice(Money.makeFrom(self._currency, self._price), ignoreZeros=True))
        return (makeMsg, sysMsgKey, smType)

    def _errorKey(self):
        sysMsgKey = 'specialize_vehicle_slot'
        if not self._isSameClass:
            sysMsgKey += '/change_class'
        elif not self._isSlotFree:
            sysMsgKey += '/retraining'
        return sysMsgKey

    def _getSysMsgBase(self):
        sysMsgKey = 'specialize_vehicle_slot'
        if not self._isSameClass:
            sysMsgKey += '/change_class'
        elif not self._isSlotFree:
            sysMsgKey += '/retraining'
        if self._resetSkills and self._hasBuild:
            sysMsgKey += '/drop_skills_with_ultimate' if self._hasUltimatePerks else '/drop_skills'
        sysMsgKey += '/financial_success' if self._price > 0 else '/success'
        return sysMsgKey


class DetachmentSpecializeVehicleSlotAndAssign(DetachmentSpecializeVehicleSlot):

    def __init__(self, detInvID, slotIdx, vehCD, paymentOptionIdx, resetSkills, vehInvID):
        super(DetachmentSpecializeVehicleSlotAndAssign, self).__init__(detInvID, slotIdx, vehCD, paymentOptionIdx, resetSkills)
        self._vehInvID = vehInvID

    def _request(self, callback):
        BigWorld.player().inventory.specializeVehicleSlotAndAssign(self._detInvID, self._slotIdx, self._vehCD, self._paymentOptionIdx, self._resetSkills, self._vehInvID, lambda code, ext: self._response(code, callback, ctx=ext))


class DetachmentUnlockSpecializeVehicleSlotAndAssign(DetachmentSpecializeVehicleSlot):

    def __init__(self, detInvID, slotIdx, vehCD, paymentOptionIdx, resetSkills, vehInvID):
        super(DetachmentUnlockSpecializeVehicleSlotAndAssign, self).__init__(detInvID, slotIdx, vehCD, paymentOptionIdx, resetSkills)
        self._vehInvID = vehInvID
        unlockedSlots = len(self.detachmentCache.getDetachment(detInvID).getVehicleCDs())
        self._money = getDetachmentVehicleSlotMoney(detInvID, unlockedSlots, default=False)

    def _successHandler(self, code, ctx=None):
        self._renewSlotsAnimation()
        makeMsg, sysMsgKey, smType = self._makeMsg(ctx)
        auxData = makeMsg(sysMsgKey=sysMsgKey, type=smType)
        return makeI18nSuccess(type=FIN_TO_SM_TYPE.get(self._money.getCurrency(), SM_TYPE.Information), sysMsgKey='buy_detachment_vehicle_slot/success', price=formatPrice(self._money, ignoreZeros=True), auxData=auxData)

    def _request(self, callback):
        BigWorld.player().inventory.unlockSpecializeVehicleSlotAndAssign(self._detInvID, self._slotIdx, self._vehCD, self._paymentOptionIdx, self._resetSkills, self._vehInvID, lambda code, ext: self._response(code, callback, ctx=ext))


class UnpackedInstructor(Processor):

    def __init__(self, instrInvID, nationID, professionID, perksIDs):
        super(UnpackedInstructor, self).__init__()
        self.instrInvID = instrInvID
        self.perksIDs = perksIDs
        self.professionID = professionID
        self.nationID = nationID
        self.addPlugins((plugins.InstructorValidator(instrInvID),
         plugins.UnpackedInstructorValidator(instrInvID),
         plugins.UnpackedInstructorNationIDValidator(instrInvID, nationID),
         plugins.UnpackedInstructorProfessionValidator(instrInvID, professionID),
         plugins.InstructorAlreadyHasPerksValidator(instrInvID)))

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='unpacked_instructor/{}'.format(errStr), defaultSysMsgKey='unpacked_instructor/server_error', auxData=ctx)

    def _successHandler(self, code, ctx=None):
        instructor = self.detachmentCache.getInstructor(self.instrInvID)
        name = instructor.getFullName() if instructor else ''
        return makeI18nSuccess(sysMsgKey='unpacked_instructor/success', type=SM_TYPE.Information, name=name, auxData=ctx)

    def _request(self, callback):
        BigWorld.player().inventory.unpackedInstructor(self.instrInvID, self.nationID, self.professionID, self.perksIDs, lambda code: self._response(code, callback))


class DetachmentResetVehicleLink(Processor):

    def __init__(self, detInvID):
        super(DetachmentResetVehicleLink, self).__init__(plugins=[plugins.DetachmentValidator(detInvID)])
        self.detInvID = detInvID
        self._prefix = 'detachment_reset_vehicle_link'
        detachment = self.detachmentCache.getDetachment(detInvID)
        if detachment and detachment.isInTank:
            vehicle = self.itemsCache.items.getVehicle(detachment.vehInvID)
            self.addPlugin(plugins.VehicleLockValidator(vehicle, isEnabled=bool(vehicle)))
            self.addPlugin(plugins.VehicleCrewLockedValidator(vehicle, isEnabled=bool(vehicle)))

    def _errorHandler(self, code, errStr='', ctx=None):
        self._prefix += '/' + errStr if errStr else '/server_error'
        return makeI18nError(sysMsgKey=self._prefix, defaultSysMsgKey='detachment_reset_vehicle_link/server_error')

    def _successHandler(self, code, ctx=None):
        self._prefix += '/success'
        return makeI18nSuccess(sysMsgKey=self._prefix, type=SM_TYPE.Information)

    def _request(self, callback):
        BigWorld.player().inventory.detachmentResetVehicleLink(self.detInvID, lambda code: self._response(code, callback))


class DetachmentChangePassport(Processor):

    def __init__(self, detInvID, gender, firstNameID, lastNameID, iconID):
        super(DetachmentChangePassport, self).__init__()
        self.__detInvID = detInvID
        self.__nameID = firstNameID
        self.__gender = gender.value
        self.__secondNameID = lastNameID
        self.__iconID = iconID

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='change_passport/{}'.format(errStr), defaultSysMsgKey='change_passport/server_error')

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(sysMsgKey='change_passport/success')

    def _request(self, callback):
        _logger.debug('Make server request to change detachment passport')
        BigWorld.player().inventory.changeDetachmentPassport(self.__detInvID, self.__gender, self.__nameID, self.__secondNameID, self.__iconID, lambda code: self._response(code, callback))


class CrewSkinUnequip(Processor):

    def __init__(self, detInvID):
        super(CrewSkinUnequip, self).__init__()
        self._detInvID = detInvID

    def _request(self, callback):
        _logger.debug('Make server request to equip crewSkin: %d', self._detInvID)
        BigWorld.player().inventory.unequipCrewSkin(self._detInvID, lambda code: self._response(code, callback))


class CrewSkinEquip(Processor):

    def __init__(self, detachment, skinID):
        super(CrewSkinEquip, self).__init__(plugins=[plugins.CrewSkinValidator(skinID, detachment)])
        self._detInvID = detachment.invID
        self.__skinID = skinID
        if detachment.isInTank:
            vehicle = self.itemsCache.items.getVehicle(detachment.vehInvID)
            self.addPlugin(plugins.VehicleLockValidator(vehicle, isEnabled=bool(vehicle)))
            self.addPlugin(plugins.VehicleCrewLockedValidator(vehicle, isEnabled=bool(vehicle)))

    def _request(self, callback):
        _logger.debug('Make server request to equip crewSkin : %d, %d', self._detInvID, self.__skinID)
        BigWorld.player().inventory.equipCrewSkin(self._detInvID, self.__skinID, lambda code: self._response(code, callback))

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(sysMsgKey='crewskin_equip/success', type=SM_TYPE.Information)


class DetachmentSwapVehicleSlots(Processor):

    def __init__(self, detachmentInvID, slot1Index, slot2Index):
        super(DetachmentSwapVehicleSlots, self).__init__([plugins.DetachmentSwapSlotsValidator(detachmentInvID, DetachmentSlotType.VEHICLES, slot1Index, slot2Index)])
        self._detInvID = detachmentInvID
        self._slot1 = slot1Index
        self._slot2 = slot2Index

    def _request(self, callback):
        BigWorld.player().inventory.detachmentSwapVehicleSlots(self._detInvID, self._slot1, self._slot2, lambda code: self._response(code, callback))

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='detachment_swap_slots/{}'.format(errStr), defaultSysMsgKey='detachment_swap_slots/server_error')


class DetachmentDemobilize(ItemProcessor):

    def __init__(self, detachment, allowRemove, freeExcludeInstructors):
        super(DetachmentDemobilize, self).__init__(detachment, [plugins.DetachmentDemobilizeValidator(detachment)])
        self.allowRemove = allowRemove
        self.freeExcludeInstructors = freeExcludeInstructors
        if detachment.isInTank:
            vehicle = self.itemsCache.items.getVehicle(detachment.vehInvID)
            self.addPlugin(plugins.VehicleLockValidator(vehicle, isEnabled=bool(vehicle)))
            self.addPlugin(plugins.VehicleCrewLockedValidator(vehicle, isEnabled=bool(vehicle)))

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='demobilize_detachment/{}'.format(errStr), defaultSysMsgKey='demobilize_detachment/server_error')

    def _successHandler(self, code, ctx=None):
        instructorCount = len([ invID for invID, locked in self.item.getDescriptor().iterSlots(DetachmentSlotType.INSTRUCTORS, getLockFlag=True, skipNone=True, skipDuplicated=True) if not locked ])
        if instructorCount and not self.freeExcludeInstructors:
            recoverInstructorCost = self.itemsCache.items.shop.recoverInstructorCost * instructorCount
            return makeI18nSuccess(sysMsgKey='demobilize_detachment/success_instructor_paid', money=formatPrice(recoverInstructorCost), count=instructorCount, type=FIN_TO_SM_TYPE.get(recoverInstructorCost.getCurrency(), SM_TYPE.Information), auxData=ctx)
        return makeI18nSuccess(sysMsgKey='demobilize_detachment/success_instructor_free', count=instructorCount, type=SM_TYPE.Information, auxData=ctx) if instructorCount else makeI18nSuccess(sysMsgKey='demobilize_detachment/success', type=SM_TYPE.Information, auxData=ctx)

    def _request(self, callback):
        _logger.debug('Make server request to demobilize detachment: %s', self.item)
        BigWorld.player().inventory.demobilizeDetachment(self.item.invID, self.allowRemove, self.freeExcludeInstructors, lambda code: self._response(code, callback))


class DetachmentRestore(ItemProcessor):

    def __init__(self, detachment, curPrice, curCurrency, specialTerm):
        super(DetachmentRestore, self).__init__(detachment, [plugins.DetachmentRestoreValidator(detachment), plugins.DormitoriesSlotsValidator(), plugins.MoneyValidator(curPrice)])
        self._curPrice = curPrice
        self._curCurrency = curCurrency
        self._specialTerm = specialTerm

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='restore_detachment/{}'.format(errStr), defaultSysMsgKey='restore_detachment/server_error')

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(sysMsgKey='restore_detachment/financial_success', money=formatPrice(self._curPrice), type=FIN_TO_SM_TYPE.get(self._curCurrency, SM_TYPE.Information), auxData=ctx) if any(self._curPrice.toDict().itervalues()) else makeI18nSuccess(sysMsgKey='restore_detachment/success', type=SM_TYPE.Information, auxData=ctx)

    def _request(self, callback):
        _logger.debug('Make server request to restore detachment: %s', self.item)
        BigWorld.player().inventory.restoreDetachment(self.item.invID, self._specialTerm, lambda code: self._response(code, callback))


class DetachmentFreeToOwnXpConvertor(Processor):

    def __init__(self, detInvID, freeXpForConvert):
        super(DetachmentFreeToOwnXpConvertor, self).__init__()
        self.__detInvID = detInvID
        self.__freeXpForConvert = freeXpForConvert

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='free_xp_to_detachment_skill/{}'.format(errStr), defaultSysMsgKey='free_xp_to_detachment_skill/server_error')

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(sysMsgKey='free_xp_to_detachment_skill/success', freeXP=backport.getIntegralFormat(self.__freeXpForConvert), type=SM_TYPE.Information)

    def _request(self, callback):
        BigWorld.player().inventory.freeXPToDetachment(self.__detInvID, self.__freeXpForConvert, lambda errStr, code: self._response(code, callback, errStr=errStr))


class SetActiveInstructorInDetachment(Processor):

    def __init__(self, detachmentInvId, instructorSlotId):
        super(SetActiveInstructorInDetachment, self).__init__()
        self._detInvID = detachmentInvId
        self._instSlotId = instructorSlotId

    def _request(self, callback):
        BigWorld.player().inventory.setActiveInstructorInDetachment(self._detInvID, self._instSlotId, lambda code: self._response(code, callback))
