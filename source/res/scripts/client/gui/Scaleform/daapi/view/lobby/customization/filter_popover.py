# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/filter_popover.py
from gui.Scaleform.daapi.view.meta.CustomizationFiltersPopoverMeta import CustomizationFiltersPopoverMeta
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.shared.formatters import text_styles
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from skeletons.gui.customization import ICustomizationService

class FiltersPopoverVO(object):
    __slots__ = ('lblTitle', 'lblGroups', 'lblShowOnlyFilters', 'btnDefault', 'basicFilterType', 'groupType', 'btnDefaultTooltip', 'groupTypeSelectedIndex', 'lblShowOnlyHistoric', 'lblShowOnlyAcquired', 'tooltipShowOnlyHistoric', 'tooltipShowOnlyAcquired', 'valueShowOnlyHistoric', 'valueShowOnlyAcquired')

    def __init__(self, lblTitle, lblGroups, lblShowOnlyFilters, btnDefault, groupType, btnDefaultTooltip, groupTypeSelectedIndex, lblShowOnlyHistoric, lblShowOnlyAcquired, tooltipShowOnlyHistoric, tooltipShowOnlyAcquired, valueShowOnlyHistoric, valueShowOnlyAcquired):
        self.lblTitle = lblTitle
        self.lblGroups = lblGroups
        self.lblShowOnlyFilters = lblShowOnlyFilters
        self.btnDefault = btnDefault
        self.groupType = groupType
        self.btnDefaultTooltip = btnDefaultTooltip
        self.groupTypeSelectedIndex = groupTypeSelectedIndex
        self.lblShowOnlyHistoric = lblShowOnlyHistoric
        self.lblShowOnlyAcquired = lblShowOnlyAcquired
        self.tooltipShowOnlyHistoric = tooltipShowOnlyHistoric
        self.tooltipShowOnlyAcquired = tooltipShowOnlyAcquired
        self.valueShowOnlyHistoric = valueShowOnlyHistoric
        self.valueShowOnlyAcquired = valueShowOnlyAcquired

    def asDict(self):
        return {'lblTitle': self.lblTitle,
         'lblGroups': self.lblGroups,
         'lblShowOnlyFilters': self.lblShowOnlyFilters,
         'btnDefault': self.btnDefault,
         'groupType': self.groupType,
         'btnDefaultTooltip': self.btnDefaultTooltip,
         'groupTypeSelectedIndex': self.groupTypeSelectedIndex,
         'lblShowOnlyHistoric': self.lblShowOnlyHistoric,
         'lblShowOnlyAcquired': self.lblShowOnlyAcquired,
         'tooltipShowOnlyHistoric': self.tooltipShowOnlyHistoric,
         'tooltipShowOnlyAcquired': self.tooltipShowOnlyAcquired,
         'valueShowOnlyHistoric': self.valueShowOnlyHistoric,
         'valueShowOnlyAcquired': self.valueShowOnlyAcquired}


class FilterPopover(CustomizationFiltersPopoverMeta):
    service = dependency.descriptor(ICustomizationService)

    def __init__(self, ctx=None):
        super(FilterPopover, self).__init__()
        self.__groupsMap = []
        data = ctx['data']
        self._purchasedToggleEnabled = data.purchasedEnabled
        self._historicToggleEnabled = data.historicEnabled
        self._groups = data.groups
        self._selectedGroup = data.selectedGroup
        self._groupCount = data.groupCount
        if hasattr(data, 'isInit'):
            self._isInit = data.isInit
        else:
            self._isInit = False
        self.__updateVO = self.__createUpdateVO()

    def setShowOnlyHistoric(self, value):
        self._historicToggleEnabled = value
        self.updateDefaultButton()
        self.service.onCarouselFilter(historic=value)

    def setShowOnlyAcquired(self, value):
        self._purchasedToggleEnabled = value
        self.updateDefaultButton()
        self.service.onCarouselFilter(inventory=value)

    def changeGroup(self, filterGroupValue):
        if not self._isInit:
            self.service.onCarouselFilter(group=filterGroupValue)
            self._selectedGroup = filterGroupValue
            self.updateDefaultButton()
        else:
            self._isInit = False

    def updateDefaultButton(self):
        defaultGroup = self._selectedGroup == self._groupCount - 1
        notDefault = not defaultGroup or self._historicToggleEnabled or self._purchasedToggleEnabled
        self.as_enableDefBtnS(notDefault)

    def setDefaultFilter(self):
        self._historicToggleEnabled = False
        self._purchasedToggleEnabled = False
        self._selectedGroup = self._groupCount - 1
        self.__updateVO = self.__createUpdateVO()
        self.as_setDataS(self.__updateVO.asDict())
        self.updateDefaultButton()
        self.service.onCarouselFilter(historic=self._historicToggleEnabled, inventory=self._purchasedToggleEnabled, group=self._selectedGroup)

    def _populate(self):
        super(FilterPopover, self)._populate()
        self.as_setDataS(self.__updateVO.asDict())
        self.updateDefaultButton()

    def _dispose(self):
        self.__groupsMap = []
        super(FilterPopover, self)._dispose()

    def __createUpdateVO(self):
        return FiltersPopoverVO(lblTitle=text_styles.highTitle(VEHICLE_CUSTOMIZATION.FILTER_POPOVER_TITLE), lblGroups=text_styles.standard(VEHICLE_CUSTOMIZATION.FILTER_POPOVER_GROUPS_TITLE), lblShowOnlyFilters=text_styles.standard(VEHICLE_CUSTOMIZATION.FILTER_POPOVER_SHOWONLYFILTERS_TITLE), btnDefault=VEHICLE_CUSTOMIZATION.FILTER_POPOVER_GETDEFAULTSETTINGS, groupType=self._groups if self._groupCount > 1 else None, btnDefaultTooltip=makeTooltip(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_FILTERPOPOVER_REFRESH_HEADER, VEHICLE_CUSTOMIZATION.CUSTOMIZATION_FILTERPOPOVER_REFRESH_BODY), groupTypeSelectedIndex=self._selectedGroup, lblShowOnlyHistoric=VEHICLE_CUSTOMIZATION.FILTER_POPOVER_SHOWONLYFILTERS_HISTORIC, lblShowOnlyAcquired=VEHICLE_CUSTOMIZATION.FILTER_POPOVER_SHOWONLYFILTERS_ACQUIRED, tooltipShowOnlyHistoric=TOOLTIPS.FILTER_POPOVER_SHOWONLYFILTERS_HISTORIC, tooltipShowOnlyAcquired=TOOLTIPS.FILTER_POPOVER_SHOWONLYFILTERS_ACQUIRED, valueShowOnlyHistoric=self._historicToggleEnabled, valueShowOnlyAcquired=self._purchasedToggleEnabled)
