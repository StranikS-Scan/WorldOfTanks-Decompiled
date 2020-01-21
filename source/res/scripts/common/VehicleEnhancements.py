# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/VehicleEnhancements.py
from items.vehicles import EnhancementItem

class VehicleEnhancements(object):

    def __init__(self, enhancements):
        self.factors = []
        for items in enhancements.itervalues():
            for enhancement in items.itervalues():
                if 'factors' in enhancement:
                    self.factors.extend([ EnhancementItem(factor['name'], factor['value'], factor['operation']) for factor in enhancement['factors'] ])

    def onCollectFactors(self, factors):
        for factor in self.factors:
            factors[factor.name] = factor.applyFactor(factors[factor.name])
