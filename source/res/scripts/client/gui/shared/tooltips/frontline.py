# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/frontline.py
from CurrentVehicle import g_currentVehicle
from gui import makeHtmlString
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.daapi.view.lobby.missions.missions_helper import isEpicDailyQuestsRefreshAvailable
from gui.impl import backport
from gui.impl.backport import getTillTimeStringByRClass as getTimeStr
from gui.impl.gen import R
from gui.server_events.awards_formatters import AWARDS_SIZES, getEpicViewAwardPacker
from gui.shared.formatters import text_styles, icons
from gui.shared.money import Currency
from gui.shared.tooltips import TOOLTIP_TYPE, formatters
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency, time_utils, int2roman
from helpers.i18n import makeString as _ms
from skeletons.gui.game_control import ITradeInController, IEpicBattleMetaGameController, IQuestsController, IEventProgressionController
_R_EPIC_BATTLE = R.strings.epic_battle.questsTooltip.epicBattle
_PREVIEW_TOOLTIP_WIDTH = 350
_GIFTS_WIDTH = 265

class FrontlinePackPreviewTooltipData(BlocksTooltipData):
    __tradeIn = dependency.descriptor(ITradeInController)

    def __init__(self, context):
        super(FrontlinePackPreviewTooltipData, self).__init__(context, TOOLTIP_TYPE.FRONTLINE)
        self._setWidth(_PREVIEW_TOOLTIP_WIDTH)
        self._setContentMargin(top=40, left=0, bottom=0, right=30)

    def _packBlocks(self, discount, bonuses):
        items = super(FrontlinePackPreviewTooltipData, self)._packBlocks()
        blocks = [self._getHeader()]
        if self.__tradeIn.isEnabled():
            blocks.append(formatters.packTextBlockData(padding=formatters.packPadding(left=50, bottom=15), text=_ms(text_styles.main(TOOLTIPS.FRONTLINEPACKPREVIEW_TRADEINBODY))))
        blocks.append(self._getDiscountSection(discount, bonuses))
        items.append(formatters.packBuildUpBlockData(blocks=blocks, gap=5, layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_VERTICAL))
        return items

    def _getHeader(self):
        return formatters.packImageTextBlockData(title=text_styles.middleTitle(TOOLTIPS.FRONTLINEPACKPREVIEW_HEADER), img=backport.image(R.images.gui.maps.icons.epicBattles.modeIcon()), imgPadding=formatters.packPadding(left=10, top=-30), descPadding=formatters.packPadding(left=-7, right=30), txtPadding=formatters.packPadding(left=-7, right=30, top=-5), padding=formatters.packPadding(bottom=-17), txtGap=15, desc=text_styles.main(TOOLTIPS.FRONTLINEPACKPREVIEW_BODY))

    def _getGiftBlock(self):
        lineBlock = formatters.packImageBlockData(align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, img=backport.image(R.images.gui.maps.icons.tooltip.line()))
        textBlock = formatters.packTextWithBgBlockData(text=text_styles.concatStylesToSingleLine(icons.makeImageTag(source=backport.image(R.images.gui.maps.icons.library.icon_gift()), width=17, height=15, vSpace=0), text_styles.vehicleStatusCriticalTextSmall(TOOLTIPS.FRONTLINEPACKPREVIEW_GIFT)), bgColor=0, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER)
        return formatters.packBuildUpBlockData(blocks=[lineBlock, textBlock], gap=-13, blockWidth=_PREVIEW_TOOLTIP_WIDTH, layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_VERTICAL, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER)

    def _getDiscountSection(self, discount, bonuses):
        discount = discount or 0
        formattedDiscount = makeHtmlString('html_templates:lobby/quests/actions', Currency.GOLD, {'value': backport.getGoldFormat(long(discount))})
        discountBlock = formatters.packTextBlockData(padding=formatters.packPadding(left=50), text=_ms(text_styles.main(TOOLTIPS.FRONTLINEPACKPREVIEW_DISCOUNT), value=formattedDiscount))
        return formatters.packBuildUpBlockData(blocks=[discountBlock, self._getGiftBlock(), self._getBonusSection(bonuses)], gap=25, layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_VERTICAL, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER)

    def _getBonusSection(self, bonuses):
        hBlocks = []
        vBlocks = []
        for item in bonuses:
            if len(hBlocks) == 2:
                vBlocks.append(formatters.packBuildUpBlockData(blocks=hBlocks, blockWidth=_GIFTS_WIDTH, gap=5, layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_HORIZONTAL, align=BLOCKS_TOOLTIP_TYPES.ALIGN_LEFT))
                hBlocks = []
            hBlocks.append(formatters.packImageTextBlockData(desc=text_styles.main(item.text), img=item.img, blockWidth=130))

        vBlocks.append(formatters.packBuildUpBlockData(blocks=hBlocks, blockWidth=_GIFTS_WIDTH, gap=5, layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_HORIZONTAL, align=BLOCKS_TOOLTIP_TYPES.ALIGN_LEFT))
        return formatters.packBuildUpBlockData(blocks=vBlocks, blockWidth=_PREVIEW_TOOLTIP_WIDTH, padding=formatters.packPadding(top=-25, left=42), layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_VERTICAL, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER)


_RANK_TOOLTIP_WIDTH = 330
_RANK_ICONS = [R.images.gui.maps.icons.library.epicRank.big_rank_recruit(),
 R.images.gui.maps.icons.library.epicRank.big_rank_private(),
 R.images.gui.maps.icons.library.epicRank.big_rank_sergeant(),
 R.images.gui.maps.icons.library.epicRank.big_rank_lieutenant(),
 R.images.gui.maps.icons.library.epicRank.big_rank_captain(),
 R.images.gui.maps.icons.library.epicRank.big_rank_major(),
 R.images.gui.maps.icons.library.epicRank.big_rank_general()]

class FrontlineRankTooltipData(BlocksTooltipData):
    __frontLine = dependency.descriptor(IEpicBattleMetaGameController)
    __rank = 0

    def __init__(self, context):
        super(FrontlineRankTooltipData, self).__init__(context, TOOLTIP_TYPE.FRONTLINE)
        self._setWidth(_RANK_TOOLTIP_WIDTH)
        self._setContentMargin(top=20, left=18, bottom=20, right=12)

    def _packBlocks(self, rank):
        items = super(FrontlineRankTooltipData, self)._packBlocks()
        self.__rank = rank
        items.append(formatters.packBuildUpBlockData(blocks=[self._getHeader(), self._getIcon(), self._getBottom()], layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_VERTICAL))
        return items

    def _getIcon(self):
        return formatters.packImageBlockData(img=backport.image(_RANK_ICONS[self.__rank]), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER)

    def _getHeader(self):
        return formatters.packTextBlockData(text=_ms(text_styles.middleTitle(TOOLTIPS.FRONTLINERANK_HEADER), rank=_ms(EPIC_BATTLE.getRankLabel(max(self.__rank, 1)))))

    def _getBottom(self):
        if self.__rank > 0:
            rankSettings = self.__frontLine.getPlayerRanksInfo()
            exp, bonus = rankSettings.get(self.__rank, (0, 0))
            blocks = [formatters.packTextBlockData(text=_ms(text_styles.main(TOOLTIPS.FRONTLINERANK_EXP), exp=text_styles.gold(exp))), formatters.packTextBlockData(text=_ms(text_styles.main(TOOLTIPS.FRONTLINERANK_EXPBONUS), bonus=text_styles.gold('+%d%%' % bonus)))]
            bottomBlocks = formatters.packBuildUpBlockData(blocks=blocks, layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_VERTICAL)
        else:
            bottomBlocks = formatters.packTextBlockData(text=_ms(text_styles.main(TOOLTIPS.FRONTLINERANK_FIRSTRANKDESCR)))
        return bottomBlocks


class FrontlineQuestsTooltipData(BlocksTooltipData):
    __eventProgressionController = dependency.descriptor(IEventProgressionController)
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)
    __questController = dependency.descriptor(IQuestsController)

    def __init__(self, context):
        super(FrontlineQuestsTooltipData, self).__init__(context, TOOLTIP_TYPE.EPIC_QUESTS)
        self._setContentMargin(top=0, left=0, bottom=0, right=0)
        self._setMargins(afterBlock=0)
        self._setWidth(322)

    def _packBlocks(self, *args, **kwargs):
        quests = [ q for q in self.__questController.getQuestForVehicle(g_currentVehicle.item) if q.getID() in self.__eventProgressionController.questIDs ]
        quests.sort(key=lambda q: q.getPriority(), reverse=True)
        if quests:
            return [self.__packHeader(quests)] + [ self.__packQuest(q) for q in quests ]
        return super(FrontlineQuestsTooltipData, self)._packBlocks()

    def __packHeader(self, quests):
        return formatters.packImageTextBlockData(title=text_styles.highTitle(backport.text(_R_EPIC_BATTLE.header())), desc=text_styles.main(self.__formatDescription(quests)), img=backport.image(R.images.gui.maps.icons.quests.epic_quests_infotip()), txtPadding=formatters.packPadding(top=18), descPadding=formatters.packPadding(top=15), txtOffset=20)

    def __packQuest(self, quest):
        return formatters.packBuildUpBlockData([self.__packQuestInfo(quest), self.__packQuestRewards(quest)])

    def __packQuestInfo(self, quest):
        title = text_styles.middleTitle(quest.getUserName())
        if quest.isCompleted():
            name = text_styles.concatStylesToSingleLine(icons.check(), title)
            selfPadding = formatters.packPadding(top=-3, left=14, right=20)
            descPadding = formatters.packPadding(left=6, top=-6)
        else:
            name = title
            selfPadding = formatters.packPadding(left=20, right=20)
            descPadding = formatters.packPadding(top=-2)
        return formatters.packTitleDescBlock(title=name, desc=text_styles.main(quest.getDescription()), padding=selfPadding, descPadding=descPadding)

    def __packQuestRewards(self, quest):
        packer = getEpicViewAwardPacker()
        return formatters.packBuildUpBlockData([ self.__packQuestReward(bonus) for bonus in packer.format(quest.getBonuses()) ], layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_HORIZONTAL, padding=formatters.packPadding(left=20, right=20), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER)

    def __packQuestReward(self, bonus):
        if bonus.label.startswith('x'):
            align = BLOCKS_TOOLTIP_TYPES.ALIGN_RIGHT
            padding = formatters.packPadding(top=-16, right=12)
        else:
            align = BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER
            padding = formatters.packPadding(top=-16)
        iconBlock = formatters.packImageBlockData(img=bonus.getImage(AWARDS_SIZES.SMALL), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER)
        textBlock = formatters.packAlignedTextBlockData(text=bonus.getFormattedLabel(), align=align, padding=padding)
        return formatters.packBuildUpBlockData(blocks=[iconBlock, textBlock], blockWidth=72, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(top=-8, bottom=-6))

    def __formatDescription(self, quests):
        season = self.__epicController.getCurrentSeason() or self.__epicController.getNextSeason()
        currentTime = time_utils.getCurrentLocalServerTimestamp()
        cycle = season.getCycleInfo()
        if not self.__epicController.isAvailable() or cycle is None:
            return ''
        else:
            _, level, _ = self.__epicController.getPlayerLevelInfo()
            maxLevel = self.__epicController.getMaxPlayerLevel()
            if level < maxLevel:
                description = backport.text(_R_EPIC_BATTLE.unavailable(), reason=backport.text(_R_EPIC_BATTLE.restrict.level(), level=maxLevel))
                return text_styles.concatStylesWithSpace(icons.markerBlocked(), text_styles.error(description))
            if cycle.endDate - currentTime < time_utils.ONE_DAY:
                icon = icons.inProgress(vspace=-3)
                messageID = _R_EPIC_BATTLE.timeLeft
                valueStyle = text_styles.stats
                timeStr = valueStyle(backport.text(R.strings.epic_battle.questsTooltip.epicBattle.lessThanDay()))
                textStyle = text_styles.main
                description = textStyle(backport.text(messageID(), cycle=int2roman(cycle.ordinalNumber), time=timeStr))
                return text_styles.concatStylesWithSpace(icon, description)
            if all((q.isCompleted() for q in quests)) and isEpicDailyQuestsRefreshAvailable():
                data = time_utils.ONE_DAY - time_utils.getServerRegionalTimeCurrentDay()
                valueStyle = text_styles.tutorial
                timeToStr = valueStyle(getTimeStr(data, R.strings.menu.Time.timeLeftShort))
                icon = icons.clockGold()
                textStyle = text_styles.tutorial
                description = textStyle(backport.text(_R_EPIC_BATTLE.startIn(), time=timeToStr))
                return text_styles.concatStylesWithSpace(icon, description)
            getDate = lambda c: c.endDate
            messageID = _R_EPIC_BATTLE.timeLeft
            icon = icons.inProgress(vspace=-3)
            textStyle = text_styles.main
            valueStyle = text_styles.stats
            timeToStr = valueStyle(getTimeStr(getDate(cycle) - currentTime, R.strings.menu.Time.timeLeftShort))
            description = textStyle(backport.text(messageID(), cycle=int2roman(cycle.ordinalNumber), time=timeToStr))
            return text_styles.concatStylesWithSpace(icon, description)
