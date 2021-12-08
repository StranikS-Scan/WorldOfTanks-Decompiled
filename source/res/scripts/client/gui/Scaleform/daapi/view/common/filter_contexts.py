# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/common/filter_contexts.py
from new_year.ny_constants import NY_FILTER

class FilterSetupContext(object):

    def __init__(self, ctx=None, asset=None):
        self.ctx = ctx or {}
        self.asset = asset or ''
        self.asset = self.asset.format(**self.ctx)


def getFilterSetupContexts(xpRateMultiplier):
    return {'favorite': FilterSetupContext(asset='favorite'),
     'elite': FilterSetupContext(asset='elite_small_icon'),
     'premium': FilterSetupContext(asset='prem_small_icon'),
     'igr': FilterSetupContext(asset='premium_small'),
     'bonus': FilterSetupContext(ctx={'multiplier': xpRateMultiplier}, asset='bonus_x{multiplier}'),
     'battleRoyale': FilterSetupContext(asset='battle_royale_toggle'),
     NY_FILTER: FilterSetupContext(asset='newYear_small')}


def getFilterPopoverSetupContexts(xpRateMultiplier):
    return {'favorite': FilterSetupContext(asset='favorite_medium'),
     'elite': FilterSetupContext(asset='elite_small_icon'),
     'premium': FilterSetupContext(asset='prem_small_icon'),
     'igr': FilterSetupContext(asset='premium_igr_small'),
     'bonus': FilterSetupContext(ctx={'multiplier': xpRateMultiplier}, asset='bonus_x'),
     NY_FILTER: FilterSetupContext(asset='newYear_small'),
     'rented': FilterSetupContext(asset='marathon/time_icon'),
     'event': FilterSetupContext(asset='event_small_icon'),
     'isCommonProgression': FilterSetupContext(asset='common_progression'),
     'crystals': FilterSetupContext(asset='bons_small'),
     'clanRented': FilterSetupContext(asset='clan_wars'),
     'ranked': FilterSetupContext(asset='ranked')}
