# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/easy_tank_equip/data_providers/crew_data_provider.py
from typing import TYPE_CHECKING
import nations
from gui.impl.gen.view_models.views.lobby.easy_tank_equip.common.preset_model import PresetDisableReason
from gui.impl.gen.view_models.views.lobby.easy_tank_equip.crew_preset_model import CrewPresetType
from gui.impl.lobby.easy_tank_equip.data_providers.base_data_provider import BaseDataProvider, PresetInfo
from gui.shared.gui_items import checkForTags
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS, sortCrew
from gui.shared.utils.requesters import REQ_CRITERIA, RequestCriteria
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.gui_items import IGuiItemsFactory
if TYPE_CHECKING:
    from typing import List, Optional, Tuple
    from gui.shared.gui_items import Tankman, Vehicle

class CrewPresetInfo(PresetInfo):

    def __init__(self, installed, recruitsCount, presetType, tankmen, tankmenNativeVeh, disableReason=PresetDisableReason.NONE):
        super(CrewPresetInfo, self).__init__(installed, disableReason=disableReason)
        self.recruitsCount = recruitsCount
        self.presetType = presetType
        self.tankmen = tankmen
        self.tankmenNativeVeh = tankmenNativeVeh


class CrewDataProvider(BaseDataProvider):
    EXPERIENCED_PRESET_NUMBER = 0
    NEW_CREW_PRESET_NUMBER = 1
    PRESET_INDEXES = [EXPERIENCED_PRESET_NUMBER, NEW_CREW_PRESET_NUMBER]
    NEW_TANKMAN_INV_ID = -1
    __itemsCache = dependency.descriptor(IItemsCache)
    __itemsFactory = dependency.descriptor(IGuiItemsFactory)

    def __init__(self, vehicle, balance):
        super(CrewDataProvider, self).__init__(vehicle, balance)
        self.__currentVehicleCrew = self.vehicle.crew
        self.__vehDescrType = self.vehicle.descriptor.type
        self.__tankmenInTank = [ tman for _, tman in self.__currentVehicleCrew if tman is not None ]
        self.__countTankmenInTank = len(self.__tankmenInTank)
        self.__tankmenRoles = [ tankmanRoles[0] for tankmanRoles in self.__vehDescrType.crewRoles ]
        self.__countRolesInTank = len(self.__tankmenRoles)
        self.__vehicleCrewIsLocked = checkForTags(self.vehicle.tags, VEHICLE_TAGS.CREW_LOCKED)
        self.__inventoryTankmen = None
        self.__freeBerthsCount = None
        self.__tankmenPresets = []
        self.__countEmptySlotInPreset = []
        self.__tankmenNativeVeh = []
        self.__tankmenPresetsForTTC = []
        self.__tankmenPresetsForApplying = []
        return

    def initialize(self):
        self.__setTankmenPresets()
        crewSetupIsNotFull = self.__countTankmenInTank < self.__countRolesInTank
        isProposalSelected = self.__isEnoughBunksForPreset(self.currentPresetIndex) if not all(self.__tankmenPresets[self.currentPresetIndex]) else crewSetupIsNotFull
        self.isProposalSelected = isProposalSelected or self.__hasNotSuitableTankmen()
        super(CrewDataProvider, self).initialize()

    def finalize(self):
        self.__currentVehicleCrew = None
        self.__vehDescrType = None
        self.__vehicleCrewIsLocked = None
        self.__inventoryTankmen = None
        self.__freeBerthsCount = None
        self.__tankmenInTank = []
        self.__tankmenRoles = []
        self.__tankmenPresets = []
        self.__countEmptySlotInPreset = []
        self.__tankmenNativeVeh = []
        self.__tankmenPresetsForTTC = []
        self.__tankmenPresetsForApplying = []
        super(CrewDataProvider, self).finalize()
        return

    def getPresets(self):
        presetsInfo = []
        for presetIndex in self.PRESET_INDEXES:
            if presetIndex == self.EXPERIENCED_PRESET_NUMBER and self.__isExperiencedPresetNeeded():
                installed = self.__isExperiencedTankmenPresetInstalled()
                presetsInfo.append(self.__getPresetInfo(installed, CrewPresetType.EXPERIENCED, presetIndex))
            if presetIndex == self.NEW_CREW_PRESET_NUMBER and not self.__vehicleCrewIsLocked:
                presetsInfo.append(self.__getPresetInfo(False, CrewPresetType.NEW_CREW, presetIndex))

        return presetsInfo

    def updatePresets(self, fullUpdate=False):
        pass

    def swapSlots(self, firstSlot, secondSlot):
        pass

    def setValuesFromCurrentPreset(self):
        self.vehicle.crew = self.__tankmenPresetsForTTC[self.currentPresetIndex]

    def revertChangesFromSelectedPreset(self):
        self.vehicle.crew = self.__currentVehicleCrew

    def getCurrentPresetItemsIds(self):
        if self.isProposalDisabled() or self.isCurrentPresetDisabled():
            return []
        else:
            return [ (tankman.invID if tankman is not None else self.NEW_TANKMAN_INV_ID) for _, tankman in self.__tankmenPresetsForApplying[self.currentPresetIndex] ]

    def _getPresetDataForApplying(self):
        applyingData = []
        for index, tankman in self.__tankmenPresetsForApplying[self.currentPresetIndex]:
            if tankman is None or tankman not in self.__tankmenInTank:
                applyingData.append((index, tankman))

        return applyingData

    def __isEnoughBunksForPreset(self, presetIndex):
        return True if self.__countEmptySlotInPreset[presetIndex] == 0 else self.__getFreeBerthsCount() >= self.__countEmptySlotInPreset[presetIndex]

    def __getPresetInfo(self, installed, presetType, presetIndex):
        disableReason = PresetDisableReason.NONE if self.__isEnoughBunksForPreset(presetIndex) else PresetDisableReason.NOT_ENOUGH_BUNKS
        return CrewPresetInfo(installed=installed, recruitsCount=self.__countEmptySlotInPreset[presetIndex], presetType=presetType, tankmen=self.__tankmenPresets[presetIndex], tankmenNativeVeh=self.__tankmenNativeVeh[presetIndex], disableReason=disableReason)

    def __setTankmenForApplying(self):
        self.vehicle.crew = self.__tankmenPresetsForApplying[self.currentPresetIndex]

    def __hasNotSuitableTankmen(self):
        return any((not tankman.descriptor.isOwnVehicleOrPremium(self.__vehDescrType) for tankman in self.__tankmenInTank))

    def __isExperiencedPresetNeeded(self):
        return self.__tankmenPresets[self.EXPERIENCED_PRESET_NUMBER] != self.__tankmenPresets[self.NEW_CREW_PRESET_NUMBER]

    def __getSortedTankmenByRoles(self):
        crew = [ (vehicleSlotIdx, tankman) for vehicleSlotIdx, tankman in enumerate(self.__tankmenPresets[self.NEW_CREW_PRESET_NUMBER]) ]
        crew = sortCrew(crew, self.__vehDescrType.crewRoles)
        return crew

    def __getSortedTankmen(self, presetIndex):
        crew = self.__getSortedTankmenByRoles()
        if presetIndex == self.NEW_CREW_PRESET_NUMBER:
            return crew
        return [ (item[0], self.__tankmenPresets[presetIndex][slotIndex]) for slotIndex, item in enumerate(crew) ]

    def __getSortedTankmenForTTC(self, presetIndex):
        crew = self.__getSortedTankmenByRoles()
        if presetIndex == self.NEW_CREW_PRESET_NUMBER:
            return crew
        result = []
        for slotIndex, item in enumerate(crew):
            tankman = self.__tankmenPresets[presetIndex][slotIndex]
            vehicleSlotIdx = item[0]
            if tankman and self.vehicle.invID != tankman.vehicleInvID:
                tmanDescr = tankman.descriptor
                tankman = self.__itemsFactory.createTankman(tmanDescr.makeCompactDescr(), vehicle=self.vehicle, vehicleSlotIdx=vehicleSlotIdx, bonusSkillsLevels=[tmanDescr.bonusSkillsLevels])
            result.append((vehicleSlotIdx, tankman))

        return result

    def __isExperiencedTankmenPresetInstalled(self):
        return self.__countTankmenInTank == self.__countRolesInTank and self.__currentVehicleCrew == self.__tankmenPresetsForApplying[self.EXPERIENCED_PRESET_NUMBER]

    def __getFreeBerthsCount(self):
        if self.__freeBerthsCount is None:
            self.__freeBerthsCount = self.__itemsCache.items.freeTankmenBerthsCount()
        return self.__freeBerthsCount

    def __getInventoryTankmen(self):
        if self.__inventoryTankmen is None:
            self.__inventoryTankmen = self.__itemsCache.items.getInventoryTankmenRO().values()
        return self.__inventoryTankmen

    def __setTankmenPresets(self):
        experiencedTankmen, tankmenNativeVeh, emptySlotCount = self.__getExperiencedTankmen()
        newTankmenPreset = [None] * self.__countRolesInTank
        self.__tankmenPresets = [experiencedTankmen, newTankmenPreset]
        self.__countEmptySlotInPreset = [emptySlotCount, self.__countRolesInTank]
        self.__tankmenNativeVeh = [tankmenNativeVeh, newTankmenPreset]
        for presetIndex in self.PRESET_INDEXES:
            self.__tankmenPresetsForTTC.append(self.__getSortedTankmenForTTC(presetIndex))
            self.__tankmenPresetsForApplying.append(self.__getSortedTankmen(presetIndex))

        return

    def __getInitialFilterCriteria(self):
        criteria = REQ_CRITERIA.TANKMAN.NATION(nations.NAMES[self.vehicle.nationID])
        criteria |= REQ_CRITERIA.CUSTOM(lambda tankman: tankman.descriptor.role in self.__tankmenRoles and tankman not in self.__tankmenInTank and tankman.descriptor.isOwnVehicleOrPremium(self.__vehDescrType))
        criteria |= ~REQ_CRITERIA.CUSTOM(lambda tankman: checkForTags(self.__itemsCache.items.getVehicle(tankman.vehicleInvID).tags, VEHICLE_TAGS.CREW_LOCKED) if tankman.isInTank else False)
        criteria |= ~REQ_CRITERIA.CUSTOM(lambda tankman: tankman.getVehicle().isLocked if tankman.isInTank else False)
        return criteria

    def __getFilterByTankmanRoleCriteria(self, tankmanRole):
        criteria = REQ_CRITERIA.CUSTOM(lambda item: item.descriptor.role == tankmanRole)
        return criteria

    def __getExperiencedTankmen(self):
        experiencedTankmen = []
        tankmenNativeVeh = []
        emptySlotCount = 0
        if self.__vehicleCrewIsLocked:
            experiencedTankmen += self.__tankmenInTank
            tankmenNativeVeh = [self.vehicle] * self.__countTankmenInTank
        else:
            suitableTankmenWithoutRetraining = filter(self.__getInitialFilterCriteria(), self.__getInventoryTankmen())
            for slotIdx, tankman in self.vehicle.crew:
                role = self.__vehDescrType.crewRoles[slotIdx][0]
                sortedTankmenByRating = sorted(filter(self.__getFilterByTankmanRoleCriteria(role), suitableTankmenWithoutRetraining), key=lambda tman: -tman.descriptor.getTotalSkillsProgressPercent(withFree=True))
                tankmanCandidate = self.__getTankmanCandidateForRole(sortedTankmenByRating, experiencedTankmen, tankman)
                if tankmanCandidate is None:
                    emptySlotCount += 1
                    tankmanNativeVeh = None
                else:
                    vehicleNativeDescr = tankmanCandidate.vehicleNativeDescr.type.compactDescr
                    tankmanNativeVeh = self.__itemsCache.items.getItemByCD(vehicleNativeDescr)
                experiencedTankmen.append(tankmanCandidate)
                tankmenNativeVeh.append(tankmanNativeVeh)

        return (experiencedTankmen, tankmenNativeVeh, emptySlotCount)

    def __getTankmanCandidateForRole(self, sortedTankmenByRating, experiencedTankmen, tankmanInVehicle=None):
        for tankmanCandidate in sortedTankmenByRating:
            if tankmanCandidate in experiencedTankmen:
                continue
            if tankmanInVehicle is None or not tankmanInVehicle.descriptor.isOwnVehicleOrPremium(self.__vehDescrType):
                return tankmanCandidate
            tankmanInVehicleSkills = tankmanInVehicle.descriptor.getTotalSkillsProgressPercent(withFree=True)
            tankmanCandidateSkills = tankmanCandidate.descriptor.getTotalSkillsProgressPercent(withFree=True)
            if tankmanInVehicleSkills >= tankmanCandidateSkills:
                return tankmanInVehicle
            return tankmanCandidate

        return tankmanInVehicle
