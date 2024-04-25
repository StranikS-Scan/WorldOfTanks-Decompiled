# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/lobby/tooltips/respawn_tooltip.py
from helpers.time_utils import ONE_MINUTE
from battle_royale.gui.Scaleform.daapi.view.common.respawn_ability import RespawnAbility
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.tooltips import TOOLTIP_TYPE
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
_TOOLTIP_WIDTH = 420

class RespawnTooltipData(BlocksTooltipData):

    def __init__(self, context=None):
        super(RespawnTooltipData, self).__init__(context, TOOLTIP_TYPE.MODULE)
        self._setContentMargin(top=0, left=0, bottom=20, right=20)
        self._setMargins(10, 15)
        self._setWidth(_TOOLTIP_WIDTH)

    def _packBlocks(self, *args, **kwargs):
        items = super(RespawnTooltipData, self)._packBlocks()
        leftPadding = 20
        rightPadding = 10
        topPadding = 20
        verticalPadding = 2
        innerBlockLeftPadding = 100
        headerBlockItem = [formatters.packBuildUpBlockData(self.__constructHeaderBlock(leftPadding, innerBlockLeftPadding), padding=formatters.packPadding(left=leftPadding, right=rightPadding, top=topPadding, bottom=verticalPadding))]
        items.append(formatters.packBuildUpBlockData(headerBlockItem))
        items.append(formatters.packBuildUpBlockData(self.__constructDescriptionBlock(leftPadding), linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding=formatters.packPadding(left=0, right=rightPadding, top=verticalPadding, bottom=verticalPadding)))
        items.append(formatters.packTextBlockData(text=text_styles.standard(backport.text(R.strings.battle_royale.tooltips.respawnIcon.definition())), padding=formatters.packPadding(left=leftPadding, top=verticalPadding - 4)))
        return items

    @staticmethod
    def __constructHeaderBlock(leftPadding, innerBlockLeftPadding):
        return [formatters.packImageTextBlockData(title=text_styles.highTitle(backport.text(R.strings.battle_royale.tooltips.respawnIcon.title())), desc=text_styles.main(backport.text(R.strings.tooltips.battle_royale.artefact.limit())), img=backport.image(RespawnAbility.icon), imgPadding=formatters.packPadding(left=7), txtGap=-4, txtOffset=innerBlockLeftPadding - leftPadding)]

    @staticmethod
    def __constructDescriptionBlock(leftPadding):
        respawnAvailabilityDurationSoloStr = text_styles.neutral(backport.text(R.strings.battle_royale.tooltips.respawnIcon.min(), duration=RespawnAbility().soloRespawnPeriod / ONE_MINUTE))
        respawnAvailabilityDurationPlatoonStr = text_styles.neutral(backport.text(R.strings.battle_royale.tooltips.respawnIcon.min(), duration=RespawnAbility().platoonRespawnPeriod / ONE_MINUTE))
        notInBattleDurationStr = text_styles.neutral(backport.text(R.strings.battle_royale.tooltips.respawnIcon.sec(), duration=RespawnAbility().platoonTimeToRessurect))
        return [formatters.packTextBlockData(text=text_styles.main(backport.text(R.strings.battle_royale.tooltips.respawnIcon.description())), padding=formatters.packPadding(top=-5, left=leftPadding)), formatters.packTitleDescBlock(title=text_styles.middleTitle(backport.text(R.strings.battle_royale.tooltips.respawnIcon.solo.subtitle())), desc=text_styles.main(backport.text(R.strings.battle_royale.tooltips.respawnIcon.solo.description(), duration=respawnAvailabilityDurationSoloStr)), padding=formatters.packPadding(top=10, left=leftPadding), descPadding=formatters.packPadding(bottom=-10)), formatters.packTitleDescBlock(title=text_styles.middleTitle(backport.text(R.strings.battle_royale.tooltips.respawnIcon.platoon.subtitle())), desc=text_styles.main(backport.text(R.strings.battle_royale.tooltips.respawnIcon.platoon.description(), duration=respawnAvailabilityDurationPlatoonStr, timeToResurrect=notInBattleDurationStr)), padding=formatters.packPadding(top=10, left=leftPadding), descPadding=formatters.packPadding(bottom=-17))]
