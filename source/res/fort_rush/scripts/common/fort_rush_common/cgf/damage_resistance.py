# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/common/fort_rush_common/cgf/damage_resistance.py
from __future__ import absolute_import
import CGF
from cgf_script.registration import ComponentProperty
from constants import ATTACK_REASON
UNRESISTED_ATTACK_REASON_IDS = frozenset((ATTACK_REASON.getIndex(ATTACK_REASON.WORLD_COLLISION), ATTACK_REASON.getIndex(ATTACK_REASON.DROWNING)))

class FortRushDamageResistanceComponentDescr(object):
    domain = CGF.Domain.All
    resistance = ComponentProperty(type=CGF.PropertyType.Float, editorName='resistance', value=0.0)
