# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/entities/vehicle_models/client_shot_params.py
from __future__ import absolute_import
import typing
from helpers_common import reprSlots

class ShotParams(object):
    __slots__ = ('sourceID', 'gunIndexDelayed', 'shellKindIdx', 'predictShooting')

    def __init__(self, sourceID, gunIndexDelayed, shellKindIdx, predictShooting):
        self.sourceID = sourceID
        self.gunIndexDelayed = gunIndexDelayed
        self.shellKindIdx = shellKindIdx
        self.predictShooting = predictShooting

    __repr__ = reprSlots
