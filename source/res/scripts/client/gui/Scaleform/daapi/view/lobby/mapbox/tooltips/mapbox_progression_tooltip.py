# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/mapbox/tooltips/mapbox_progression_tooltip.py
import string
from gui.impl.gen import R
from gui.impl import backport
from gui.Scaleform.daapi.view.lobby.mapbox import mapbox_helpers
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.shared.tooltips import formatters, TOOLTIP_TYPE
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency
from skeletons.gui.game_control import IMapboxController
from gui.shared.formatters import text_styles

class MapboxProgressionTooltip(BlocksTooltipData):
    __mapboxCtrl = dependency.descriptor(IMapboxController)

    def __init__(self, context):
        super(MapboxProgressionTooltip, self).__init__(context, TOOLTIP_TYPE.MAPBOX_SELECTOR_INFO)
        self._setWidth(350)
        self._setContentMargin(top=0, left=0, bottom=16, right=0)

    def _packBlocks(self, *args):
        items = []
        progressionData = self.__mapboxCtrl.getProgressionData()
        if progressionData is not None and self.__mapboxCtrl.isActive() and self.__mapboxCtrl.isInPrimeTime():
            items.append(self.__packHeaderBlock())
            items.append(formatters.packTextBlockData(text_styles.main(backport.text(R.strings.mapbox.questFlag.description(), highlightedText=text_styles.stats(backport.text(R.strings.mapbox.questFlag.highlightedText())))), padding=formatters.packPadding(left=18, right=10)))
            items.append(formatters.packBuildUpBlockData(self.__packTotalProgressionBlock(progressionData), linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE))
            items.append(self.__packMapsProgressionBlock(progressionData))
        else:
            items.append(self.__packFrozenBlock())
        return items

    def __packMapsProgressionBlock(self, progressionData):
        items = []
        iconsPath = R.images.gui.maps.icons.mapbox.progressionTooltip
        seasonNumber = self.__mapboxCtrl.getCurrentSeason().getNumber()
        nameMapping = {'all': 'all_{}'.format(seasonNumber)}
        mapVOs = []
        sortedProgressionData = sorted(progressionData.surveys.items(), key=lambda item: (item[0].startswith(tuple(string.digits)), item[0]))
        passedSurveys = 0
        for mapName, mapData in sortedProgressionData:
            counter = backport.text(R.strings.mapbox.questFlag.counter(), progress=text_styles.bonusPreviewText(min(mapData.progress, mapData.total)), total=mapData.total) if not mapData.passed else ''
            mapVOs.append({'icon': backport.image(iconsPath.dyn(self.__formatMapName(nameMapping.get(mapName, mapName)))()),
             'count': counter,
             'isCompleted': mapData.passed})
            if mapData.passed:
                passedSurveys += 1

        if passedSurveys == len(sortedProgressionData):
            progressStyle = text_styles.bonusAppliedText
        else:
            progressStyle = text_styles.bonusPreviewText
        countStr = backport.text(R.strings.mapbox.questFlag.counter(), progress=progressStyle(passedSurveys), total=text_styles.main(len(sortedProgressionData)))
        items.append(formatters.packTextBlockData(text_styles.stats(backport.text(R.strings.mapbox.questFlag.surveysTitle(), count=countStr)), padding=formatters.packPadding(left=17)))
        items.append(formatters.packMapBoxBlockData(mapVOs, 60, 60, padding=formatters.packPadding(left=42, top=8), horizontalGap=10))
        return formatters.packBuildUpBlockData(items)

    def __formatMapName(self, mapName):
        return 'c_' + mapName if mapName.startswith(tuple(string.digits)) else mapName

    def __packTotalProgressionBlock(self, progressionData):
        progress = progressionData.totalBattles
        total = max(progressionData.rewards)
        items = []
        progressStyle = text_styles.bonusAppliedText if progress >= total else text_styles.bonusPreviewText
        progressionCounter = []
        progressionCounter.append(formatters.packTextBlockData(text_styles.stats(backport.text(R.strings.mapbox.questFlag.progressTitle())), blockWidth=250, padding=formatters.packPadding(left=18)))
        progressionCounter.append(formatters.packAlignedTextBlockData(backport.text(R.strings.mapbox.questFlag.counter(), progress=progressStyle(min(progress, total)), total=text_styles.main(total)), blockWidth=85, align=BLOCKS_TOOLTIP_TYPES.ALIGN_RIGHT))
        items.append(formatters.packBuildUpBlockData(progressionCounter, layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_HORIZONTAL))
        items.append(formatters.packBlockDataItem(linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_EPIC_PROGRESS_BLOCK_LINKAGE, data={'value': min(progress, total),
         'maxValue': total,
         'isGreen': progress >= total}, blockWidth=330, padding=formatters.packPadding(top=-11, bottom=8, left=20)))
        if progress < total:
            items.append(formatters.packTextBlockData(text_styles.main(backport.text(R.strings.mapbox.questFlag.incomplete(), count=text_styles.stats(min([ battles for battles in progressionData.rewards.keys() if battles > progress ]) - progress))), padding=formatters.packPadding(left=18)))
        else:
            items.append(formatters.packTextBlockData(text_styles.main(backport.text(R.strings.mapbox.questFlag.complete())), padding=formatters.packPadding(left=18)))
        return items

    def __packHeaderBlock(self):
        seasonNumber = self.__mapboxCtrl.getCurrentSeason().getNumber()
        header = backport.text(R.strings.tooltips.battleTypes.mapbox.header())
        timeLeftStr = text_styles.stats(mapbox_helpers.getTillTimeString(self.__mapboxCtrl.getEventEndTimestamp()))
        body = backport.text(R.strings.menu.headerButtons.battle.types.mapbox.extra.endsIn(), timeLeft=timeLeftStr)
        return formatters.packImageTextBlockData(title=text_styles.highTitle(header), desc=text_styles.main(body), img=backport.image(R.images.gui.maps.icons.mapbox.quests.dyn('tooltip_header_bg_{}'.format(seasonNumber))()), txtOffset=1, txtPadding=formatters.packPadding(top=15, left=17), padding=formatters.packPadding(bottom=-10))

    def __packFrozenBlock(self):
        items = []
        items.append(formatters.packTextBlockData(text=text_styles.middleTitle(backport.text(R.strings.mapbox.questFlag.frozen.header()))))
        items.append(formatters.packTextBlockData(text=text_styles.main(backport.text(R.strings.mapbox.questFlag.frozen.text())), blockWidth=420))
        return formatters.packBuildUpBlockData(items, padding=formatters.packPadding(top=20, left=18))
