# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/city/ny_object_view.py
from helpers import dependency
from new_year.skeletons.new_year import INewYearController
from gui.impl.gui_decorators import args2params
from new_year.gui.impl.gen.view_models.common.customization_zone_type_model import CustomizationZone
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.city.object_view_model import ObjectViewModel
from new_year.gui.impl.gen.view_models.common.ny_currency_type_model import NyCurrencyType
from new_year.gui.impl.lobby.new_year.sub_model_presenter import SubModelPresenter
from new_year.gui.impl.new_year.navigation import NewYearNavigation
from new_year.gui.impl.new_year.sounds import NewYearSoundsManager
from new_year.gui.shared.ny_level_helper import NewYearAtmospherePresenter
from new_year.gui.shared.ny_currency_provider import NyCurrencyProvider
from new_year.ny_constants import OBJECT_TO_VIEW_SATE, InternalViewState
from new_year_common.items.components.ny_constants import CustomizationObjects, NewYearObjects
from new_year_common.items.components.ny_constants import OBJECT_MAX_LEVEL
from cgf_components.view_camera_sync import CameraState
OBJECTS_ORDER = (CustomizationObjects.FAIR,
 CustomizationObjects.INSTALLATIONS,
 CustomizationObjects.SKATING,
 CustomizationObjects.FIR,
 CustomizationObjects.LIGHTS,
 CustomizationObjects.ATTRACTIONS)

class NyObjectView(SubModelPresenter):
    __slots__ = ('__currentObject', '__currencyProvider', '__currencyForLevelUpdate')
    __nyController = dependency.descriptor(INewYearController)

    def __init__(self, *args, **kwargs):
        super(NyObjectView, self).__init__(*args, **kwargs)
        self.__currentObject = None
        self.__currencyProvider = NyCurrencyProvider()
        self.__currencyForLevelUpdate = NyCurrencyType.MANDARIN
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def initialize(self, *args, **kwargs):
        super(NyObjectView, self).initialize(*args, **kwargs)
        self.__currencyProvider.initialize()
        self.__fillModel()

    def finalize(self):
        self.__currencyProvider.finalize()
        super(NyObjectView, self).finalize()

    def setCameraState(self, cameraState):
        if cameraState == CameraState.INSTALLED:
            NewYearSoundsManager.setGladeState(self.__currentObject)

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
        NewYearSoundsManager.playGladeEvent(self.__currentObject, '_ENTER')

    def __getPrevNextObject(self, currentObject):
        idx = OBJECTS_ORDER.index(currentObject)
        return (self.__getObject(idx - 1), self.__getObject(idx + 1))

    def __getObject(self, idx):
        return OBJECTS_ORDER[idx % len(OBJECTS_ORDER)]

    def _getEvents(self):
        return ((self.viewModel.onGoToCustomizationObject, self.__onGoToCustomizationObject),
         (self.viewModel.onClose, self.__onClose),
         (self.__nyController.onCustomizationObjectUpdated, self.__onCustomizationObjectUpdated),
         (self.__currencyProvider.onCurrencyUpdated, self.__onCurrencyUpdated))

    @args2params(str)
    def __onGoToCustomizationObject(self, objectName):
        NewYearNavigation.switchTo(objectName)

    def update(self):
        self.__fillModel()

    def __onClose(self):
        NewYearNavigation.switchTo(NewYearObjects.CITY_VIEW)

    def __onCustomizationObjectUpdated(self, *args):
        if self.__currentObject in args:
            self.__onLevelUpdate()

    def __onCurrencyUpdated(self, currency, diff):
        if currency == self.__currencyForLevelUpdate:
            self.__onLevelUpdate()

    def __onLevelUpdate(self):
        level = NewYearAtmospherePresenter.getLevelItem(self.__currentObject)
        updateLevelPrice = NewYearAtmospherePresenter.getLevelPrice(self.__currentObject, level + 1)
        currencyCount = self.__currencyProvider.getCurrencyCount(self.__currencyForLevelUpdate)
        with self.viewModel.transaction() as model:
            model.customizationZoneObject.setCurrentLevel(level)
            model.customizationZoneObject.setCurrencyCount(currencyCount)
            model.customizationZoneObject.setLevelUpCurrencyNeed(updateLevelPrice)
            model.customizationZoneObject.currencyType.setValue(self.__currencyForLevelUpdate)
