# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/mapbox/tooltips/mapbox_progression_tooltip.py
import logging
from gui.impl.gen import R
from gui.impl import backport
from gui.impl.gen_utils import INVALID_RES_ID
from gui.mapbox.mapbox_helpers import getTillTimeString, prepareProgressionData
from gui.Scaleform.genConsts.PROGRESSCOLOR_CONSTANTS import PROGRESSCOLOR_CONSTANTS
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.shared.formatters import text_styles
from gui.shared.tooltips import formatters, TOOLTIP_TYPE
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.tooltips.formatters import RENDERERS_ALIGN_CENTER
from helpers import dependency
from skeletons.gui.game_control import IMapboxController
_logger = logging.getLogger(__name__)
_IMG_PATH = R.images.gui.maps.icons.mapbox
_STR_PATH = R.strings.mapbox.questFlag
_MAPS_IN_ROW = 3
_MAX_MAPS_IN_ROW = 4
_MAP_ICON_SIZE = (54, 54)

class MapboxProgressionTooltip(BlocksTooltipData):
    __mapboxCtrl = dependency.descriptor(IMapboxController)

    def __init__(self, context):
        super(MapboxProgressionTooltip, self).__init__(context, TOOLTIP_TYPE.MAPBOX_SELECTOR_INFO)
        self._setWidth(350)
        self._setContentMargin(top=0, left=0, bottom=16, right=0)

    def _packBlocks(self, *args):
        items = []
        progressionData = self.__mapboxCtrl.getProgressionData()
        if progressionData is not None and self.__mapboxCtrl.isActive():
            items.append(self.__packHeaderBlock())
            items.append(formatters.packTextBlockData(text_styles.main(backport.text(_STR_PATH.description(), highlightedText=text_styles.stats(backport.text(_STR_PATH.highlightedText())))), padding=formatters.packPadding(left=18, right=10)))
            items.append(formatters.packBuildUpBlockData(self.__packTotalProgressionBlock(progressionData), linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE))
            items.append(self.__packMapsProgressionBlock(progressionData))
        else:
            items.append(self.__packFrozenBlock())
        return items

    def __packHeaderBlock(self):
        header = backport.text(R.strings.tooltips.battleTypes.mapbox.header())
        timeLeftStr = text_styles.stats(getTillTimeString(self.__mapboxCtrl.getEventEndTimestamp()))
        body = backport.text(R.strings.menu.headerButtons.battle.types.mapbox.extra.endsIn(), timeLeft=timeLeftStr)
        return formatters.packImageTextBlockData(title=text_styles.highTitle(header), desc=text_styles.main(body), img=backport.image(_IMG_PATH.quests.tooltip_header_bg()), txtOffset=1, txtPadding=formatters.packPadding(top=15, left=17), padding=formatters.packPadding(bottom=-10))

    def __packMapsProgressionBlock(self, progressionData):
        items = []
        mapVOs = []
        actualSeason = self.__mapboxCtrl.getCurrentSeason()
        validMaps = self.__mapboxCtrl.getModeSettings().geometryIDs[actualSeason.getSeasonID()]
        sortedProgressionData = prepareProgressionData(progressionData.surveys, validMaps)
        passedSurveys = 0
        for mapName, mapData in sortedProgressionData:
            counter = backport.text(_STR_PATH.counter(), progress=text_styles.bonusPreviewText(min(mapData.progress, mapData.total)), total=mapData.total) if not mapData.passed else ''
            iconPath = _IMG_PATH.progressionTooltip.num(mapName, _IMG_PATH.progressionTooltip.dyn(mapName))()
            mapVOs.append({'icon': backport.image(iconPath) if iconPath != INVALID_RES_ID else '',
             'count': counter,
             'isCompleted': mapData.passed})
            if mapData.passed:
                passedSurveys += 1

        if passedSurveys == len(sortedProgressionData):
            progressStyle = text_styles.bonusAppliedText
        else:
            progressStyle = text_styles.bonusPreviewText
        countStr = backport.text(_STR_PATH.counter(), progress=progressStyle(passedSurveys), total=text_styles.main(len(sortedProgressionData)))
        items.append(formatters.packTextBlockData(text_styles.stats(backport.text(_STR_PATH.surveysTitle(), count=countStr)), padding=formatters.packPadding(left=17)))
        iconBorders = 2
        columnWidth = _MAP_ICON_SIZE[0] + iconBorders
        rowHeight = _MAP_ICON_SIZE[1] + iconBorders
        horizontalGap = 10
        paddingTop = 8
        sublists = self.__getMapsSublists(mapVOs)
        for mapsList in sublists:
            items.append(formatters.packMapBoxBlockData(mapsList, columnWidth, rowHeight, padding=formatters.packPadding(top=paddingTop), horizontalGap=horizontalGap, renderersAlign=RENDERERS_ALIGN_CENTER))

        return formatters.packBuildUpBlockData(items)

    @staticmethod
    def __packTotalProgressionBlock(progressionData):
        progress = progressionData.totalBattles
        total = max(progressionData.rewards)
        items = []
        progressStyle = text_styles.bonusAppliedText if progress >= total else text_styles.bonusPreviewText
        progressionCounter = [formatters.packTextBlockData(text_styles.stats(backport.text(_STR_PATH.progressTitle())), blockWidth=250, padding=formatters.packPadding(left=18)), formatters.packAlignedTextBlockData(backport.text(_STR_PATH.counter(), progress=progressStyle(min(progress, total)), total=text_styles.main(total)), blockWidth=85, align=BLOCKS_TOOLTIP_TYPES.ALIGN_RIGHT)]
        items.append(formatters.packBuildUpBlockData(progressionCounter, layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_HORIZONTAL))
        progressColor = PROGRESSCOLOR_CONSTANTS.GREEN if progress >= total else PROGRESSCOLOR_CONSTANTS.ORANGE
        items.append(formatters.packBlockDataItem(linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_EPIC_PROGRESS_BLOCK_LINKAGE, data={'value': min(progress, total),
         'maxValue': total,
         'progressColor': progressColor}, blockWidth=330, padding=formatters.packPadding(top=-11, bottom=8, left=20)))
        if progress < total:
            items.append(formatters.packTextBlockData(text_styles.main(backport.text(_STR_PATH.incomplete(), count=text_styles.stats(min([ battles for battles in progressionData.rewards.keys() if battles > progress ]) - progress))), padding=formatters.packPadding(left=18)))
        else:
            items.append(formatters.packTextBlockData(text_styles.main(backport.text(_STR_PATH.complete())), padding=formatters.packPadding(left=18)))
        return items

    @staticmethod
    def __packFrozenBlock():
        items = [formatters.packTextBlockData(text=text_styles.middleTitle(backport.text(_STR_PATH.frozen.header()))), formatters.packTextBlockData(text=text_styles.main(backport.text(_STR_PATH.frozen.text())), blockWidth=420)]
        return formatters.packBuildUpBlockData(items, padding=formatters.packPadding(top=20, left=18))

    @staticmethod
    def __getMapsSublists(mapsVOs):
        mapsCount = len(mapsVOs)
        itemsInOneRow = _MAX_MAPS_IN_ROW if mapsCount % _MAX_MAPS_IN_ROW == 0 else _MAPS_IN_ROW
        return [ mapsVOs[rowNumber:rowNumber + itemsInOneRow] for rowNumber in range(0, mapsCount, itemsInOneRow) ]
