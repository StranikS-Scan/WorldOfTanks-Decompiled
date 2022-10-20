# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/Scaleform/daapi/view/tooltips/halloween_lobby_builders.py
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts, TOOLTIP_TYPE
from gui.shared.tooltips.builders import DataBuilder
from gui.shared.utils import getPlayerName
from halloween.hw_constants import HWTooltips
from gui.impl.gen import R
from gui.impl import backport
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.tooltips import formatters
from gui.shared.formatters import text_styles
from helpers import dependency
from skeletons.gui.shared import IItemsCache
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(HWTooltips.HW_BADGE, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, BadgeTooltipData(contexts.ToolTipContext(None))),)


class BadgeTooltipData(BlocksTooltipData):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, context):
        super(BadgeTooltipData, self).__init__(context, TOOLTIP_TYPE.PRIVATE_QUESTS)
        self._setContentMargin(top=20, left=20, bottom=20, right=20)
        self._setMargins(afterBlock=16)
        self._setWidth(364)

    def _packBlocks(self, badgeID):
        badge = self.__itemsCache.items.getBadges()[badgeID]
        blocks = [formatters.packTextBlockData(text_styles.highTitle(badge.getUserName()), padding=formatters.packPadding(bottom=10))]
        imgBlock = self.__getImageBlock(badgeID)
        if imgBlock is not None:
            blocks.append(imgBlock)
        if g_currentVehicle.isPresent():
            vehicle = g_currentVehicle.item
            badgeIcon = backport.image(R.images.gui.maps.icons.library.badges.c_24x24.dyn('badge_{}'.format(badgeID))())
            blocks.append(formatters.packBadgeInfoBlockData(badgeIcon, vehicle.iconContour, text_styles.bonusPreviewText(getPlayerName()), text_styles.bonusPreviewText(vehicle.shortUserName), padding=formatters.packPadding(bottom=25, top=0 if imgBlock is not None else 15)))
        blocks.append(formatters.packTextBlockData(text_styles.main(backport.text(R.strings.badge.dyn('badge_{}_descr'.format(badgeID))()))))
        return [formatters.packBuildUpBlockData(blocks)]

    @staticmethod
    def __getImageBlock(badgeID):
        badgeIcon = backport.image(R.images.gui.maps.icons.library.badges.c_220x220.dyn('badge_{}'.format(badgeID))())
        return formatters.packImageBlockData(badgeIcon, BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(top=-5, bottom=11)) if badgeIcon else None
