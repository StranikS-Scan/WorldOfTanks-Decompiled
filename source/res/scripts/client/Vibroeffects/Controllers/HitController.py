# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/Vibroeffects/Controllers/HitController.py
# Compiled at: 2011-04-14 19:54:36
import BigWorld
import Math
from constants import SHOT_RESULT
from debug_utils import *
from OnceController import OnceController
import math

class HitController:

    def __init__(self, shotResult):
        if shotResult in (SHOT_RESULT.ARMOR_NOT_PIERCED, SHOT_RESULT.ARMOR_PIERCED_NO_DAMAGE):
            OnceController('hit_nonpenetration_veff')
            return
        if shotResult == SHOT_RESULT.RICOCHET:
            OnceController('hit_ricochet_veff')
            return
        if shotResult == SHOT_RESULT.MAX_HIT + 1:
            OnceController('hit_splash_veff')
            return
        OnceController('hit_veff')
