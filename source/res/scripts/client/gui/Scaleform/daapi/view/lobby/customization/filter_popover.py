# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/filter_popover.py
from gui.Scaleform.daapi.view.meta.CustomizationFiltersPopoverMeta import CustomizationFiltersPopoverMeta
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.shared.formatters import text_styles
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from skeletons.gui.customization import ICustomizationService
from gui.Scaleform.locale.RES_ICONS import RES_ICONS

class FiltersPopoverVO(object):
    __slots__ = ('lblTitle', 'lblGroups', 'lblShowOnlyFilters', 'btnDefault', 'basicFilterType', 'groupType', 'btnDefaultTooltip', 'groupTypeSelectedIndex', 'filterBtns')

    def __init__(self, lblTitle, lblGroups, lblShowOnlyFilters, btnDefault, groupType, btnDefaultTooltip, groupTypeSelectedIndex, filterBtns):
        self.lblTitle = lblTitle
        self.lblGroups = lblGroups
        self.lblShowOnlyFilters = lblShowOnlyFilters
        self.btnDefault = btnDefault
        self.groupType = groupType
        self.btnDefaultTooltip = btnDefaultTooltip
        self.groupTypeSelectedIndex = groupTypeSelectedIndex
        self.filterBtns = filterBtns

    def asDict(self):
        return {'lblTitle': self.lblTitle,
         'lblGroups': self.lblGroups,
         'lblShowOnlyFilters': self.lblShowOnlyFilters,
         'btnDefault': self.btnDefault,
         'groupType': self.groupType,
         'btnDefaultTooltip': self.btnDefaultTooltip,
         'groupTypeSelectedIndex': self.groupTypeSelectedIndex,
         'filterBtns': self.filterBtns}


class FilterPopover(CustomizationFiltersPopoverMeta):
    service = dependency.descriptor(ICustomizationService)

    def __init__(self, ctx=None):
        super(FilterPopover, self).__init__()
        self.__groupsMap = []
        self.__ctx = None
        data = ctx['data']
        self._purchasedToggleEnabled = data.purchasedEnabled
        self._historicToggleEnabled = data.historicEnabled
        self._appliedToggleEnabled = data.appliedEnabled
        self._groups = data.groups
        self._selectedGroup = data.selectedGroup
        self._groupCount = data.groupCount
        if hasattr(data, 'isInit'):
            self._isInit = data.isInit
        else:
            self._isInit = False
        self.__updateVO = self.__createUpdateVO()
        return

    def onFilterChange(self, index, value):
        (self.setShowOnlyHistoric, self.setShowOnlyAcquired, self.setShowOnlyApplied)[index](value)

    def setShowOnlyHistoric(self, value):
        self._historicToggleEnabled = value
        self.updateDefaultButton()
        self.__ctx.applyCarouselFilter(historic=value)

    def setShowOnlyAcquired(self, value):
        self._purchasedToggleEnabled = value
        self.updateDefaultButton()
        self.__ctx.applyCarouselFilter(inventory=value)

    def setShowOnlyApplied(self, value):
        self._appliedToggleEnabled = value
        self.updateDefaultButton()
        self.__ctx.applyCarouselFilter(applied=value)

    def changeGroup(self, filterGroupValue):
        if not self._isInit:
            self.__ctx.applyCarouselFilter(group=filterGroupValue)
            self._selectedGroup = filterGroupValue
            self.updateDefaultButton()
        else:
            self._isInit = False

    def updateDefaultButton(self):
        defaultGroup = self._selectedGroup == self._groupCount - 1
        notDefault = not defaultGroup or self._historicToggleEnabled or self._purchasedToggleEnabled or self._appliedToggleEnabled
        self.as_enableDefBtnS(notDefault)

    def setDefaultFilter(self):
        self._historicToggleEnabled = False
        self._purchasedToggleEnabled = False
        self._appliedToggleEnabled = False
        self._selectedGroup = self._groupCount - 1
        self.__updateVO = self.__createUpdateVO()
        self.as_setDataS(self.__updateVO.asDict())
        self.updateDefaultButton()
        self.__ctx.applyCarouselFilter(historic=self._historicToggleEnabled, inventory=self._purchasedToggleEnabled, applied=self._appliedToggleEnabled, group=self._selectedGroup)

    def _populate(self):
        super(FilterPopover, self)._populate()
        self.as_setDataS(self.__updateVO.asDict())
        self.__ctx = self.service.getCtx()
        self.updateDefaultButton()

    def _dispose(self):
        self.__groupsMap = []
        self.__ctx = None
        super(FilterPopover, self)._dispose()
        return

    def __createUpdateVO(self):
        self._filterBtns = [{'value': RES_ICONS.MAPS_ICONS_BUTTONS_NON_HISTORICAL,
          'tooltip': VEHICLE_CUSTOMIZATION.CAROUSEL_FILTER_NONHISTORICALBTN,
          'selected': self._historicToggleEnabled}, {'value': RES_ICONS.MAPS_ICONS_CUSTOMIZATION_STORAGE_ICON,
          'tooltip': VEHICLE_CUSTOMIZATION.CAROUSEL_FILTER_STORAGEBTN,
          'selected': self._purchasedToggleEnabled}, {'value': RES_ICONS.MAPS_ICONS_BUTTONS_EQUIPPED_ICON,
          'tooltip': VEHICLE_CUSTOMIZATION.CAROUSEL_FILTER_EQUIPPEDBTN,
          'selected': self._appliedToggleEnabled}]
        return FiltersPopoverVO(lblTitle=text_styles.highTitle(VEHICLE_CUSTOMIZATION.FILTER_POPOVER_TITLE), lblGroups=text_styles.standard(VEHICLE_CUSTOMIZATION.FILTER_POPOVER_GROUPS_TITLE), lblShowOnlyFilters=text_styles.standard(VEHICLE_CUSTOMIZATION.FILTER_POPOVER_SHOWONLYFILTERS_TITLE), btnDefault=VEHICLE_CUSTOMIZATION.FILTER_POPOVER_GETDEFAULTSETTINGS, groupType=self._groups if self._groupCount > 1 else None, btnDefaultTooltip=makeTooltip(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_FILTERPOPOVER_REFRESH_HEADER, VEHICLE_CUSTOMIZATION.CUSTOMIZATION_FILTERPOPOVER_REFRESH_BODY), groupTypeSelectedIndex=self._selectedGroup, filterBtns=self._filterBtns)
