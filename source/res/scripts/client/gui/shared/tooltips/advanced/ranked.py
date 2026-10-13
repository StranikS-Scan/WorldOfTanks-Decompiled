# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/advanced/ranked.py
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.shared.tooltips.advanced import BaseAdvancedTooltip
from gui.shared.tooltips.advanced.data.default_alt_key_data import AltKeyData

class RankedAdvanced(BaseAdvancedTooltip):

    def _getTooltipData(self, *args, **kwargs):
        return AltKeyData(swfName='gamemodeRanked', header=backport.text(R.strings.tooltips.battleTypes.ranked.header()), description=PREBATTLE_ACTION_NAME.RANKED)
