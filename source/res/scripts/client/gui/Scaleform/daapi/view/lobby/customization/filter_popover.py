# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/filter_popover.py
import logging
from collections import OrderedDict
from account_helpers.AccountSettings import AccountSettings, CustomizationFilter
from gui.customization.constants import CustomizationModes
from gui.customization.shared import PROJECTION_DECAL_TEXT_FORM_TAG
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.meta.CustomizationFiltersPopoverMeta import CustomizationFiltersPopoverMeta
from gui.Scaleform.daapi.view.lobby.customization.shared import CustomizationTabs
from gui.Scaleform.genConsts.CUSTOMIZATION_CONSTS import CUSTOMIZATION_CONSTS
from gui.shared.formatters import text_styles
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from items.components.c11n_constants import ProjectionDecalFormTags
from skeletons.gui.customization import ICustomizationService
_logger = logging.getLogger(__name__)

class FiltersPopoverVO(object):
    __slots__ = ('lblTitle', 'lblGroups', 'filtersGroupLblMain', 'filtersGroupLblHistorical', 'filtersGroupLblEditable', 'lblAdditional', 'additionalCheckBoxData', 'btnDefault', 'basicFilterType', 'groupType', 'btnDefaultTooltip', 'groupTypeSelectedIndex', 'filterBtnsGroupMain', 'filterBtnsGroupHistorical', 'filterBtnsGroupEditable', 'additionalEnabled', 'formsBtns', 'formsBtnsLbl', 'lblDisplayBy', 'displayBy', 'displayBySelectedIndex')

    def __init__(self, lblTitle, lblGroups, filtersGroupLblMain, filtersGroupLblHistorical, filtersGroupLblEditable, lblAdditional, additionalCheckBoxData, btnDefault, groupType, btnDefaultTooltip, groupTypeSelectedIndex, filterBtnsGroupMain, filterBtnsGroupHistorical, filterBtnsGroupEditable, additionalEnabled, lblDisplayBy, displayBy, displayBySelectedIndex, formsBtns=None, formsBtnsLbl=''):
        self.lblTitle = lblTitle
        self.lblGroups = lblGroups
        self.filtersGroupLblMain = filtersGroupLblMain
        self.filtersGroupLblHistorical = filtersGroupLblHistorical
        self.filtersGroupLblEditable = filtersGroupLblEditable
        self.lblAdditional = lblAdditional
        self.additionalCheckBoxData = additionalCheckBoxData
        self.btnDefault = btnDefault
        self.groupType = groupType
        self.btnDefaultTooltip = btnDefaultTooltip
        self.groupTypeSelectedIndex = groupTypeSelectedIndex
        self.filterBtnsGroupMain = filterBtnsGroupMain
        self.filterBtnsGroupHistorical = filterBtnsGroupHistorical
        self.filterBtnsGroupEditable = filterBtnsGroupEditable
        self.additionalEnabled = additionalEnabled
        self.formsBtns = formsBtns
        self.formsBtnsLbl = formsBtnsLbl
        self.lblDisplayBy = lblDisplayBy
        self.displayBy = displayBy
        self.displayBySelectedIndex = displayBySelectedIndex

    def asDict(self):
        return {'lblTitle': self.lblTitle,
         'lblGroups': self.lblGroups,
         'filtersGroupLblMain': self.filtersGroupLblMain,
         'filtersGroupLblHistorical': self.filtersGroupLblHistorical,
         'filtersGroupLblEditable': self.filtersGroupLblEditable,
         'lblAdditional': self.lblAdditional,
         'additionalCheckBoxData': self.additionalCheckBoxData,
         'btnDefault': self.btnDefault,
         'groupType': self.groupType,
         'btnDefaultTooltip': self.btnDefaultTooltip,
         'groupTypeSelectedIndex': self.groupTypeSelectedIndex,
         'filterBtnsGroupMain': self.filterBtnsGroupMain,
         'filterBtnsGroupHistorical': self.filterBtnsGroupHistorical,
         'filterBtnsGroupEditable': self.filterBtnsGroupEditable,
         'additionalEnabled': self.additionalEnabled,
         'formsBtns': self.formsBtns,
         'formsBtnsLbl': self.formsBtnsLbl,
         'lblDisplayBy': self.lblDisplayBy,
         'displayBy': self.displayBy,
         'displayBySelectedIndex': self.displayBySelectedIndex}


class FilterPopover(CustomizationFiltersPopoverMeta):
    PROJECTION_DECAL_IMAGE_FORM_TAG = {ProjectionDecalFormTags.SQUARE: backport.image(R.images.gui.maps.icons.customization.icon_form_1_c()),
     ProjectionDecalFormTags.RECT1X2: backport.image(R.images.gui.maps.icons.customization.icon_form_2_c()),
     ProjectionDecalFormTags.RECT1X3: backport.image(R.images.gui.maps.icons.customization.icon_form_3_c()),
     ProjectionDecalFormTags.RECT1X4: backport.image(R.images.gui.maps.icons.customization.icon_form_4_c()),
     ProjectionDecalFormTags.RECT1X6: backport.image(R.images.gui.maps.icons.customization.icon_form_6())}
    service = dependency.descriptor(ICustomizationService)

    def __init__(self, ctx=None):
        super(FilterPopover, self).__init__()
        self.__ctx = None
        self.__filterChangeHandlersMap = {CUSTOMIZATION_CONSTS.FILTER_GROUP_MAIN: [self.setShowOnlyAcquired, self.setShowOnlyApplied, self.setShowOnlyFavorite],
         CUSTOMIZATION_CONSTS.FILTER_GROUP_HISTORICAL: [self.setShowOnlyFantastical, self.setShowOnlyNonHistoric, self.setShowOnlyHistoric],
         CUSTOMIZATION_CONSTS.FILTER_GROUP_EDITABLE: []}
        data = ctx['data']
        self._purchasedToggleEnabled = data.purchasedEnabled
        self._historicToggleEnabled = data.historicEnabled
        self._nonHistoricToggleEnabled = data.nonHistoricEnabled
        self._fantasticalToggleEnabled = data.fantasticalEnabled
        self._appliedToggleEnabled = data.appliedEnabled
        self._favoriteToggleEnabled = data.favoriteEnabled
        self._groups = data.groups
        self._displayGroups = data.displayGroups
        self._selectedGroup = data.selectedGroup
        self._groupCount = data.groupCount
        self._hideOnAnotherVehEnabled = data.hideOnAnotherVehEnabled
        self._showOnlyProgressionDecalsEnabled = data.showOnlyProgressionDecalsEnabled
        self._showOnlyEditableStylesEnabled = data.showOnlyEditableStylesEnabled
        self._showOnlyNonEditableStylesEnabled = data.showOnlyNonEditableStylesEnabled
        self._showOnlyProgressionStylesEnabled = data.showOnlyProgressionStylesEnabled
        self._formfactorTypes = OrderedDict()
        for i, val in enumerate(data.formfactorGroups):
            if i <= len(ProjectionDecalFormTags.ALL):
                self._formfactorTypes[ProjectionDecalFormTags.ALL[i]] = val

        if hasattr(data, 'isInit'):
            self._isInit = data.isInit
            self._isInitDisplay = data.isInit
        else:
            self._isInit = False
            self._isInitDisplay = False
        return

    def onFilterChange(self, groupId, index, value):
        self.__filterChangeHandlersMap[groupId][index](value)

    def onFormChange(self, index, value):
        if not self._formfactorTypes:
            return
        if index >= len(ProjectionDecalFormTags.ALL):
            _logger.warning('"index" = %(index)s is not valid', {'index': index})
            return
        formFactor = ProjectionDecalFormTags.ALL[index]
        if formFactor not in self._formfactorTypes:
            _logger.warning('"index" = %(index)s is not valid  (self._formfactorTypes = %(formfactorTypes)s)', {'index': index,
             'formfactorTypes': self._formfactorTypes})
            return
        self._formfactorTypes[formFactor] = value
        self.__ctx.events.onCarouselFiltered(formfactorGroups=self._formfactorTypes)
        self.updateDefaultButton()

    def setShowOnlyHistoric(self, value):
        self._historicToggleEnabled = value
        self.updateDefaultButton()
        self.__ctx.events.onCarouselFiltered(historic=value)

    def setShowOnlyNonHistoric(self, value):
        self._nonHistoricToggleEnabled = value
        self.updateDefaultButton()
        self.__ctx.events.onCarouselFiltered(nonHistoric=value)

    def setShowOnlyFantastical(self, value):
        self._fantasticalToggleEnabled = value
        self.updateDefaultButton()
        self.__ctx.events.onCarouselFiltered(fantastical=value)

    def setShowOnlyAcquired(self, value):
        self._purchasedToggleEnabled = value
        self.updateDefaultButton()
        self.__ctx.events.onCarouselFiltered(inventory=value)

    def setShowOnlyFavorite(self, value):
        self._favoriteToggleEnabled = value
        self.updateDefaultButton()
        self.__ctx.events.onCarouselFiltered(favorite=value)

    def setHideOnAnotherVeh(self, value):
        self._hideOnAnotherVehEnabled = value
        self.updateDefaultButton()
        self.__ctx.events.onCarouselFiltered(onAnotherVeh=value)

    def setShowOnlyProgressionDecals(self, value):
        self._showOnlyProgressionDecalsEnabled = value
        self.updateDefaultButton()
        self.__ctx.events.onCarouselFiltered(onlyProgressionDecals=value)

    def setShowOnlyEditableStyles(self, value):
        self._showOnlyEditableStylesEnabled = value
        self.updateDefaultButton()
        self.__ctx.events.onCarouselFiltered(onlyEditableStyles=value)

    def setShowOnlyNonEditableStyles(self, value):
        self._showOnlyNonEditableStylesEnabled = value
        self.updateDefaultButton()
        self.__ctx.events.onCarouselFiltered(onlyNonEditableStyles=value)

    def setShowOnlyProgressionStyles(self, value):
        self._showOnlyProgressionStylesEnabled = value
        self.updateDefaultButton()
        self.__ctx.events.onCarouselFiltered(onlyProgressionStyles=value)

    def setShowOnlyApplied(self, value):
        self._appliedToggleEnabled = value
        self.updateDefaultButton()
        self.__ctx.events.onCarouselFiltered(applied=value)

    def changeGroup(self, filterGroupValue):
        if not self._isInit:
            self.__ctx.events.onCarouselFiltered(group=filterGroupValue)
            self._selectedGroup = filterGroupValue
            self.updateDefaultButton()
        else:
            self._isInit = False

    def changeDisplayMethod(self, filterGroupValue):
        if not self._isInitDisplay:
            self.__ctx.events.onCarouselFiltered(displayGroup=filterGroupValue)
            self.updateDefaultButton()
        else:
            self._isInitDisplay = False

    def updateDefaultButton(self):
        if self._groupCount > 0:
            defaultGroup = self._selectedGroup == self._groupCount - 1
        else:
            defaultGroup = True
        defaultFormfactorGroups = any(self._formfactorTypes.values())
        notDefault = not defaultGroup or defaultFormfactorGroups or self._historicToggleEnabled or self._nonHistoricToggleEnabled or self._fantasticalToggleEnabled or self._purchasedToggleEnabled or self._hideOnAnotherVehEnabled or self._showOnlyProgressionDecalsEnabled or self._showOnlyEditableStylesEnabled or self._showOnlyNonEditableStylesEnabled or self._showOnlyProgressionStylesEnabled or self._appliedToggleEnabled or self._favoriteToggleEnabled
        self.as_enableDefBtnS(notDefault)

    def setDefaultFilter(self):
        self._historicToggleEnabled = False
        self._nonHistoricToggleEnabled = False
        self._fantasticalToggleEnabled = False
        self._purchasedToggleEnabled = False
        self._appliedToggleEnabled = False
        self._favoriteToggleEnabled = False
        self._hideOnAnotherVehEnabled = False
        self._showOnlyProgressionDecalsEnabled = False
        self._showOnlyEditableStylesEnabled = False
        self._showOnlyNonEditableStylesEnabled = False
        self._showOnlyProgressionStylesEnabled = False
        self._selectedGroup = self._groupCount - 1
        self._formfactorTypes = OrderedDict.fromkeys(self._formfactorTypes, False)
        self.__updateVO = self.__createUpdateVO()
        self.as_setDataS(self.__updateVO.asDict())
        self.updateDefaultButton()
        self.__ctx.events.onCarouselFiltered(historic=self._historicToggleEnabled, nonHistoric=self._nonHistoricToggleEnabled, fantastical=self._fantasticalToggleEnabled, inventory=self._purchasedToggleEnabled, applied=self._appliedToggleEnabled, favorite=self._favoriteToggleEnabled, group=self._selectedGroup, formfactorGroups=self._formfactorTypes, onAnotherVeh=self._hideOnAnotherVehEnabled, onlyProgressionDecals=self._showOnlyProgressionDecalsEnabled, onlyEditableStyles=self._showOnlyEditableStylesEnabled, onlyNonEditableStyles=self._showOnlyNonEditableStylesEnabled, onlyProgressionStyles=self._showOnlyProgressionStylesEnabled)

    def _populate(self):
        super(FilterPopover, self)._populate()
        self.__ctx = self.service.getCtx()
        self.__ctx.events.onCarouselFiltered += self.__onCarouselFiltered
        self.updateDefaultButton()
        self.__updateVO = self.__createUpdateVO()
        self.as_setDataS(self.__updateVO.asDict())
        self.__onCarouselFiltered()

    def _dispose(self):
        if self.__ctx.events is not None:
            self.__ctx.events.onFilterPopoverClosed()
            self.__ctx.events.onCarouselFiltered -= self.__onCarouselFiltered
        self.__ctx = None
        self.__filterChangeHandlers = None
        super(FilterPopover, self)._dispose()
        return

    def __onCarouselFiltered(self, *args, **kwargs):
        current, total = self.__ctx.carouselItemsCounts
        newHiddenElementsCount = self.__ctx.newHiddenElementsCount
        self.as_updateCounterS(current, total, newHiddenElementsCount)

    def __createUpdateVO(self):
        _filterBtnsMain = [{'value': backport.image(R.images.gui.maps.icons.customization.storage_icon()),
          'tooltip': makeTooltip(backport.text(R.strings.vehicle_customization.carousel.filter.storageBtn.header()), backport.text(R.strings.vehicle_customization.carousel.filter.storageBtn.body())),
          'selected': self._purchasedToggleEnabled}, {'value': backport.image(R.images.gui.maps.icons.buttons.equipped_icon()),
          'tooltip': makeTooltip(backport.text(R.strings.vehicle_customization.carousel.filter.equippedBtn.header()), backport.text(R.strings.vehicle_customization.carousel.filter.equippedBtn.body())),
          'selected': self._appliedToggleEnabled}, {'value': backport.image(R.images.gui.maps.icons.buttons.favorite_small()),
          'tooltip': makeTooltip(backport.text(R.strings.vehicle_customization.customization.filterPopover.favoriteBtn.header()), backport.text(R.strings.vehicle_customization.customization.filterPopover.favoriteBtn.body())),
          'selected': self._favoriteToggleEnabled}]
        _filterBtnsHistorical = [{'value': backport.image(R.images.gui.maps.icons.buttons.fantastical()),
          'tooltip': makeTooltip(backport.text(R.strings.vehicle_customization.carousel.filter.fantasticalBtn.header()), backport.text(R.strings.vehicle_customization.carousel.filter.fantasticalBtn.body())),
          'selected': self._fantasticalToggleEnabled}, {'value': backport.image(R.images.gui.maps.icons.buttons.non_historical()),
          'tooltip': makeTooltip(backport.text(R.strings.vehicle_customization.carousel.filter.nonHistoricalBtn.header()), backport.text(R.strings.vehicle_customization.carousel.filter.nonHistoricalBtn.body())),
          'selected': self._nonHistoricToggleEnabled}, {'value': backport.image(R.images.gui.maps.icons.buttons.hist_small()),
          'tooltip': makeTooltip(backport.text(R.strings.vehicle_customization.carousel.filter.historicalBtn.header()), backport.text(R.strings.vehicle_customization.carousel.filter.historicalBtn.body())),
          'selected': self._historicToggleEnabled}]
        _filterBtnsEditable = []
        if self.__ctx.modeId == CustomizationModes.STYLED:
            _filterBtnsEditable.append({'value': backport.image(R.images.gui.maps.icons.buttons.editable_small()),
             'tooltip': makeTooltip(backport.text(R.strings.vehicle_customization.customization.filterPopover.editableStylesBtn.header()), backport.text(R.strings.vehicle_customization.customization.filterPopover.editableStylesBtn.body())),
             'selected': self._showOnlyEditableStylesEnabled})
            _filterBtnsEditable.append({'value': backport.image(R.images.gui.maps.icons.buttons.non_editable()),
             'tooltip': makeTooltip(backport.text(R.strings.vehicle_customization.customization.filterPopover.nonEditableStylesBtn.header()), backport.text(R.strings.vehicle_customization.customization.filterPopover.nonEditableStylesBtn.body())),
             'selected': self._showOnlyNonEditableStylesEnabled})
            _filterBtnsEditable.append({'value': backport.image(R.images.gui.maps.icons.buttons.progression_0_small()),
             'tooltip': makeTooltip(backport.text(R.strings.vehicle_customization.customization.filterPopover.progressiveStyleBtn.header()), backport.text(R.strings.vehicle_customization.customization.filterPopover.progressiveStyleBtn.body())),
             'selected': self._showOnlyProgressionStylesEnabled})
            self.__filterChangeHandlersMap[CUSTOMIZATION_CONSTS.FILTER_GROUP_EDITABLE].extend((self.setShowOnlyEditableStyles, self.setShowOnlyNonEditableStyles, self.setShowOnlyProgressionStyles))
        if self.__ctx.isProgressiveItemsExist and self.__ctx.tabId == CustomizationTabs.PROJECTION_DECALS:
            tooltip = makeTooltip(backport.text(R.strings.vehicle_customization.customization.filterPopover.progressionDecalsBtn.header()), backport.text(R.strings.vehicle_customization.customization.filterPopover.progressionDecalsBtn.body()))
            selected = self._showOnlyProgressionDecalsEnabled
            _filterBtnsEditable.append({'value': backport.image(R.images.gui.maps.icons.buttons.progression()),
             'tooltip': tooltip,
             'selected': selected})
            self.__filterChangeHandlersMap[CUSTOMIZATION_CONSTS.FILTER_GROUP_EDITABLE].append(self.setShowOnlyProgressionDecals)
        self.__filterChangeHandlers = [ handler for handlers in self.__filterChangeHandlersMap.values() for handler in handlers ]
        _formsBtns = [ {'value': self.PROJECTION_DECAL_IMAGE_FORM_TAG[formType],
         'selected': value,
         'tooltip': makeTooltip('{} {}'.format(backport.text(R.strings.vehicle_customization.popover.tooltip.form()), PROJECTION_DECAL_TEXT_FORM_TAG[formType]), backport.text(R.strings.vehicle_customization.popover.tooltip.form.body(), value=backport.text(R.strings.vehicle_customization.form.dyn(formType)())))} for formType, value in self._formfactorTypes.iteritems() ]
        formsBtnsLbl = ''
        if self._formfactorTypes:
            formsBtnsLbl = text_styles.standard(backport.text(R.strings.vehicle_customization.filter.popover.formfilters.title()))
        additionalCheckBoxLabel = backport.text(R.strings.vehicle_customization.filter.popover.showonlyfilters.onAnotherVeh())
        additionalCheckBoxTooltip = makeTooltip(backport.text(R.strings.vehicle_customization.customization.filterPopover.additionalCheckBox.header()), backport.text(R.strings.vehicle_customization.customization.filterPopover.additionalCheckBox.body()))
        filterSettings = AccountSettings.getFilter(CustomizationFilter.CUSTOMIZATION_FILTER)
        return FiltersPopoverVO(lblTitle=text_styles.highTitle(backport.text(R.strings.vehicle_customization.filter.popover.title())), lblGroups=text_styles.standard(backport.text(R.strings.vehicle_customization.filter.popover.groups.title())), lblDisplayBy=text_styles.standard(backport.text(R.strings.vehicle_customization.filter.popover.displayBy.title())), filtersGroupLblMain=text_styles.standard(backport.text(R.strings.vehicle_customization.filter.popover.showonlyfilters.main.title())), filtersGroupLblHistorical=text_styles.standard(backport.text(R.strings.vehicle_customization.filter.popover.showonlyfilters.historical.title())), filtersGroupLblEditable=text_styles.standard(backport.text(R.strings.vehicle_customization.filter.popover.showonlyfilters.editable.title())), lblAdditional=text_styles.standard(backport.text(R.strings.vehicle_customization.filter.popover.showonlyfilters.additional())), additionalCheckBoxData={'label': additionalCheckBoxLabel,
         'tooltip': additionalCheckBoxTooltip,
         'selected': self._hideOnAnotherVehEnabled}, btnDefault=backport.text(R.strings.vehicle_customization.filter.popover.getDefaultSettings()), groupType=self._groups if self._groupCount > 1 else None, displayBy=self._displayGroups if self._groupCount > 1 else None, btnDefaultTooltip=makeTooltip(backport.text(R.strings.vehicle_customization.customization.filterPopover.refresh.header()), backport.text(R.strings.vehicle_customization.customization.filterPopover.refresh.body())), groupTypeSelectedIndex=self._selectedGroup, displayBySelectedIndex=filterSettings[CustomizationFilter.DISPLAY_GROUP], filterBtnsGroupMain=_filterBtnsMain, filterBtnsGroupHistorical=_filterBtnsHistorical, filterBtnsGroupEditable=_filterBtnsEditable, additionalEnabled=self.__ctx.isItemsOnAnotherVeh, formsBtnsLbl=formsBtnsLbl, formsBtns=_formsBtns)
