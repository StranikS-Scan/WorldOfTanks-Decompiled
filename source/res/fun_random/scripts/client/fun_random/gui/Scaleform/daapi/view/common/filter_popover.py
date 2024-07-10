# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/Scaleform/daapi/view/common/filter_popover.py
from fun_random.gui.feature.util.fun_mixins import FunAssetPacksMixin
from gui.Scaleform.daapi.view.common.filter_popover import FILTER_SECTION, BattlePassCarouselFilterPopover
from gui.impl import backport
from gui.shared.utils.functions import makeTooltip

def fillFunRandomFilterVO(vo, selected, enabled):
    vo.update({'value': backport.image(FunAssetPacksMixin.getModeIconsResRoot().library.carousel_filter()),
     'tooltip': makeTooltip(header=backport.text(FunAssetPacksMixin.getModeLocalsResRoot().tooltip.filter.header()), body=backport.text(FunAssetPacksMixin.getModeLocalsResRoot().tooltip.filter.body())),
     'selected': selected,
     'enabled': enabled})
    return vo


class FunRandomCarouselFilterPopover(BattlePassCarouselFilterPopover):

    @classmethod
    def _hasClanWarsVehicles(cls):
        return False

    @classmethod
    def _generateMapping(cls, hasRented, hasEvent, hasRoles, **kwargs):
        mapping = super(FunRandomCarouselFilterPopover, cls)._generateMapping(hasRented, hasEvent, hasRoles, **kwargs)
        mapping[FILTER_SECTION.SPECIALS].append('funRandom')
        return mapping

    def _packSpecial(self, entry, ctx, selected, tooltipRes, enabled):
        return super(FunRandomCarouselFilterPopover, self)._packSpecial(entry, ctx, selected, tooltipRes, enabled) if entry != 'funRandom' else fillFunRandomFilterVO({}, selected, enabled)
