# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/epic_battle/epic_battle_tooltips.py
import logging
from helpers.i18n import makeString
from constants import PLAYER_RANK
from gui.battle_control.controllers.epic_missions_ctrl import RANK_TO_TRANSLATION
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
_logger = logging.getLogger(__name__)

class EpicRankUnlockTooltipData(BlocksTooltipData):
    _RANK_LEVEL_AVAILABLE_TOOLTIP = (2, 3)

    def __init__(self, context):
        super(EpicRankUnlockTooltipData, self).__init__(context, None)
        self._setContentMargin(top=14, left=14, bottom=14, right=14)
        self._setWidth(280)
        return

    def _packBlocks(self, *args, **kwargs):
        items = super(EpicRankUnlockTooltipData, self)._packBlocks()
        unlockRank = args[0]
        if unlockRank not in self._RANK_LEVEL_AVAILABLE_TOOLTIP or unlockRank not in PLAYER_RANK.NAMES:
            return items
        items.append(formatters.packImageTextBlockData(title=text_styles.main(backport.text(R.strings.epic_battle.tooltips.slotUnlocked.message(), rank=makeString(RANK_TO_TRANSLATION[unlockRank]))), img=backport.image(R.images.gui.maps.icons.library.epicRank.tooltip.dyn(PLAYER_RANK.NAMES[unlockRank])()), txtPadding=formatters.packPadding(top=3)))
        return items
