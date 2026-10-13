# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/advanced/tankman.py
from gui.shared.tooltips.advanced import BaseAdvancedTooltip
from gui.shared.tooltips.advanced.data.advanced_constants import TANKMAN_MOVIES
from gui.shared.tooltips.advanced.data.default_alt_key_data import AltKeyData
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES

class TankmanPreviewTooltipAdvanced(BaseAdvancedTooltip):

    def _getTooltipData(self, role, *args, **kwargs):
        return (AltKeyData(swfName=TANKMAN_MOVIES[role], header=ITEM_TYPES.tankman_roles(role), description=role),)
