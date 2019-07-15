# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/filter_popover.py
import logging
from collections import OrderedDict
from gui.Scaleform.daapi.view.meta.CustomizationFiltersPopoverMeta import CustomizationFiltersPopoverMeta
from gui.shared.formatters import text_styles
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from skeletons.gui.customization import ICustomizationService
from items.components.c11n_constants import ProjectionDecalFormTags
from gui.impl import backport
from gui.impl.gen import R
from gui.customization.shared import PROJECTION_DECAL_TEXT_FORM_TAG
_logger = logging.getLogger(__name__)

class FiltersPopoverVO(object):
    __slots__ = ('lblTitle', 'lblGroups', 'lblShowOnlyFilters', 'btnDefault', 'basicFilterType', 'groupType', 'btnDefaultTooltip', 'groupTypeSelectedIndex', 'filterBtns', 'formsBtns', 'formsBtnsLbl')

    def __init__(self, lblTitle, lblGroups, lblShowOnlyFilters, btnDefault, groupType, btnDefaultTooltip, groupTypeSelectedIndex, filterBtns, formsBtns=None, formsBtnsLbl=''):
        self.lblTitle = lblTitle
        self.lblGroups = lblGroups
        self.lblShowOnlyFilters = lblShowOnlyFilters
        self.btnDefault = btnDefault
        self.groupType = groupType
        self.btnDefaultTooltip = btnDefaultTooltip
        self.groupTypeSelectedIndex = groupTypeSelectedIndex
        self.filterBtns = filterBtns
        self.formsBtns = formsBtns
        self.formsBtnsLbl = formsBtnsLbl

    def asDict(self):
        return {'lblTitle': self.lblTitle,
         'lblGroups': self.lblGroups,
         'lblShowOnlyFilters': self.lblShowOnlyFilters,
         'btnDefault': self.btnDefault,
         'groupType': self.groupType,
         'btnDefaultTooltip': self.btnDefaultTooltip,
         'groupTypeSelectedIndex': self.groupTypeSelectedIndex,
         'filterBtns': self.filterBtns,
         'formsBtns': self.formsBtns,
         'formsBtnsLbl': self.formsBtnsLbl}


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
        data = ctx['data']
        self._purchasedToggleEnabled = data.purchasedEnabled
        self._historicToggleEnabled = data.historicEnabled
        self._appliedToggleEnabled = data.appliedEnabled
        self._groups = data.groups
        self._selectedGroup = data.selectedGroup
        self._groupCount = data.groupCount
        self._formfactorTypes = OrderedDict()
        for i, val in enumerate(data.formfactorGroups):
            if i <= len(ProjectionDecalFormTags.ALL):
                self._formfactorTypes[ProjectionDecalFormTags.ALL[i]] = val

        if hasattr(data, 'isInit'):
            self._isInit = data.isInit
        else:
            self._isInit = False
        self.__updateVO = self.__createUpdateVO()
        return

    def onFilterChange(self, index, value):
        (self.setShowOnlyHistoric, self.setShowOnlyAcquired, self.setShowOnlyApplied)[index](value)

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
        self.__ctx.applyCarouselFilter(formfactorGroups=self._formfactorTypes)
        self.updateDefaultButton()

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
        defaultFormfactorGroups = any(self._formfactorTypes.values())
        notDefault = not defaultGroup or defaultFormfactorGroups or self._historicToggleEnabled or self._purchasedToggleEnabled or self._appliedToggleEnabled
        self.as_enableDefBtnS(notDefault)

    def setDefaultFilter(self):
        self._historicToggleEnabled = False
        self._purchasedToggleEnabled = False
        self._appliedToggleEnabled = False
        self._selectedGroup = self._groupCount - 1
        self._formfactorTypes = OrderedDict.fromkeys(self._formfactorTypes, False)
        self.__updateVO = self.__createUpdateVO()
        self.as_setDataS(self.__updateVO.asDict())
        self.updateDefaultButton()
        self.__ctx.applyCarouselFilter(historic=self._historicToggleEnabled, inventory=self._purchasedToggleEnabled, applied=self._appliedToggleEnabled, group=self._selectedGroup, formfactorGroups=self._formfactorTypes)

    def _populate(self):
        super(FilterPopover, self)._populate()
        self.as_setDataS(self.__updateVO.asDict())
        self.__ctx = self.service.getCtx()
        self.updateDefaultButton()

    def _dispose(self):
        self.__ctx.onFilterPopoverClosed()
        self.__ctx = None
        super(FilterPopover, self)._dispose()
        return

    def __createUpdateVO(self):
        _filterBtns = [{'value': backport.image(R.images.gui.maps.icons.buttons.non_historical()),
          'tooltip': makeTooltip(backport.text(R.strings.vehicle_customization.carousel.filter.nonHistoricalBtn.header()), backport.text(R.strings.vehicle_customization.carousel.filter.nonHistoricalBtn.body())),
          'selected': self._historicToggleEnabled}, {'value': backport.image(R.images.gui.maps.icons.customization.storage_icon()),
          'tooltip': makeTooltip(backport.text(R.strings.vehicle_customization.carousel.filter.storageBtn.header()), backport.text(R.strings.vehicle_customization.carousel.filter.storageBtn.body())),
          'selected': self._purchasedToggleEnabled}, {'value': backport.image(R.images.gui.maps.icons.buttons.equipped_icon()),
          'tooltip': makeTooltip(backport.text(R.strings.vehicle_customization.carousel.filter.equippedBtn.header()), backport.text(R.strings.vehicle_customization.carousel.filter.equippedBtn.body())),
          'selected': self._appliedToggleEnabled}]
        _formsBtns = [ {'value': self.PROJECTION_DECAL_IMAGE_FORM_TAG[formType],
         'selected': value,
         'tooltip': makeTooltip('{} {}'.format(backport.text(R.strings.vehicle_customization.popover.tooltip.form()), PROJECTION_DECAL_TEXT_FORM_TAG[formType]), backport.text(R.strings.vehicle_customization.popover.tooltip.form.body(), value=backport.text(R.strings.vehicle_customization.form.dyn(formType)())))} for formType, value in self._formfactorTypes.iteritems() ]
        formsBtnsLbl = ''
        if self._formfactorTypes:
            formsBtnsLbl = text_styles.standard(backport.text(R.strings.vehicle_customization.filter.popover.formfilters.title()))
        return FiltersPopoverVO(lblTitle=text_styles.highTitle(backport.text(R.strings.vehicle_customization.filter.popover.title())), lblGroups=text_styles.standard(backport.text(R.strings.vehicle_customization.filter.popover.groups.title())), lblShowOnlyFilters=text_styles.standard(backport.text(R.strings.vehicle_customization.filter.popover.showonlyfilters.title())), btnDefault=backport.text(R.strings.vehicle_customization.filter.popover.getDefaultSettings()), groupType=self._groups if self._groupCount > 1 else None, btnDefaultTooltip=makeTooltip(backport.text(R.strings.vehicle_customization.customization.filterPopover.refresh.header()), backport.text(R.strings.vehicle_customization.customization.filterPopover.refresh.body())), groupTypeSelectedIndex=self._selectedGroup, filterBtns=_filterBtns, formsBtnsLbl=formsBtnsLbl, formsBtns=_formsBtns)
