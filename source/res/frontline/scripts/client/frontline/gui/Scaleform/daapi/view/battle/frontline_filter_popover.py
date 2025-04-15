# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/Scaleform/daapi/view/battle/frontline_filter_popover.py
from gui.Scaleform.daapi.view.common.common_constants import FILTER_POPOVER_SECTION
from gui.Scaleform.daapi.view.common.filter_popover import TankCarouselFilterPopover
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_filter import FILTER_KEYS

class FrontlineBattleTankCarouselFilterPopover(TankCarouselFilterPopover):
    _BASE_SPECIALS_LIST = [FILTER_KEYS.FAVORITE, FILTER_KEYS.PREMIUM]

    def _getInitialVO(self, filters, xpRateMultiplier):
        dataVO = super(FrontlineBattleTankCarouselFilterPopover, self)._getInitialVO(filters, xpRateMultiplier)
        dataVO['specialSectionVisible'] = True
        dataVO['searchSectionVisible'] = True
        dataVO['progressionsSectionVisible'] = False
        vehicleLevels = self._carousel.getCustomParams().get('vehicleLevelsFilter', list())
        if self._carousel is not None and not len(vehicleLevels) > 1:
            dataVO['tankTierSectionVisible'] = False
        return dataVO

    def _generateMapping(self, hasRented, hasEvent, hasRoles, hasCustomization, **kwargs):
        mapping = super(FrontlineBattleTankCarouselFilterPopover, self)._generateMapping(hasRented, hasEvent, hasRoles, hasCustomization, **kwargs)
        vehicleLevels = kwargs.get('vehicleLevelsFilter', list())
        if len(vehicleLevels) > 1:
            mapping[FILTER_POPOVER_SECTION.LEVELS] = [ 'level_{}'.format(lvl) for lvl in vehicleLevels ]
        else:
            mapping[FILTER_POPOVER_SECTION.LEVELS] = []
        return mapping
