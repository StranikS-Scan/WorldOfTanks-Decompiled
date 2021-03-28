# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/bootcamp.py
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.tooltips import formatters
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.locale.BOOTCAMP import BOOTCAMP
from helpers import dependency
from skeletons.gui.game_control import IBootcampController

class BootcampStatuses(object):
    WAIT = 'wait'
    RECEIVED = 'received'
    COMPLETED = 'completed'
    IN_PROGRESS = 'in_progress'


class StatsTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(StatsTooltipData, self).__init__(context, None)
        self._setWidth(330)
        return

    def _packBlocks(self, label, description, icon):
        items = super(StatsTooltipData, self)._packBlocks()
        items.append(formatters.packBuildUpBlockData([formatters.packTextBlockData(text_styles.highTitle(label)), formatters.packImageBlockData(img=icon, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER), formatters.packTextBlockData(text_styles.main(description))]))
        return items


class ProgressBarBlocks(object):
    bootcampController = dependency.descriptor(IBootcampController)

    @staticmethod
    def getStatuBlock(status, lesson=None):
        if status in [BootcampStatuses.RECEIVED, BootcampStatuses.COMPLETED]:
            if status == BootcampStatuses.RECEIVED:
                text = BOOTCAMP.TOOLTIP_PROGRESSION_STATUS_GOT
                img = R.images.gui.maps.icons.library.check()
            else:
                text = BOOTCAMP.TOOLTIP_PROGRESSION_STATUS_COMPLETED
                img = R.images.gui.maps.icons.buttons.checkmark()
            title = text_styles.bonusAppliedText(text)
        else:
            if status == BootcampStatuses.WAIT:
                text = backport.text(R.strings.bootcamp.tooltip.progression.status.wait() if ProgressBarBlocks.bootcampController.needAwarding() else R.strings.bootcamp.tooltip.progression.status.wait.bc_completed(), lesson=lesson)
                img = R.images.gui.maps.icons.library.info_yellow()
            else:
                text = BOOTCAMP.TOOLTIP_PROGRESSION_STATUS_IN_PROGRESS
                img = R.images.gui.maps.icons.missions.icons.icon_flag()
            title = text_styles.neutral(text)
        if status in [BootcampStatuses.RECEIVED, BootcampStatuses.WAIT]:
            bottom = -10
            top = -1
        else:
            bottom = -20
            top = 2
        return formatters.packImageTextBlockData(title=title, img=backport.image(img), imgPadding=formatters.packPadding(left=-4, top=top), txtOffset=20, padding=formatters.packPadding(top=15, bottom=bottom))


class ProgressRewardTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(ProgressRewardTooltipData, self).__init__(context, None)
        self._setWidth(330)
        return

    def _packBlocks(self, label, description, icon, status=None, lesson=None, imgLeftPadding=50):
        items = super(ProgressRewardTooltipData, self)._packBlocks()
        blocks = [formatters.packTextBlockData(text_styles.highTitle(label)), formatters.packImageTextBlockData(img=icon, imgPadding=formatters.packPadding(left=imgLeftPadding)), formatters.packTextBlockData(text_styles.main(description))]
        if status:
            blocks.append(ProgressBarBlocks.getStatuBlock(status, lesson))
        items.append(formatters.packBuildUpBlockData(blocks))
        return items


class ProgressLessonTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(ProgressLessonTooltipData, self).__init__(context, None)
        self._setWidth(220)
        return

    def _packBlocks(self, label, description, status=None):
        items = super(ProgressLessonTooltipData, self)._packBlocks()
        blocks = [formatters.packTextBlockData(text_styles.highTitle(label)), formatters.packTextBlockData(text_styles.main(description))]
        if status:
            blocks.append(ProgressBarBlocks.getStatuBlock(status))
        items.append(formatters.packBuildUpBlockData(blocks))
        return items
