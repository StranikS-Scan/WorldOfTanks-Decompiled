# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/emission_params.py
from collections import namedtuple
EmissionParams = namedtuple('EmissionParams', ('emissionTexture', 'emissionDeferredPower', 'emissionForwardPower'))
EmissionParams.__new__.__defaults__ = ('', 1.0, 1.0)

def getEmissionParams(item):
    return EmissionParams(emissionTexture=item.emissionParams.emissionTexture, emissionDeferredPower=item.emissionParams.emissionDeferredPower, emissionForwardPower=item.emissionParams.emissionForwardPower) if item is not None and item.emissionParams is not None and item.emissionParams.emissionTexture else None
