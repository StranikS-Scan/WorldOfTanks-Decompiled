# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/lobby/tooltips/hangar_vehicle_info.py
import CommandMapping
from gui.Scaleform.daapi.view.common.battle_royale.br_helpers import getHotKeyString
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.tooltips import formatters, TOOLTIP_TYPE
from gui.shared.tooltips.common import BlocksTooltipData

class BattleProgressionTooltipData(BlocksTooltipData):

    def __init__(self, context=None):
        super(BattleProgressionTooltipData, self).__init__(context, TOOLTIP_TYPE.CONTROL)
        self._setWidth(390)
        self._setMargins(afterBlock=10, afterSeparator=15)
        self._setContentMargin(top=10, left=20, bottom=15, right=15)

    def _packBlocks(self, *args, **kwargs):
        items = super(BattleProgressionTooltipData, self)._packBlocks(*args, **kwargs)
        titleStr = text_styles.highTitle(backport.text(R.strings.battle_royale.hangarVehicleInfo.tooltips.battleProgression.title()))
        titleDescrStr = text_styles.neutral(backport.text(R.strings.battle_royale.hangarVehicleInfo.tooltips.battleProgression.titleDescr()))
        items.append(formatters.packItemTitleDescBlockData(title=titleStr, desc=titleDescrStr, txtGap=5))
        highlight1Str = text_styles.neutral(backport.text(R.strings.battle_royale.hangarVehicleInfo.tooltips.battleProgression.noteHighlight1()))
        highlight2Str = text_styles.neutral(backport.text(R.strings.battle_royale.hangarVehicleInfo.tooltips.battleProgression.noteHighlight2()))
        noteStr = text_styles.main(backport.text(R.strings.battle_royale.hangarVehicleInfo.tooltips.battleProgression.note(), highlight1=highlight1Str, highlight2=highlight2Str))
        noteBlock = formatters.packTextBlockData(text=noteStr)
        items.append(formatters.packBuildUpBlockData(blocks=[noteBlock], linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE))
        tutorialHighlightStr = text_styles.neutral(backport.text(R.strings.battle_royale.hangarVehicleInfo.tooltips.battleProgression.tutorialHighlight()))
        treeKey = text_styles.alert(getHotKeyString(CommandMapping.CMD_UPGRADE_PANEL_SHOW))
        leftModuleKey = text_styles.alert(getHotKeyString(CommandMapping.CMD_CM_VEHICLE_UPGRADE_PANEL_LEFT))
        rightModuleKey = text_styles.alert(getHotKeyString(CommandMapping.CMD_CM_VEHICLE_UPGRADE_PANEL_RIGHT))
        tutorialStr = text_styles.main(backport.text(R.strings.battle_royale.hangarVehicleInfo.tooltips.battleProgression.tutorial(), treeKey=treeKey, leftModuleKey=leftModuleKey, rightModuleKey=rightModuleKey))
        tutorialStr = text_styles.concatStylesWithSpace(tutorialHighlightStr, tutorialStr)
        items.append(formatters.packTextBlockData(text=tutorialStr))
        return items
