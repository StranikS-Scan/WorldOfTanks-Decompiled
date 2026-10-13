# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattle/tooltips/recertification_tooltip.py
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.tooltips import TOOLTIP_COMPONENT, formatters
from gui.shared.tooltips.advanced import BaseAdvancedTooltip
from gui.shared.tooltips.contexts import ToolTipContext
from gui.shared.tooltips.demount_kits import DemountKitToolTipData
from helpers import dependency
from skeletons.gui.goodies import IGoodiesCache
from gui.shared.tooltips.advanced.data.default_alt_key_data import AltKeyData

class EpicBattleBlanksContext(ToolTipContext):
    goodiesCache = dependency.descriptor(IGoodiesCache)

    def __init__(self, fieldsToExclude=None):
        super(EpicBattleBlanksContext, self).__init__(TOOLTIP_COMPONENT.RECERTIFICATION_FORM, fieldsToExclude)

    def buildItem(self, recertificationFormID):
        return self.goodiesCache.getGoodie(recertificationFormID)


class EpicBattleRecertificationFormTooltipAdvanced(BaseAdvancedTooltip):

    def _getTooltipData(self, *args, **kwargs):
        recertificationForm = self.context.buildItem(*args, **kwargs)
        return (AltKeyData(swfName='resetPerksBook', description=backport.text(R.strings.tooltips.advanced.recertificationForm.description()), header=recertificationForm.userName),)


class EpicBattleRecertificationFormTooltip(DemountKitToolTipData):
    _WIDTH = 400

    def __init__(self, context):
        super(EpicBattleRecertificationFormTooltip, self).__init__(context)
        self._setContentMargin(top=15, left=18, bottom=21, right=0)

    def _packDescription(self):
        return formatters.packTitleDescBlock(title=text_styles.middleTitle(backport.text(R.strings.tooltips.equipment.effect())), desc=text_styles.main(backport.text(R.strings.recertification_form.base.recertificationForm.description())), blocksLinkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)
