# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/customization_3d_objects/logger.py
from typing import TYPE_CHECKING
from CurrentVehicle import g_currentVehicle
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.Scaleform.daapi.view.common.common_constants import FILTER_POPOVER_SECTION
from gui.Scaleform.daapi.view.common.shared import isVehicleFilterNew
from gui.Scaleform.daapi.view.lobby.customization.shared import CustomizationTabs, vehicleHasSlot
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.customization import ICustomizationService
from uilogging.base.logger import MetricsLogger, ifUILoggingEnabled
from uilogging.customization_3d_objects.logging_constants import ATTACHMENT_TYPE_MAPPING, CUSTOMIZATION_CAROUSEL_MODE_MAPPING, CUSTOMIZATION_CAROUSEL_TAB_MAPPING, FEATURE, VEHICLE_CUSTOMIZATION_FILTER_MAPPING, CustomizationActions, CustomizationCarouselStates, CustomizationChamomileButtons, CustomizationFilterButtons, CustomizationTutorialStates, CustomizationFilterTypes, CustomizationViewKeys
from wotdecorators import noexcept
if TYPE_CHECKING:
    from typing import Optional, Union, Dict
    from uilogging.types import ItemType, InfoType, ItemStateType, ParentScreenType
    from uilogging.customization_3d_objects.logging_constants import CustomizationButtons
    from items.components.c11n_constants import Rarity
    from gui.customization.shared import C11nId
    from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_environment import ICarouselEnvironment
    from gui.Scaleform.daapi.view.lobby.customization.context.context import CustomizationContext
    from gui.Scaleform.daapi.view.lobby.customization.customization_carousel import CarouselCache

class CustomizationMetricsLogger(MetricsLogger):
    __slots__ = ('_parentScreen',)

    def __init__(self, parentScreen=None):
        super(CustomizationMetricsLogger, self).__init__(FEATURE)
        self._parentScreen = CUSTOMIZATION_CAROUSEL_TAB_MAPPING.get(parentScreen, parentScreen)

    def _logAction(self, action, item, itemState=None, parentScreen=None, info=None):
        self.log(action=action, item=item, itemState=itemState, parentScreen=parentScreen or self._parentScreen, info=info)

    def onViewOpen(self, view, itemState=None, parentScreen=None, info=None):
        self._logAction(action=CustomizationActions.OPEN, item=view, itemState=itemState, parentScreen=parentScreen, info=info)

    def onViewClose(self, view, itemState=None, parentScreen=None, info=None):
        self._logAction(action=CustomizationActions.CLOSE, item=view, itemState=itemState, parentScreen=parentScreen, info=info)

    def onClick(self, item, itemState=None, parentScreen=None, info=None):
        self._logAction(action=CustomizationActions.CLICK, item=item, itemState=itemState, parentScreen=parentScreen, info=info)


class _TutorialMixin(object):
    __slots__ = ()

    def onHintButtonClick(self, button, isTutorial, parentScreen=None, info=None):
        self.onClick(item=button, itemState=self._getTutorialState(isTutorial), parentScreen=parentScreen, info=info)

    def _getTutorialState(self, isTutorial):
        return CustomizationTutorialStates.IS_TUTORIAL if isTutorial else CustomizationTutorialStates.IS_NOT_TUTORIAL


class CustomizationMainViewLogger(CustomizationMetricsLogger):
    __slots__ = ()

    @noexcept
    def onAnchorClick(self, slotId, parentScreen=None):
        if slotId.slotType != GUI_ITEM_TYPE.ATTACHMENT:
            return
        slot = g_currentVehicle.item.getAnchorBySlotId(slotId.slotType, slotId.areaId, slotId.regionIdx)
        self.onClick(item=ATTACHMENT_TYPE_MAPPING[slot.applyType], parentScreen=parentScreen)


class CustomizationPropertySheetLogger(CustomizationMetricsLogger):
    __slots__ = ()

    def onChamomileClick(self, button, slotId):
        if not self.__needToLogForSlot(slotId):
            return
        self.onClick(item=button)

    @noexcept
    def onScaleClick(self, scaleIndex, slotId):
        if not self.__needToLogForSlot(slotId):
            return
        self.onClick(item=CustomizationChamomileButtons.ALL_SCALE[scaleIndex])

    def __needToLogForSlot(self, slotId):
        return slotId.slotType == GUI_ITEM_TYPE.ATTACHMENT


class CustomizationAmmunitionPanelLogger(CustomizationMetricsLogger, _TutorialMixin):
    __slots__ = ()


class CustomizationBottomPanelLogger(CustomizationMetricsLogger, _TutorialMixin):
    __slots__ = ('__ctx',)
    __service = dependency.descriptor(ICustomizationService)

    def __init__(self, parentScreen=None):
        super(CustomizationBottomPanelLogger, self).__init__(parentScreen)
        self.__ctx = self.__service.getCtx()

    @noexcept
    @ifUILoggingEnabled()
    def onTabOpened(self, tabId):
        super(CustomizationBottomPanelLogger, self)._logAction(action=CustomizationActions.OPEN, item=CUSTOMIZATION_CAROUSEL_TAB_MAPPING[tabId], itemState=self.__getCarouselState(tabId), info=CUSTOMIZATION_CAROUSEL_MODE_MAPPING[self.__ctx.modeId])

    @noexcept
    @ifUILoggingEnabled()
    def onViewOpen(self, view):
        tabId = self.__ctx.mode.tabId
        super(CustomizationBottomPanelLogger, self).onViewOpen(view=view, itemState=self.__getCarouselState(tabId), parentScreen=CUSTOMIZATION_CAROUSEL_TAB_MAPPING[tabId])

    @noexcept
    @ifUILoggingEnabled()
    def onViewClose(self, view):
        tabId = self.__ctx.mode.tabId
        super(CustomizationBottomPanelLogger, self).onViewClose(view=view, itemState=self.__getCarouselState(tabId), parentScreen=CUSTOMIZATION_CAROUSEL_TAB_MAPPING[tabId])

    @noexcept
    @ifUILoggingEnabled()
    def onButtonClick(self, button):
        tabId = self.__ctx.mode.tabId
        self.onClick(item=button, itemState=self.__getCarouselState(tabId), parentScreen=CUSTOMIZATION_CAROUSEL_TAB_MAPPING[tabId])

    @noexcept
    @ifUILoggingEnabled()
    def onHintButtonClick(self, button, isTutorial):
        tabId = self.__ctx.mode.tabId
        super(CustomizationBottomPanelLogger, self).onHintButtonClick(button=button, isTutorial=isTutorial, parentScreen=CUSTOMIZATION_CAROUSEL_TAB_MAPPING[tabId], info=self.__getCarouselState(tabId))

    @noexcept
    def onPrimaryFilterClick(self, index):
        if not self.__needToLogFilterClick():
            return
        self.onClick(item=(CustomizationFilterButtons.IN_DEPOT, CustomizationFilterButtons.APPLIED)[index], info=CustomizationFilterTypes.PRIMARY)

    def __getCarouselState(self, tabId):
        if tabId == CustomizationTabs.ATTACHMENTS:
            attachments = g_currentVehicle.itemsCache.items.getItems(GUI_ITEM_TYPE.ATTACHMENT, REQ_CRITERIA.CUSTOMIZATION.ON_ACCOUNT | REQ_CRITERIA.CUSTOM(lambda item: not item.descriptor.isHiddenInUI()))
            if not attachments:
                return CustomizationCarouselStates.TOTAL_ZERO_STATE
            if vehicleHasSlot(GUI_ITEM_TYPE.ATTACHMENT):
                return CustomizationCarouselStates.NON_ZERO_STATE
            return CustomizationCarouselStates.VEHICLE_ZERO_STATE
        return CustomizationCarouselStates.NONE

    def __needToLogFilterClick(self):
        return self.__ctx.mode.tabId == CustomizationTabs.ATTACHMENTS


class VehicleSidebarLogger(CustomizationMetricsLogger):
    __slots__ = ()


class CustomizationFilterLogger(CustomizationMetricsLogger):
    __slots__ = ('__ctx',)
    __service = dependency.descriptor(ICustomizationService)

    def __init__(self, parentScreen=None):
        super(CustomizationFilterLogger, self).__init__(parentScreen)
        self.__ctx = self.__service.getCtx()

    @noexcept
    def onViewOpen(self, view, parentScreen=None):
        if not self.__needToLogFilterClick():
            return
        super(CustomizationFilterLogger, self).onViewOpen(view=view, parentScreen=parentScreen)

    @noexcept
    def onViewClose(self, view, parentScreen=None):
        if not self.__needToLogFilterClick():
            return
        super(CustomizationFilterLogger, self).onViewClose(view=view, parentScreen=parentScreen)

    @noexcept
    def onFilterClick(self, button, parentScreen=None):
        if not self.__needToLogFilterClick():
            return
        self.onClick(item=button, parentScreen=parentScreen)

    @noexcept
    def onPrimaryFilterClick(self, button):
        if not self.__needToLogFilterClick():
            return
        self.onClick(item=button, info=CustomizationFilterTypes.PRIMARY)

    @noexcept
    def onRarityFilterClick(self, rarity):
        if not self.__needToLogFilterClick():
            return
        self.onClick(item=CustomizationFilterButtons.RARITY_TEMPLATE.value.format(rarity), info=CustomizationFilterTypes.RARITY)

    @noexcept
    def onGroupFilterClick(self, carouselCache, groupIndex, parentScreen=None, isReset=False):
        if isReset or not self.__needToLogFilterClick():
            return
        groups = carouselCache.getItemsData().groups.values()
        if groupIndex >= len(groups):
            groupName = CustomizationFilterButtons.ALL_GROUPS.value
        else:
            groupName = groups[groupIndex]
            groupName = groupName.replace(' ', '_')
            groupName = groupName.lower()
        self.onClick(item=CustomizationFilterButtons.GROUP_TEMPLATE.value.format(groupName), info=CustomizationFilterTypes.GROUPS, parentScreen=parentScreen)

    def __needToLogFilterClick(self):
        return self.__ctx.mode.tabId == CustomizationTabs.ATTACHMENTS


class CustomizationHangarVehicleFilterLogger(CustomizationMetricsLogger, _TutorialMixin):
    __slots__ = ()

    @noexcept
    @ifUILoggingEnabled()
    def onFilterButtonClick(self, carousel, mapping, sectionId, itemId):
        if carousel is not None and carousel.filter is not None:
            if sectionId != FILTER_POPOVER_SECTION.CUSTOMIZATION:
                return
            filterKey = mapping[sectionId][itemId]
            self.onClick(item=VEHICLE_CUSTOMIZATION_FILTER_MAPPING[filterKey], itemState=self._getTutorialState(isVehicleFilterNew(filterKey)))
        return


class CustomizationRarityRewardViewLogger(CustomizationMetricsLogger):
    __slots__ = ()
