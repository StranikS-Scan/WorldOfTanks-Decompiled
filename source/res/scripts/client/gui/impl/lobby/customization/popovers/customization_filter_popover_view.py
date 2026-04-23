# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/customization/popovers/customization_filter_popover_view.py
from frameworks.wulf import ViewSettings, WindowLayer
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.customization.customization_filter_model import CustomizationFilterModel
from gui.impl.lobby.customization.customization_carousel_helpers import CarouselFilterTypes
from gui.impl.lobby.customization.filter_types import AvailabilityFilterState, getStructureList
from gui.impl.pub import PopOverViewImpl, PopOverWindow
from helpers import dependency
from skeletons.gui.customization import ICustomizationService

class CustomizationFilterPopoverView(PopOverViewImpl):
    __slots__ = ('__ctx', '__carouselDP')
    __service = dependency.descriptor(ICustomizationService)

    def __init__(self, layoutID, carouselDP):
        settings = ViewSettings(layoutID)
        settings.model = CustomizationFilterModel()
        super(CustomizationFilterPopoverView, self).__init__(settings)
        self.__ctx = None
        self.__carouselDP = carouselDP
        return

    @property
    def viewModel(self):
        return super(CustomizationFilterPopoverView, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.changeFilter, self.__changeFilter), (self.viewModel.clearFilter, self.__clearFilter), (self.__ctx.events.onCarouselFiltered, self.__onCarouselFiltered))

    def _initialize(self):
        self.__ctx.events.onFilterPopover(True)
        super(CustomizationFilterPopoverView, self)._initialize()

    def _finalize(self):
        self.__ctx.events.onFilterPopover(False)
        super(CustomizationFilterPopoverView, self)._finalize()

    def _onLoading(self, *args, **kwargs):
        self.__ctx = self.__service.getCtx()
        super(CustomizationFilterPopoverView, self)._onLoading(*args, **kwargs)
        self.__fillModel()

    def __fillModel(self):
        filterData = self.__carouselDP.getFilterData()
        filteredItemsCounter, itemsCounter, newHiddenItemsCount = self.__carouselDP.getCountersForCtx()
        structure = getStructureList(self.__ctx, self.__carouselDP)
        displayGroupsData = self.__carouselDP.getDisplayGroupsData()
        groupNum = filterData[CarouselFilterTypes.GROUP] if filterData[CarouselFilterTypes.GROUP] is not None else -1
        with self.viewModel.transaction() as model:
            groups = model.getGroups()
            displayGroups = model.getDisplayGroups()
            structureList = model.getStructure()
            groups.clear()
            displayGroups.clear()
            structureList.clear()
            model.setIsFilteringActive(self.__carouselDP.hasAppliedFilter())
            model.setAvailability(self.__carouselDP.getAvailabilityFilter())
            model.setIsEnableOnAnotherVeh(self.__carouselDP.getAvailabilityFilter() == AvailabilityFilterState.ALL)
            model.setOnAnotherVeh(filterData[CarouselFilterTypes.ON_ANOTHER_VEH])
            model.setApplied(filterData[CarouselFilterTypes.APPLIED])
            model.setFavorite(filterData[CarouselFilterTypes.FAVORITE])
            model.setHistoric(filterData[CarouselFilterTypes.HISTORIC])
            model.setNonHistoric(filterData[CarouselFilterTypes.NON_HISTORIC])
            model.setFantastical(filterData[CarouselFilterTypes.FANTASTICAL])
            model.setOnlyEditableStyles(filterData[CarouselFilterTypes.ONLY_EDITABLE_STYLES])
            model.setOnlyNonEditableStyles(filterData[CarouselFilterTypes.ONLY_NON_EDITABLE_STYLES])
            model.setOnlyProgressionStyles(filterData[CarouselFilterTypes.ONLY_PROGRESSION_STYLES])
            model.setOnlyProgressionDecals(filterData[CarouselFilterTypes.ONLY_PROGRESSION_DECALS])
            model.setAllItemsCounter(itemsCounter)
            model.setFilteredItemsCounter(filteredItemsCounter)
            model.setNewHiddenItemsCounter(newHiddenItemsCount)
            model.setSelectedDisplayGroup(filterData[CarouselFilterTypes.DISPLAY_GROUP])
            model.setSelectedGroup(groupNum)
            model.setFormfactor_square(filterData[CarouselFilterTypes.FORMFACTOR_SQUARE])
            model.setFormfactor_rect1x2(filterData[CarouselFilterTypes.FORMFACTOR_RECT1X2])
            model.setFormfactor_rect1x3(filterData[CarouselFilterTypes.FORMFACTOR_RECT1X3])
            model.setFormfactor_rect1x4(filterData[CarouselFilterTypes.FORMFACTOR_RECT1X4])
            model.setFormfactor_rect1x6(filterData[CarouselFilterTypes.FORMFACTOR_RECT1X6])
            for group in self.__carouselDP.getItemsData().groups.values():
                groups.addString(group)

            for displayGroup in displayGroupsData:
                displayGroups.addString(displayGroup)

            for el in structure:
                structureList.addString(el.value)

            groups.invalidate()
            displayGroups.invalidate()
            structureList.invalidate()
        return

    def __changeFilter(self, args):
        value = args['value']
        if isinstance(value, float):
            value = int(value)
        self.__carouselDP.updateFilterCarousel({args['key']: value})

    def __onCarouselFiltered(self):
        self.__fillModel()

    def __clearFilter(self):
        self.__carouselDP.resetFilter()


class CustomizationFilterPopoverViewWindow(PopOverWindow):
    __slots__ = ()

    def __init__(self, event, parent=None, carouselDP=None):
        super(CustomizationFilterPopoverViewWindow, self).__init__(event=event, content=CustomizationFilterPopoverView(R.views.lobby.customization.popovers.CustomizationFilterPopoverView(), carouselDP), parent=parent, layer=WindowLayer.TOP_WINDOW)
