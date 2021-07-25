# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/tooltips/detachment_info_tooltip.py
import typing
from crew2 import settings_globals
from frameworks.wulf import ViewSettings
from gui.impl.auxiliary.detachment_helper import fillDetachmentTopPanelModel, getRecruitsForMobilization, getVehicleLockState, isDetachmentInRecycleBin, fillRestorePriceModel, getRecoveryTerms
from gui.impl.auxiliary.instructors_helper import fillInstructorBaseModel
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.detachment_info_instructor_model import DetachmentInfoInstructorModel
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.detachment_info_slot_model import DetachmentInfoSlotModel
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.detachment_info_tooltip_model import DetachmentInfoTooltipModel
from gui.impl.pub import ViewImpl
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers.dependency import descriptor
from items.components.component_constants import EMPTY_STRING
from items.components.detachment_constants import NO_DETACHMENT_ID, DetachmentSlotType
from skeletons.gui.detachment import IDetachmentCache
from skeletons.gui.shared import IItemsCache
from uilogging.detachment.loggers import DynamicGroupTooltipLogger
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.detachment import Detachment
    from gui.shared.gui_items.Vehicle import Vehicle
    from gui.shared.gui_items.instructor import Instructor

class DetachmentInfoTooltip(ViewImpl):
    __itemsCache = descriptor(IItemsCache)
    __detachmentCache = descriptor(IDetachmentCache)
    __slots__ = ('_detachment', '_detachmentInvID', '_detachmentSettings', '_vehicleInvID')
    uiLogger = DynamicGroupTooltipLogger()

    def __init__(self, detachmentInvID=None, vehicleInvID=None):
        settings = ViewSettings(R.views.lobby.detachment.tooltips.DetachmentInfoTooltip())
        settings.model = DetachmentInfoTooltipModel()
        super(DetachmentInfoTooltip, self).__init__(settings)
        self._detachmentInvID = detachmentInvID
        self._detachmentSettings = settings_globals.g_detachmentSettings
        self._vehicleInvID = vehicleInvID
        self._detachment = None
        return

    @property
    def viewModel(self):
        return super(DetachmentInfoTooltip, self).getViewModel()

    def _fillDemobilizeModel(self, detachment, mdl):
        recycleBinSize = len(self.__detachmentCache.getDetachments(REQ_CRITERIA.DETACHMENT.DEMOBILIZE))
        fullTerm, freeTerm, paidTerm = getRecoveryTerms(detachment, self._detachmentSettings)
        mdl.setFullTerm(fullTerm)
        mdl.setFreeTerm(freeTerm)
        mdl.setPaidTerm(paidTerm)
        mdl.setDissolvedCount(recycleBinSize)
        mdl.setRecycleMax(self._detachmentSettings.recycleBinMaxSize)

    def _initialize(self, *args, **kwargs):
        super(DetachmentInfoTooltip, self)._initialize()
        self.uiLogger.tooltipOpened()

    def _finalize(self):
        self.uiLogger.tooltipClosed(self.__class__.__name__)
        self.uiLogger.reset()
        super(DetachmentInfoTooltip, self)._finalize()

    def _onLoading(self):
        super(DetachmentInfoTooltip, self)._onLoading()
        with self.viewModel.transaction() as tx:
            if self._detachmentInvID != NO_DETACHMENT_ID and self._detachmentInvID is not None:
                self._detachment = self.__detachmentCache.getDetachment(self._detachmentInvID)
                tx.setIsDetachmentExists(True)
                tx.setIsDismissed(isDetachmentInRecycleBin(self._detachment))
                if self._detachment.isInTank:
                    vehicle = self.__itemsCache.items.getVehicle(self._detachment.vehInvID)
                    tx.setHasLockCrew(vehicle.isCrewLocked)
                    tx.setLockState(getVehicleLockState(vehicle))
                if self._detachment.isInRecycleBin:
                    self._fillDemobilizeModel(self._detachment, tx.demobilizeInfo)
                self.__updateTopPanel(tx)
                self.__updateVehicleSlots(tx)
                self.__updateInstructorSlots(tx)
                fillRestorePriceModel(tx.demobilizeInfo.priceModel, self.__itemsCache.items.stats, self._detachmentInvID)
            else:
                vehicle = self.__itemsCache.items.getVehicle(self._vehicleInvID)
                recruits = []
                if vehicle is not None:
                    recruits = getRecruitsForMobilization(vehicle)
                tx.setIsRecruitersExists(bool(recruits))
        return

    def __updateTopPanel(self, tx):
        fillDetachmentTopPanelModel(model=tx, detachment=self._detachment)

    def __fillVehicleSlot(self, vehicle, vehicleSlot, isCurrent):
        vehicleSlot.setId(vehicle.invID)
        vehicleSlot.setStatus(DetachmentInfoSlotModel.ASSIGNED)
        vehicleSlot.setName(vehicle.shortUserName)
        vehicleIcon = vehicle.name.replace(':', '_').replace('-', '_')
        iconResID = R.images.gui.maps.icons.vehicle.contour.dyn(vehicleIcon)()
        vehicleSlot.setIcon(iconResID)
        vehicleSlot.setIsCurrentVehicle(isCurrent)

    def __updateVehicleSlots(self, tx):
        vehicleSlots = tx.getVehicleSlots()
        vehicleSlots.clear()
        vehicleCDs = self._detachment.getVehicleCDs()
        slotLevels = self._detachment.getVehicleSlotUnlockLevels()
        hasLockCrew = False
        if self._detachment.vehInvID:
            currentVehicle = self.__itemsCache.items.getVehicle(self._detachment.vehInvID)
            hasLockCrew = currentVehicle.isCrewLocked
            if hasLockCrew:
                vehicleSlot = DetachmentInfoSlotModel()
                self.__fillVehicleSlot(currentVehicle, vehicleSlot, True)
                vehicleSlots.addViewModel(vehicleSlot)
        if not hasLockCrew:
            for index in xrange(self._detachment.maxVehicleSlots):
                vehicleSlot = DetachmentInfoSlotModel()
                if index < len(vehicleCDs):
                    vehicleCD = vehicleCDs[index]
                    if vehicleCD:
                        vehicleGuiItem = self.__itemsCache.items.getItemByCD(vehicleCD)
                        self.__fillVehicleSlot(vehicleGuiItem, vehicleSlot, self._detachment.vehInvID == vehicleGuiItem.invID)
                    else:
                        vehicleSlot.setStatus(DetachmentInfoSlotModel.EMPTY)
                else:
                    vehicleSlot.setStatus(DetachmentInfoSlotModel.LOCKED)
                    vehicleSlot.setLevelReq(slotLevels[index])
                vehicleSlots.addViewModel(vehicleSlot)

        vehicleSlots.invalidate()

    def __updateInstructorSlots(self, tx):
        instructorSlots = tx.getInstructorSlots()
        instructorSlots.clear()
        instructorUnlockLevels = self._detachment.getInstructorUnlockLevels()
        instructorsIDs = self._detachment.getInstructorsIDs()
        tx.setOpenInstSlotsCount(len(instructorsIDs))
        processedInstructors = set()
        occupiedSlotsCount = len(instructorsIDs)
        for index in xrange(self._detachment.getMaxInstructorsCount()):
            if index < occupiedSlotsCount:
                instructorInvID = instructorsIDs[index]
                instructorItem = self.__detachmentCache.getInstructor(instructorInvID)
                if instructorItem and instructorInvID in processedInstructors:
                    continue
                elif instructorItem:
                    processedInstructors.add(instructorInvID)
                instructorSlot = DetachmentInfoInstructorModel()
                if instructorItem is not None:
                    instructorSlot.setStatus(DetachmentInfoSlotModel.ASSIGNED)
                    instructorSlot.setName(instructorItem.fullName)
                    fillInstructorBaseModel(instructorSlot, instructorItem, fillPlaceholder=False)
                else:
                    instructorSlot.setStatus(DetachmentInfoSlotModel.EMPTY)
            else:
                instructorSlot = DetachmentInfoInstructorModel()
                instructorSlot.setStatus(DetachmentInfoSlotModel.LOCKED)
                instructorSlot.setLevelReq(instructorUnlockLevels[index])
            instructorSlot.setId(index)
            instructorSlots.addViewModel(instructorSlot)

        tx.setHasInstructors(any(instructorsIDs))
        instructorSlots.invalidate()
        return


class PreviewDetachmentInfoTooltip(ViewImpl):
    __itemsCache = descriptor(IItemsCache)
    __detachmentCache = descriptor(IDetachmentCache)
    __slots__ = ('_detachment', '_instructors', '_vehicle')

    def __init__(self, detachment, instructors, vehicle):
        settings = ViewSettings(R.views.lobby.detachment.tooltips.DetachmentInfoTooltip())
        settings.model = DetachmentInfoTooltipModel()
        super(PreviewDetachmentInfoTooltip, self).__init__(settings)
        self._detachment = detachment
        self._instructors = instructors
        self._vehicle = vehicle

    @property
    def viewModel(self):
        return super(PreviewDetachmentInfoTooltip, self).getViewModel()

    def _onLoading(self):
        super(PreviewDetachmentInfoTooltip, self)._onLoading()
        with self.viewModel.transaction() as tx:
            tx.setIsDetachmentExists(True)
            tx.setIsDismissed(False)
            tx.setHasLockCrew(self._vehicle.isCrewLocked)
            tx.setLockState(EMPTY_STRING)
            self.__updateTopPanel(tx)
            self.__updateVehicleSlots(tx)
            self.__updateInstructorSlots(tx)

    def __updateTopPanel(self, tx):
        fillDetachmentTopPanelModel(model=tx, detachment=self._detachment)

    def __fillVehicleSlot(self, vehicle, vehicleSlot, isCurrent):
        vehicleSlot.setId(vehicle.invID)
        vehicleSlot.setStatus(DetachmentInfoSlotModel.ASSIGNED)
        vehicleSlot.setName(vehicle.shortUserName)
        vehicleIcon = vehicle.name.replace(':', '_').replace('-', '_')
        iconResID = R.images.gui.maps.icons.vehicle.contour.dyn(vehicleIcon)()
        vehicleSlot.setIcon(iconResID)
        vehicleSlot.setIsCurrentVehicle(isCurrent)

    def __updateVehicleSlots(self, tx):
        vehicleSlots = tx.getVehicleSlots()
        vehicleSlots.clear()
        slotLevels = self._detachment.getVehicleSlotUnlockLevels()
        hasLockCrew = self._vehicle.isCrewLocked
        if hasLockCrew:
            vehicleSlot = DetachmentInfoSlotModel()
            self.__fillVehicleSlot(self._vehicle, vehicleSlot, True)
            vehicleSlots.addViewModel(vehicleSlot)
        else:
            for index in xrange(self._detachment.maxVehicleSlots):
                vehicleSlot = DetachmentInfoSlotModel()
                if index == 0 and not (self._vehicle.isPremium or self._vehicle.isPremiumIGR):
                    self.__fillVehicleSlot(self._vehicle, vehicleSlot, False)
                elif self._detachment.getDescriptor().isSlotAvailable(DetachmentSlotType.VEHICLES, index):
                    vehicleSlot.setStatus(DetachmentInfoSlotModel.EMPTY)
                else:
                    vehicleSlot.setStatus(DetachmentInfoSlotModel.LOCKED)
                    vehicleSlot.setLevelReq(slotLevels[index])
                vehicleSlots.addViewModel(vehicleSlot)

            vehicleSlots.invalidate()

    def __updateInstructorSlots(self, tx):
        instructorSlots = tx.getInstructorSlots()
        instructorSlots.clear()
        instructorUnlockLevels = self._detachment.getInstructorUnlockLevels()
        instructorsCount = len(self._instructors)
        tx.setOpenInstSlotsCount(instructorsCount)
        slotIndex = instrIndex = 0
        while slotIndex < self._detachment.getMaxInstructorsCount():
            instructorSlot = DetachmentInfoInstructorModel()
            capacity = 1
            if instrIndex < instructorsCount:
                instructor = self._instructors[instrIndex]
                instrIndex += 1
                capacity = instructor.descriptor.getSlotsCount()
                fillInstructorBaseModel(instructorSlot, instructor)
                instructorSlot.setStatus(DetachmentInfoSlotModel.ASSIGNED)
            elif self._detachment.getDescriptor().isSlotAvailable(DetachmentSlotType.INSTRUCTORS, slotIndex):
                instructorSlot.setStatus(DetachmentInfoSlotModel.EMPTY)
            else:
                instructorSlot.setLevelReq(instructorUnlockLevels[slotIndex])
                instructorSlot.setStatus(DetachmentInfoSlotModel.LOCKED)
            slotIndex += capacity
            instructorSlots.addViewModel(instructorSlot)

        instructorSlots.invalidate()
