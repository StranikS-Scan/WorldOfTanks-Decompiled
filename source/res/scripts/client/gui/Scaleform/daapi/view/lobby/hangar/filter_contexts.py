# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/filter_contexts.py


class FilterSetupContext(object):
    """ Class responsible for configuration of filter creation.
    
    Some filters require specifically named asset or some additional runtime information,
    this class provides this kind of stuff.
    """

    def __init__(self, ctx=None, asset=None):
        """
        :param ctx: context with runtime information required by filter
        :param asset: name of the asset (icon) for filter
        """
        self.ctx = ctx or {}
        self.asset = asset or ''
        self.asset = self.asset.format(**self.ctx)


def getFilterSetupContexts(xpRateMultiplier):
    """ Generate contexts for the filters that require special info.
    
    :return: dict {filter_name: FilterSetupContext}
    """
    return {'favorite': FilterSetupContext(asset='favorite'),
     'elite': FilterSetupContext(asset='elite_small_icon'),
     'premium': FilterSetupContext(asset='prem_small_icon'),
     'igr': FilterSetupContext(asset='premium_small'),
     'bonus': FilterSetupContext(ctx={'multiplier': xpRateMultiplier}, asset='bonus_x{multiplier}')}


def getFilterPopoverSetupContexts(xpRateMultiplier):
    """ Generate contexts for the filters popover that require special info.
    
    :return: dict {filter_name: FilterSetupContext}
    """
    return {'favorite': FilterSetupContext(asset='favorite_medium'),
     'elite': FilterSetupContext(asset='elite_small_icon'),
     'premium': FilterSetupContext(asset='prem_small_icon'),
     'igr': FilterSetupContext(asset='premium_igr_small'),
     'bonus': FilterSetupContext(ctx={'multiplier': xpRateMultiplier}, asset='bonus_x')}
