# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/VehicleEnhancements.py
from __future__ import absolute_import
from future.utils import viewvalues
from items.vehicles import EnhancementItem

class VehicleEnhancements(object):

    def __init__(self, enhancements):
        self.factors = []
        for items in viewvalues(enhancements):
            for enhancement in viewvalues(items):
                if 'factors' in enhancement:
                    self.factors.extend([ EnhancementItem(factor['name'], factor['value'], factor['operation']) for factor in enhancement['factors'] ])

    def onCollectFactors(self, factors):
        for factor in self.factors:
            factors[factor.name] = factor.applyFactor(factors[factor.name])
