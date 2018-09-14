# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/customization/slots.py
import copy
from gui.customization.shared import getAdjustedSlotIndex, elementsDiffer, CUSTOMIZATION_TYPE, INSTALLATION

class Slots(object):

    def __init__(self, events):
        self.__events = events
        self.__currentType = CUSTOMIZATION_TYPE.CAMOUFLAGE
        self.__currentIdx = 0
        self.__currentSlotsData = None
        self.__installedSlotsData = None
        self.__installedElements = None
        self.__newVehicleSelected = False
        return

    def init(self):
        self.__events.onDisplayedElementsAndGroupsUpdated += self.__updateSlotsData
        self.__events.onInstalledElementsUpdated += self.__saveInstalledElements
        self.__events.onCarouselElementPicked += self.__applyElement

    def fini(self):
        self.__events.onCarouselElementPicked -= self.__applyElement
        self.__events.onInstalledElementsUpdated -= self.__saveInstalledElements
        self.__events.onDisplayedElementsAndGroupsUpdated -= self.__updateSlotsData
        self.__installedSlotsData = None
        self.__installedElements = None
        self.__currentSlotsData = None
        return

    @property
    def currentSlotIdx(self):
        return self.__currentIdx

    @property
    def currentType(self):
        return self.__currentType

    @property
    def currentSlotsData(self):
        return self.__currentSlotsData

    def getCurrentSlotData(self, slotIdx=None, cType=None):
        slotIdx = self.__currentIdx if slotIdx is None else slotIdx
        cType = self.__currentType if cType is None else cType
        return self.__currentSlotsData[cType][slotIdx]

    def getInstalledSlotData(self, slotIdx=None, cType=None):
        slotIdx = self.__currentIdx if slotIdx is None else slotIdx
        cType = self.__currentType if cType is None else cType
        return self.__installedSlotsData[cType][slotIdx]

    def getSummary(self):
        """ Get amount of slots on the current vehicle (occupied and total)
        
        :return: tuple (occupied, total)
        """
        totalSlotsNum = 0
        occupiedSlotsNum = 0
        for slotGroupData in self.__currentSlotsData:
            totalSlotsNum += len(slotGroupData)
            for slotData in slotGroupData:
                if slotData['element'] is not None:
                    occupiedSlotsNum += 1

        return (occupiedSlotsNum, totalSlotsNum)

    def select(self, cType, slotIdx):
        self.__currentType = cType
        self.__currentIdx = slotIdx
        slotData = self.__currentSlotsData[cType][slotIdx]
        self.__events.onSlotSelected(cType, slotIdx, slotData)

    def clearSlot(self, cType, slotIdx):
        installedSlotData = self.__installedSlotsData[cType][slotIdx]
        if installedSlotData['element'] is not None:
            self.__events.onTankSlotCleared(cType, installedSlotData['spot'], getAdjustedSlotIndex(slotIdx, cType, self.__currentSlotsData), installedSlotData['element'].getID(), 0, installationFlag=INSTALLATION.REMOVAL)
        else:
            self.dropAppliedItem(cType, slotIdx)
        return

    def dropAppliedItem(self, cType, slotIdx):
        installedSlotData = self.__installedSlotsData[cType][slotIdx]
        self.__setSlotAndUpdateView(cType, slotIdx, installedSlotData)

    def __saveInstalledElements(self, newVehicleIsSelected, installedElements):
        self.__newVehicleSelected = newVehicleIsSelected
        self.__installedElements = installedElements

    def __applyElement(self, element, duration, isInQuest):
        """
            :param element: one of elements from DataAggregator
            :param duration: duration which user selected for purchase
            :param isInQuest: element was picked from quest and cannot be bought
            :return: None
        """
        cType = self.__currentType
        slotIdx = self.__currentIdx
        installedSlot = self.__installedSlotsData[cType][slotIdx]
        installedElement = installedSlot['element']
        newSlotData = {'element': element,
         'duration': duration,
         'spot': self.__currentSlotsData[cType][slotIdx]['spot'],
         'isRevertible': installedElement is not None,
         'isInDossier': element.isInDossier,
         'isInQuest': isInQuest}
        if installedElement is not None and installedElement.getID() == element.getID():
            self.__setSlotAndUpdateView(cType, slotIdx, copy.deepcopy(installedSlot))
        elif element.isInDossier:
            numberOfDays = element.numberOfDays
            if numberOfDays is not None:
                itemDuration = numberOfDays if numberOfDays == 30 else 7
                installationFlag = INSTALLATION.INVOICED
            else:
                itemDuration = 0
                installationFlag = INSTALLATION.NORMAL
            self.__events.onOwnedElementPicked(cType, newSlotData['spot'], getAdjustedSlotIndex(slotIdx, cType, self.__currentSlotsData), element.getID(), itemDuration, installationFlag=installationFlag)
        else:
            self.__setSlotAndUpdateView(cType, slotIdx, newSlotData)
        return

    def __setSlotAndUpdateView(self, cType, slotIdx, appliedSlotData):
        appliedSlotData = copy.deepcopy(appliedSlotData)
        self.__currentSlotsData[cType][slotIdx] = appliedSlotData
        self.__events.onSlotsSet(copy.deepcopy(self.__currentSlotsData))
        self.__events.onSlotUpdated(appliedSlotData, cType, slotIdx)

    def __updateSlotsData(self, displayedElements, displayedGroups):
        """
        Method sets initialSlotsData and currentSlotsData. It's called when
        tank has been updated because of some server changes. It's also called
        initially to set slots data as slots are at the time of opening
        customization view.
        
        :return: None
        """
        newSlotsData = []
        for cType in CUSTOMIZATION_TYPE.ALL:
            selectorSlotsData = []
            for slotIdx in range(0, len(self.__installedElements[cType])):
                installedElement = self.__installedElements[cType][slotIdx]
                displayedElement = None
                elementID = installedElement.elementID
                if elementID is not None and elementID in displayedElements[cType]:
                    displayedElement = displayedElements[cType][elementID]
                slotData = {'element': displayedElement,
                 'spot': installedElement.spot,
                 'duration': installedElement.duration,
                 'daysLeft': installedElement.numberOfDaysLeft,
                 'isRevertible': False,
                 'isInDossier': elementID >= 0,
                 'isInQuest': False}
                selectorSlotsData.append(slotData)

            newSlotsData.append(selectorSlotsData)

        if self.__installedSlotsData is not None and not self.__newVehicleSelected:
            self.__handleServerChange(newSlotsData)
        else:
            self.__currentSlotsData = newSlotsData
            self.__installedSlotsData = copy.deepcopy(self.__currentSlotsData)
            if self.__newVehicleSelected:
                self.__resetSlots()
        self.__events.onInitialSlotsSet(self.__installedSlotsData)
        self.__events.onSlotsSet(self.__currentSlotsData)
        return

    def __handleServerChange(self, newSlotsData):
        oldInstalledSlotsData = self.__installedSlotsData
        self.__installedSlotsData = newSlotsData
        for cType in CUSTOMIZATION_TYPE.ALL:
            for slotIdx in range(0, len(newSlotsData[cType])):
                newSlotData = newSlotsData[cType][slotIdx]
                currentSlotData = self.__currentSlotsData[cType][slotIdx]
                oldInstalledSlotData = oldInstalledSlotsData[cType][slotIdx]
                if elementsDiffer(newSlotData['element'], oldInstalledSlotData['element']):
                    self.__currentSlotsData[cType][slotIdx] = newSlotData
                    self.__events.onSlotUpdated(newSlotData, cType, slotIdx)
                if elementsDiffer(oldInstalledSlotData['element'], currentSlotData['element']):
                    self.__events.onSlotUpdated(currentSlotData, cType, slotIdx)

    def __resetSlots(self):
        for cType in CUSTOMIZATION_TYPE.ALL:
            for slotIdx in range(0, len(self.__currentSlotsData[cType])):
                self.__events.onSlotUpdated(self.__currentSlotsData[cType][slotIdx], cType, slotIdx)
