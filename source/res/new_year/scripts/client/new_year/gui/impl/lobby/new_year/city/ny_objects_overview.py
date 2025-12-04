# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/city/ny_objects_overview.py
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.city.objects_overview_model import ObjectsOverviewModel
from new_year.gui.impl.lobby.new_year.ny_views_helpers import HoverObject, destroyGUIHoveredObject
from new_year_common.items.components.ny_constants import TOY_TYPES_BY_OBJECT
from new_year.gui.impl.lobby.new_year.sub_model_presenter import SubModelPresenter
from gui.impl.gui_decorators import args2params
from helpers import dependency
from new_year.ny_constants import ANCHOR_TO_OBJECT
from skeletons.gui.shared import IItemsCache
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.customization_zone.customization_zone_model import CustomizationZoneModel
from new_year.skeletons.new_year import INewYearController, INewYearCurrencyController
from new_year_common.items.components.ny_constants import CustomizationObjects
from new_year.helpers.server_settings import getNewYearObjectsConfig
from new_year.helpers.ny_helpers import getCurrentObjectLevel
from new_year.gui.impl.gen.view_models.common.customization_zone_type_model import CustomizationZone
from new_year.gui.shared.ny_level_helper import NewYearAtmospherePresenter
from shared_utils import findFirst
from new_year.ny_constants import SyncDataKeys

class NyObjectsOverview(SubModelPresenter):
    __slots__ = ('__config', '__hoveredObject')
    __nyController = dependency.descriptor(INewYearController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __nyCurrencyController = dependency.descriptor(INewYearCurrencyController)

    def __init__(self, viewModel, *args):
        super(NyObjectsOverview, self).__init__(viewModel, *args)
        self.__config = getNewYearObjectsConfig()
        self.__hoveredObject = HoverObject(None)
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def initialize(self, *args, **kwargs):
        super(NyObjectsOverview, self).initialize(*args, **kwargs)
        self.__fillModel()

    def finalize(self):
        if self.__hoveredObject.isHovered:
            self.viewModel.hoveredObject.setIsZoneHovered(False)
        destroyGUIHoveredObject(self.__hoveredObject)
        super(NyObjectsOverview, self).finalize()

    def update(self):
        self.__fillModel()

    def __fillModel(self):
        with self.viewModel.transaction() as model:
            customizationZones = model.panel.getCustomizationZones()
            customizationZones.clear()
            for customizationZone in CustomizationObjects.PANEL_OBJECTS_ORDER:
                customizationZoneModel = CustomizationZoneModel()
                currentBalance = self.__nyCurrencyController.getMandarinTokenCount
                currentLevel = getCurrentObjectLevel(customizationZone)
                slotsDescr = self.__nyController.getSlotDescrs()
                visitedSlots = []
                for slot in slotsDescr:
                    if slot.type in TOY_TYPES_BY_OBJECT[customizationZone]:
                        visitedSlots.append(self.__nyController.checkForNewToys(slot=slot.id))

                upgradeCost = self.__config.getNextLevelPrice(customizationZone, currentLevel)
                atmospherePoints = NewYearAtmospherePresenter.getNewYearLevelAtmospherePoints(customizationZone, currentLevel + 1)
                customizationZoneModel.setHasNewToys(any(visitedSlots))
                customizationZoneModel.customizationZone.setValue(CustomizationZone(customizationZone))
                customizationZoneModel.setLevelUpCurrencyNeed(upgradeCost)
                customizationZoneModel.setAtmospherePoints(atmospherePoints)
                if currentBalance < upgradeCost:
                    customizationZoneModel.setCanUpgrade(False)
                customizationZones.addViewModel(customizationZoneModel)

            customizationZones.invalidate()

    def _getEvents(self):
        return ((self.viewModel.onObjectHover, self.__onObjectHover),
         (self.viewModel.onObjectHoverOut, self.__onObjectHoverOut),
         (self.__nyController.onCustomizationObjectUpdated, self.__onObjectUpdate),
         (self.__nyController.onSpaceObjectHover, self.__onSpaceObjectHover),
         (self.__nyController.onGUIObjectHover, self.__onGUIObjectHover),
         (self.__nyCurrencyController.onCurrencyUpdated, self.__onObjectUpdate),
         (self.__nyController.onDataUpdated, self.__onDataUpdated))

    def __onDataUpdated(self, keys):
        if SyncDataKeys.INVENTORY_TOYS in keys:
            self.update()

    def __onObjectUpdate(self, *args, **kwargs):
        self.__fillModel()

    @args2params(str)
    def __onObjectHover(self, customizationZoneName):
        self.__nyController.setGuiObjectHover(customizationZoneName, True)

    @args2params(str)
    def __onObjectHoverOut(self, customizationZoneName):
        self.__nyController.setGuiObjectHover(customizationZoneName, False)

    def __onSpaceObjectHover(self, objectName, isHovered):
        objectName = ANCHOR_TO_OBJECT.get(objectName, '')
        if objectName in CustomizationObjects.ALL:
            self.__hoveredObject.setSpaceObjectHover(objectName, isHovered)
            self.viewModel.hoveredObject.setIsZoneHovered(isHovered)
        customizationZones = self.viewModel.panel.getCustomizationZones()
        customizationZone = findFirst(lambda zone: zone.customizationZone.getValue().value == objectName, customizationZones, None)
        if customizationZone is not None:
            customizationZone.setIsZoneHovered(isHovered)
        return

    def __onGUIObjectHover(self, objectName, isHovered):
        if objectName in CustomizationObjects.ALL:
            self.__hoveredObject.setGUIObjectHover(objectName, isHovered)
