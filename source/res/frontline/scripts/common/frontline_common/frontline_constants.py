# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/common/frontline_common/frontline_constants.py
from __future__ import absolute_import
from future.utils import viewitems
EMPTY_SETUP_RESERVES_MODIFIER = -1

class FLBattleReservesModifier(object):
    STANDARD = 0
    FAST = 1
    RANDOM = 2


RESERVES_MODIFIER_NAMES = {v:k.lower() for k, v in viewitems(FLBattleReservesModifier.__dict__) if not k.startswith('__')}
RESERVES_MODIFIER_IDS = {v:k for k, v in viewitems(RESERVES_MODIFIER_NAMES)}
