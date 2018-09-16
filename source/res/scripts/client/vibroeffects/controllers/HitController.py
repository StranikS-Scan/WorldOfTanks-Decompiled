# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/Vibroeffects/Controllers/HitController.py
from constants import VEHICLE_HIT_EFFECT as HIT_EFFECT
from OnceController import OnceController

class HitController(object):

    def __init__(self, hitEffectCode):
        if hitEffectCode in (HIT_EFFECT.ARMOR_NOT_PIERCED, HIT_EFFECT.ARMOR_PIERCED_NO_DAMAGE):
            OnceController('hit_nonpenetration_veff')
            return
        if hitEffectCode in HIT_EFFECT.RICOCHETS:
            OnceController('hit_ricochet_veff')
            return
        if hitEffectCode == HIT_EFFECT.MAX_CODE + 1:
            OnceController('hit_splash_veff')
            return
        OnceController('hit_veff')
