# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/battle_pass_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts, battle_pass
from gui.shared.tooltips.builders import DataBuilder
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.DEVICE_GIFT_TOKEN, TOOLTIPS_CONSTANTS.DEVICE_GIFT_TOKEN_UI, battle_pass.DeviceGiftTokenTooltipData(contexts.DeviceGiftTokenContext())), DataBuilder(TOOLTIPS_CONSTANTS.BATTLE_PASS_POINTS, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, battle_pass.BattlePassPointsTooltipData(contexts.ToolTipContext(None))))
