# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/veh_cmp.py
from gui.Scaleform.daapi.view.lobby.vehicle_compare import cmp_helpers
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.shared.formatters import text_styles
from gui.shared.tooltips import TOOLTIP_TYPE, formatters
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from gui.impl import backport
from gui.impl.gen import R

class VehCmpCustomizationTooltip(BlocksTooltipData):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, context):
        super(VehCmpCustomizationTooltip, self).__init__(context, TOOLTIP_TYPE.VEH_CMP_CUSTOMIZATION)
        self._setContentMargin(top=20, left=20, bottom=20, right=20)
        self._setWidth(420)
        self.__vehicle = None
        self.__camo = None
        self._customCamo = False
        return

    def _packBlocks(self, *args):
        self._customCamo = args[0]
        self.__vehicle = cmp_helpers.getCmpConfiguratorMainView().getCurrentVehicle()
        self.__camo = cmp_helpers.getSuitableCamouflage(self.__vehicle)
        camouflage = self.__vehicle.getBonusCamo()
        if camouflage is not None and not self.__camo:
            self.__camo = self.itemsCache.items.getItemByCD(camouflage.compactDescr)
            self._customCamo = False
        items = [self.__packTitleBlock(), self.__packBonusBlock(), self.__packBottomPanelBlock()]
        return items

    def __packTitleBlock(self):
        blocks = [formatters.packTextBlockData(text=text_styles.highTitle(backport.text(R.strings.veh_compare.vehConf.tooltips.camoTitle())), padding=formatters.packPadding(top=-3, left=-2)), formatters.packImageBlockData(img=self.__camo.bonus.iconBig, padding=formatters.packPadding(top=-6, left=90))]
        return formatters.packBuildUpBlockData(blocks)

    def __packBonusBlock(self):
        blocks = [formatters.packTextParameterBlockData(name=self.__camo.bonus.description, value=text_styles.bonusAppliedText('+{}'.format(self.__camo.bonus.getFormattedValue(self.__vehicle))), valueWidth=53, gap=18, padding=formatters.packPadding(top=-5, bottom=-7))]
        return formatters.packBuildUpBlockData(blocks, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)

    def __packBottomPanelBlock(self):
        title = R.strings.veh_compare.vehConf.tooltips
        if self._customCamo:
            title = title.camoInfo
        else:
            title = title.defCamoInfo
        return formatters.packTextBlockData(text=text_styles.standard(backport.text(title())), padding=formatters.packPadding(top=-6, left=-2, bottom=-6))
