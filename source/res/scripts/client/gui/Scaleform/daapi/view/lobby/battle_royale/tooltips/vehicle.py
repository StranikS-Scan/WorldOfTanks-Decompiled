# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/battle_royale/tooltips/vehicle.py
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.tooltips import formatters
from gui.shared.tooltips import TOOLTIP_TYPE
from gui.shared.tooltips.vehicle import StatusBlockConstructor
from gui.shared.tooltips.common import BlocksTooltipData
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController
_TOOLTIP_WIDTH = 420

class VehicleTooltipData(BlocksTooltipData):
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)

    def __init__(self, context=None):
        super(VehicleTooltipData, self).__init__(context, TOOLTIP_TYPE.VEHICLE)
        self._setContentMargin(top=20, left=30, bottom=20, right=30)
        self._setMargins(afterBlock=10, afterSeparator=15)
        self._setWidth(400)

    def _packBlocks(self, *args, **kwargs):
        vehicle = self.context.buildItem(*args, **kwargs)
        if vehicle is None:
            return
        else:
            items = super(VehicleTooltipData, self)._packBlocks(*args, **kwargs)
            items.append(self.__setBackground(vehicle))
            items.append(formatters.packBuildUpBlockData(blocks=self.__constructHeaderBlock(vehicle)))
            items.append(formatters.packBuildUpBlockData(blocks=self.__constructDescriptionBlock(vehicle)))
            statusBlock = self.__constructStatusBlock(vehicle)
            if statusBlock is not None:
                items.append(statusBlock)
            return items

    def __constructStatusBlock(self, vehicle):
        statusConfig = self.context.getStatusConfiguration(vehicle)
        statusBlock, operationError = StatusBlockConstructor(vehicle, statusConfig).construct()
        return formatters.packBuildUpBlockData(statusBlock) if statusBlock and not operationError else None

    @classmethod
    def __constructHeaderBlock(cls, vehicle):
        headerBlock = []
        titleStr = text_styles.highTitle(vehicle.shortUserName)
        titleDescrStr = text_styles.main(backport.text(R.strings.tooltips.battle_royale.hangar.vehicle.status()))
        headerBlock.append(formatters.packItemTitleDescBlockData(title=titleStr, desc=titleDescrStr, descPadding=formatters.packPadding(top=15)))
        return headerBlock

    @staticmethod
    def __constructDescriptionBlock(vehicle):
        return [formatters.packTextBlockData(text=text_styles.standard(backport.text(R.strings.tooltips.battle_royale.hangar.vehicle.description.dyn(vehicle.nationName)())))]

    @staticmethod
    def __setBackground(vehicle):
        return formatters.packImageBlockData(img=RES_ICONS.getTooltipFlag(vehicle.nationName), align=BLOCKS_TOOLTIP_TYPES.ALIGN_LEFT, padding=formatters.packPadding(top=-20, left=-30, bottom=-100))
