# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/boosters.py
from gui.Scaleform.daapi.view.lobby.server_events import events_helpers
from gui.goodies import g_goodiesCache
from gui.server_events.EventsCache import g_eventsCache
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.tooltips import TOOLTIP_TYPE
from gui.shared.tooltips import formatters
from gui.shared.formatters import text_styles
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from helpers.i18n import makeString
from gui.Scaleform.locale.MENU import MENU

class BoosterTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(BoosterTooltipData, self).__init__(context, TOOLTIP_TYPE.BOOSTER)
        self._setContentMargin(top=15, left=19, bottom=21, right=22)
        self._setMargins(afterBlock=14)
        self._setWidth(396)

    def _packBlocks(self, boosterID, *args, **kwargs):
        items = super(BoosterTooltipData, self)._packBlocks(*args, **kwargs)
        booster = g_goodiesCache.getBooster(boosterID)
        questsResult = self.__getBoosterQuestNames(boosterID)
        items.append(formatters.packBuildUpBlockData([formatters.packTitleDescBlock(text_styles.highTitle(booster.fullUserName), desc=text_styles.main(booster.description)), formatters.packImageBlockData(img=booster.bigTooltipIcon, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, width=180, height=180, padding={'top': -14,
          'bottom': -14})]))
        items.append(self.__packDueDate(booster))
        if len(questsResult):
            qNames = '"%s"' % ', '.join(questsResult)
            items.append(self.__packAccessCondition(qNames))
        if booster.inCooldown:
            items.append(self.__packActiveState(booster.getUsageLeftTimeStr()))
        return items

    def __packDueDate(self, booster):
        if booster.expiryTime:
            text = makeString(TOOLTIPS.BOOSTERSWINDOW_BOOSTER_DUEDATE_VALUE, date=booster.getExpiryDate())
        else:
            text = makeString(MENU.BOOSTERSWINDOW_BOOSTERSTABLERENDERER_UNDEFINETIME)
        return formatters.packBuildUpBlockData([formatters.packTitleDescBlock(text_styles.middleTitle(TOOLTIPS.BOOSTERSWINDOW_BOOSTER_DUEDATE_TITLE), text_styles.standard(text))])

    def __packAccessCondition(self, questName):
        return formatters.packBuildUpBlockData([formatters.packTitleDescBlock(text_styles.middleTitle(TOOLTIPS.BOOSTERSWINDOW_BOOSTER_GETCONDITION_TITLE), text_styles.standard(makeString(TOOLTIPS.BOOSTERSWINDOW_BOOSTER_GETCONDITION_VALUE, questName=text_styles.neutral(questName))))])

    def __packActiveState(self, time):
        title = text_styles.statInfo(TOOLTIPS.BOOSTERSWINDOW_BOOSTER_ACTIVE_TITLE)
        state = text_styles.main(makeString(TOOLTIPS.BOOSTERSWINDOW_BOOSTER_ACTIVE_VALUE, time=text_styles.stats(time)))
        return formatters.packBuildUpBlockData([formatters.packAlignedTextBlockData(title, BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding={'bottom': 4}), formatters.packAlignedTextBlockData(state, BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER)])

    def __getBoosterQuestNames(self, boosterID):
        questsResult = set()
        quests = g_eventsCache.getAllQuests(lambda q: q.isAvailable()[0] and not q.isCompleted(), includePotapovQuests=True)
        for q in quests.itervalues():
            bonuses = q.getBonuses('goodies')
            for b in bonuses:
                boosters = b.getBoosters()
                for qBooster, count in boosters.iteritems():
                    if boosterID == qBooster.boosterID:
                        questsResult.add(q.getUserName())

        for chapter, boosters in events_helpers.getTutorialQuestsBoosters().iteritems():
            for booster, count in boosters:
                if boosterID == booster.boosterID:
                    questsResult.add(chapter.getTitle())

        return questsResult
