# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/customization/tank_model.py
import copy
import time
from gui.shared.utils.HangarSpace import g_hangarSpace
from gui.customization.shared import getAdjustedSlotIndex, CUSTOMIZATION_TYPE, SLOT_TYPE

class TankModel(object):

    def __init__(self, events):
        self._currentModelAttributes = None
        self.__events = events
        self.__hangarCameraLocation = None
        self.__slotsData = None
        self.__selectedSlotIdx = 0
        self.__initialModelAttributes = None
        self.__hangarSpace = self._getHangarSpace()
        return

    def init(self):
        self.__hangarCameraLocation = self.__hangarSpace.space.getCameraLocation()
        self.__hangarSpace.space.locateCameraToPreview()
        self.__events.onCustomizationViewClosed += self.applyInitialModelAttributes
        self.__events.onBackToSelectorGroup += self.__onBackToSelectorGroup
        self.__events.onSlotUpdated += self.__update
        self.__events.onSlotsSet += self.__onSlotsSet
        self.__events.onSlotSelected += self.__onSlotSelected
        self.__events.onTankModelAttributesUpdated += self.__saveModelAttributes
        self.__hangarSpace.onSpaceCreate += self.__saveHangarCameraLocation

    def fini(self):
        self.__events.onTankModelAttributesUpdated -= self.__saveModelAttributes
        self.__events.onSlotSelected -= self.__onSlotSelected
        self.__events.onSlotsSet -= self.__onSlotsSet
        self.__events.onSlotUpdated -= self.__update
        self.__events.onCustomizationViewClosed -= self.applyInitialModelAttributes
        self.__events.onBackToSelectorGroup -= self.__onBackToSelectorGroup
        self.__hangarSpace.onSpaceCreate -= self.__saveHangarCameraLocation

    def applyInitialModelAttributes(self):
        camouflageIDToSet, newViewData = self.__initialModelAttributes[0], self.__initialModelAttributes[1:3]
        hangarSpace = self.__hangarSpace.space
        if hangarSpace is not None:
            hangarSpace.updateVehicleCamouflage(camouflageIDToSet)
            hangarSpace.updateVehicleSticker(newViewData)
            if self.__hangarCameraLocation is not None:
                hangarSpace.setCameraLocation(**self.__hangarCameraLocation)
            hangarSpace.clearSelectedEmblemInfo()
        return

    def __onBackToSelectorGroup(self):
        hangarSpace = self.__hangarSpace.space
        if hangarSpace is not None:
            hangarSpace.clearSelectedEmblemInfo()
            hangarSpace.locateCameraToPreview()
        return

    @staticmethod
    def _getHangarSpace():
        return g_hangarSpace

    def __saveModelAttributes(self, attributes):
        self.__initialModelAttributes = attributes
        self._currentModelAttributes = copy.deepcopy(attributes)

    def __onSlotsSet(self, slotsData):
        self.__slotsData = slotsData

    def __onSlotSelected(self, cType, slotIdx, slotData):
        self.__selectedSlotIdx = slotIdx
        if cType == CUSTOMIZATION_TYPE.CAMOUFLAGE and slotData['element']:
            self._currentModelAttributes[0] = slotData['element'].getID()
        self.__applyViewModel()
        if cType != CUSTOMIZATION_TYPE.CAMOUFLAGE:
            self.__hangarSpace.space.locateCameraOnEmblem(slotData['spot'] == 0, SLOT_TYPE[cType], getAdjustedSlotIndex(slotIdx, cType, self.__slotsData), 0.2)
        else:
            self.__hangarSpace.space.locateCameraToPreview()

    def __saveHangarCameraLocation(self):
        if self.__hangarSpace.space is not None:
            self.__hangarCameraLocation = self.__hangarSpace.space.getCameraLocation()
        return

    def __update(self, updatedSlotData, cType, slotIdx):
        element = updatedSlotData['element']
        if cType == CUSTOMIZATION_TYPE.CAMOUFLAGE:
            if slotIdx == self.__selectedSlotIdx:
                if element is None:
                    self._currentModelAttributes[0] = None
                else:
                    self._currentModelAttributes[0] = element.getID()
        else:
            if element is None:
                elementID = None
            else:
                elementID = element.getID()
            viewModelItem = [elementID, time.time(), 0]
            if cType == CUSTOMIZATION_TYPE.INSCRIPTION:
                viewModelItem.append(0)
            self._currentModelAttributes[cType][updatedSlotData['spot'] + getAdjustedSlotIndex(slotIdx, cType, self.__slotsData)] = viewModelItem
        self.__applyViewModel()
        return

    def __applyViewModel(self):
        self.__hangarSpace.space.updateVehicleCamouflage(camouflageID=self._currentModelAttributes[0])
        self.__hangarSpace.space.updateVehicleSticker(self._currentModelAttributes[1:3])
        self.__events.onBonusesUpdated()
