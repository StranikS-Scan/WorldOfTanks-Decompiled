# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/city/ny_object_view.py
from helpers import dependency
from new_year.skeletons.new_year import INewYearController, INewYearCurrencyController
from gui.impl.gui_decorators import args2params
from new_year.gui.impl.gen.view_models.common.customization_zone_type_model import CustomizationZone
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.city.object_view_model import ObjectViewModel
from new_year.gui.impl.gen.view_models.common.ny_currency_type_model import NyCurrencyType
from new_year.gui.impl.lobby.new_year.sub_model_presenter import SubModelPresenter
from new_year.gui.impl.new_year.navigation import NewYearNavigation
from new_year.gui.impl.new_year.sounds import NewYearSoundsManager, TreeCameraSounds
from new_year.gui.shared.ny_level_helper import NewYearAtmospherePresenter
from new_year.ny_constants import OBJECT_TO_VIEW_SATE, InternalViewState
from new_year_common.items.components.ny_constants import CustomizationObjects, NewYearObjects
from new_year_common.items.components.ny_constants import OBJECT_MAX_LEVEL
from cgf_components.view_camera_sync import CameraState
OBJECTS_ORDER = (CustomizationObjects.INSTALLATIONS,
 CustomizationObjects.FIR,
 CustomizationObjects.TEREM,
 CustomizationObjects.SNOW_SLIDE,
 CustomizationObjects.FAIR,
 CustomizationObjects.FIREWORKS)
TREE_SUBSTATES = (InternalViewState.TREE_TOP, InternalViewState.TREE_DOWN)

class NyObjectView(SubModelPresenter):
    __slots__ = ('__currentObject', '__currencyForLevelUpdate', '__cameraSubState')
    __nyController = dependency.descriptor(INewYearController)
    __nyCurrencyController = dependency.descriptor(INewYearCurrencyController)

    def __init__(self, *args, **kwargs):
        super(NyObjectView, self).__init__(*args, **kwargs)
        self.__currentObject = None
        self.__currencyForLevelUpdate = NyCurrencyType.MANDARIN
        self.__cameraSubState = None
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def initialize(self, *args, **kwargs):
        super(NyObjectView, self).initialize(*args, **kwargs)
        self.__fillModel()

    def finalize(self):
        self.viewModel.customizationZoneObject.customizationZone.setValue(CustomizationZone.UNDEFINED)
        super(NyObjectView, self).finalize()

    def switchFinalize(self):
        self.finalize()

    def setCameraState(self, cameraState):
        if cameraState == CameraState.INSTALLED:
            self.__cameraSubState = None
            if self.__currentObject == CustomizationObjects.FIR:
                NewYearSoundsManager.setTreeCameraState(self.__currentObject)
            NewYearSoundsManager.setGladeState(self.__currentObject)
        return

    def setCameraSubState(self, subState, cameraState):
        if cameraState == CameraState.IN_TRANSITION:
            self.__cameraSubState = subState
            NewYearSoundsManager.playEvent(TreeCameraSounds.CAMERA_FLY)
        elif cameraState == CameraState.INSTALLED:
            NewYearSoundsManager.setTreeCameraState(subState)

    def __fillModel(self):
        self.__currentObject = NewYearNavigation.getCurrentObject()
        prevObject, nextObject = self.__getPrevNextObject(self.__currentObject)
        self.setInternalViewState(OBJECT_TO_VIEW_SATE.get(self.__currentObject, InternalViewState.DEFAULT))
        with self.viewModel.transaction() as model:
            model.setCurrentObject(self.__currentObject)
            model.setPrevObject(prevObject)
            model.setNextObject(nextObject)
            model.customizationZoneObject.setMaxLevel(OBJECT_MAX_LEVEL)
            model.customizationZoneObject.customizationZone.setValue(CustomizationZone(self.__currentObject))
        self.__onLevelUpdate()

    def __getPrevNextObject(self, currentObject):
        idx = OBJECTS_ORDER.index(currentObject)
        return (self.__getObject(idx - 1), self.__getObject(idx + 1))

    def __getObject(self, idx):
        return OBJECTS_ORDER[idx % len(OBJECTS_ORDER)]

    def _getEvents(self):
        return ((self.viewModel.onGoToCustomizationObject, self.__onGoToCustomizationObject),
         (self.viewModel.onClose, self.__onClose),
         (self.viewModel.onEscape, self.__onEscape),
         (self.__nyController.onCustomizationObjectUpdated, self.__onCustomizationObjectUpdated),
         (self.__nyCurrencyController.onCurrencyUpdated, self.__onCurrencyUpdated))

    @args2params(str)
    def __onGoToCustomizationObject(self, objectName):
        NewYearNavigation.switchTo(objectName)

    def update(self):
        self.__fillModel()

    def __onClose(self):
        self.__goToCityRoot()

    def __onEscape(self):
        hasSubMove = self.__currentObject == CustomizationObjects.FIR and self.__cameraSubState in TREE_SUBSTATES
        if hasSubMove:
            self.__cameraSubState = None
            self.setInternalViewState(InternalViewState.TREE)
            return
        else:
            self.__goToCityRoot()
            return

    @staticmethod
    def __goToCityRoot():
        NewYearSoundsManager.setCityState()
        NewYearNavigation.switchTo(NewYearObjects.CITY_VIEW)

    def __onCustomizationObjectUpdated(self, *args):
        if self.__currentObject in args:
            self.__onLevelUpdate()

    def __onCurrencyUpdated(self, currency, diff):
        if currency == self.__currencyForLevelUpdate:
            self.__onLevelUpdate()

    def __onLevelUpdate(self):
        level = NewYearAtmospherePresenter.getLevelItem(self.__currentObject)
        nextLevel = level + 1
        updateLevelPrice = NewYearAtmospherePresenter.getLevelPrice(self.__currentObject, nextLevel)
        currencyCount = self.__nyCurrencyController.getCurrencyCount(self.__currencyForLevelUpdate)
        toysCount = len(NewYearAtmospherePresenter.getNewYearLevelToys(self.__currentObject, nextLevel))
        atmospherePointsCount = NewYearAtmospherePresenter.getNewYearLevelAtmospherePoints(self.__currentObject, nextLevel)
        with self.viewModel.transaction() as model:
            model.customizationZoneObject.setCurrentLevel(level)
            model.customizationZoneObject.setCurrencyCount(currencyCount)
            model.customizationZoneObject.setLevelUpCurrencyNeed(updateLevelPrice)
            model.customizationZoneObject.currencyType.setValue(self.__currencyForLevelUpdate)
            model.customizationZoneObject.setAtmospherePoints(atmospherePointsCount)
            model.customizationZoneObject.setToysCount(toysCount)
