# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/comp7/filter_popover.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import COMP7_PREBATTLE_CAROUSEL_ROW_VALUE
from gui.Scaleform.daapi.view.battle.comp7.common import getSavedRowCountValue, rowValueToRowCount, rowCountToRowValue
from gui.Scaleform.daapi.view.common.filter_popover import TankCarouselFilterPopover, FILTER_SECTION
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles

class Comp7TankCarouselFilterPopover(TankCarouselFilterPopover):

    def switchCarouselType(self, selected):
        self._carouselRowCount = 1 if selected else 0
        self.__saveRowCountValue()
        self._carousel.setRowCount(rowValueToRowCount(self._carouselRowCount))

    def _readRowCount(self, ctx):
        savedRowValue, isSavedByPlayer = getSavedRowCountValue()
        if isSavedByPlayer:
            self._carouselRowCount = savedRowValue
        elif ctx and 'data' in ctx:
            data = ctx['data']
            self._carouselRowCount = rowCountToRowValue(getattr(data, 'rowCount', 1))

    def _saveRowCount(self):
        savedRowValue, isSavedByPlayer = getSavedRowCountValue()
        if isSavedByPlayer and savedRowValue != self._carouselRowCount:
            self.__saveRowCountValue()

    def _getInitialVO(self, filters, xpRateMultiplier):
        dataVO = super(Comp7TankCarouselFilterPopover, self)._getInitialVO(filters, xpRateMultiplier)
        dataVO['specialSectionVisible'] = True
        dataVO['searchSectionVisible'] = True
        dataVO['progressionsSectionVisible'] = False
        dataVO['additionalInfo'] = text_styles.stats(backport.text(R.strings.comp7.battleCarousel.filterPopover.desc()))
        vehicleLevels = self._carousel.getCustomParams().get('vehicleLevelsFilter', list())
        if self._carousel is not None and not len(vehicleLevels) > 1:
            dataVO['tankTierSectionVisible'] = False
        return dataVO

    def _generateMapping(self, hasRented, hasEvent, hasRoles, **kwargs):
        mapping = super(Comp7TankCarouselFilterPopover, self)._generateMapping(hasRented, hasEvent, hasRoles, **kwargs)
        mapping[FILTER_SECTION.SPECIALS] = ['rented', 'favorite']
        vehicleLevels = kwargs.get('vehicleLevelsFilter', list())
        if len(vehicleLevels) > 1:
            mapping[FILTER_SECTION.LEVELS] = [ 'level_{}'.format(lvl) for lvl in vehicleLevels ]
        else:
            mapping[FILTER_SECTION.LEVELS] = []
        return mapping

    def __saveRowCountValue(self):
        AccountSettings.setSettings(COMP7_PREBATTLE_CAROUSEL_ROW_VALUE, self._carouselRowCount)
