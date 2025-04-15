# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/tooltips/quest_flag_tooltip.py
import typing
from CurrentVehicle import g_currentVehicle
from gui import makeHtmlString
from gui.Scaleform.daapi.view.lobby.session_stats.shared import toIntegral
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.shared.formatters import text_styles, icons
from gui.shared.tooltips import formatters
from gui.impl.gen import R
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.tooltips.quests import StringTokenBonusFormatter
from helpers import dependency
from historical_battles.quests.vehicle_quest_info import VehicleQuestInfo
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
if typing.TYPE_CHECKING:
    from gui.server_events.event_items import Quest

class QuestFlagTooltip(BlocksTooltipData):
    _MAX_QUESTS_PER_TOOLTIP = 4
    _MAX_BONUSES_PER_QUEST = 2
    __gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, context):
        super(QuestFlagTooltip, self).__init__(context, TOOLTIPS_CONSTANTS.HB_ORDER_TOOLTIP)
        self._setContentMargin(top=2, left=3, bottom=3, right=3)
        self._setMargins(afterBlock=0)
        self._setWidth(300)

    def _packBlocks(self, *args, **kwargs):
        items = super(QuestFlagTooltip, self)._packBlocks()
        vehicle = g_currentVehicle.item
        vehicleQuestInfo = VehicleQuestInfo(vehicle)
        vehicleQuestInfo.init()
        if vehicleQuestInfo.isAnyAvailable() and not vehicleQuestInfo.isAllCompleted():
            self.__exportAvailableHeader(items)
            self.__exportActiveQuestsBody(items, vehicleQuestInfo)
        elif vehicleQuestInfo.isEmptyConfig():
            self.__exportMaintenanceHeader(items)
        elif vehicleQuestInfo.isAllCompleted():
            self.__exportCompletedHeader(items)
            self.__exportActiveQuestsBody(items, vehicleQuestInfo)
        else:
            self.__exportUnavailableHeader(items)
        return items

    def __getHeader(self, title, desc, showImg=True, descFormatter=text_styles.neutral):
        img = None
        if showImg:
            img = backport.image(R.images.historical_battles.gui.maps.icons.quests.bz_head())
        return formatters.packImageTextBlockData(title=text_styles.highTitle(title), desc=descFormatter(desc), img=img, txtPadding=formatters.packPadding(top=10), txtOffset=10)

    def __getQuestItem(self, quest):
        bonusNames = self.__getFormattedBonuses(quest)
        return self._packQuest(quest.getUserName(), bonusNames, quest.isCompleted())

    def __getFormattedBonuses(self, quest):
        bonusNames = []
        for bonus in quest.getBonuses():
            bonusNames.extend(StringTokenBonusFormatter().format(bonus))

        return bonusNames

    def _packQuest(self, questName, bonuses, isCompleted):
        blocks = []
        bonusesLength = len(bonuses)
        if bonusesLength > self._MAX_BONUSES_PER_QUEST:
            bonuses = bonuses[:self._MAX_BONUSES_PER_QUEST]
            formater = '{{}} {}'.format(text_styles.stats(backport.text(R.strings.tooltips.hangar.header.quests.reward.rest(), count=bonusesLength - self._MAX_BONUSES_PER_QUEST)))
        else:
            formater = '{}'
        strBonus = ', '.join(bonuses)
        title = self.__getCheckImageTag() + questName if isCompleted else questName
        blocks.append(formatters.packImageTextBlockData(title=text_styles.middleTitle(title), desc=text_styles.neutral(backport.text(R.strings.tooltips.hangar.header.quests.reward(), rewards=text_styles.main(formater.format(strBonus)))), imgPadding=formatters.packPadding(top=-13, left=-2), txtPadding=formatters.packPadding(top=-2), txtGap=6, padding=formatters.packPadding(bottom=6), txtOffset=20))
        return formatters.packBuildUpBlockData(blocks, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)

    def __exportAvailableHeader(self, items):
        flagImg = icons.makeImageTag(backport.image(R.images.gui.maps.icons.eventBoards.flagIcons.flag_icon()))
        title = backport.text(R.strings.hb_tooltips.quest.tooltip.header.label())
        desc = backport.text(R.strings.hb_tooltips.quest.tooltip.header.in_progress())
        items.append(self.__getHeader(title, flagImg + desc))

    def __exportCompletedHeader(self, items):
        flagImg = icons.makeImageTag(backport.image(R.images.gui.maps.icons.library.time_icon()))
        title = backport.text(R.strings.hb_tooltips.quest.tooltip.header.label())
        if self.__gameEventController.isLastDay():
            desc = backport.text(R.strings.hb_tooltips.quest.tooltip.header.endsIn(), hours=toIntegral(self.__gameEventController.getHoursLeft()))
        else:
            desc = backport.text(R.strings.hb_tooltips.quest.tooltip.header.cooldown.hours(), hours=toIntegral(self.__gameEventController.getQuestsUpdateHoursLeft()))
        items.append(self.__getHeader(title, flagImg + ' ' + desc))

    def __exportUnavailableHeader(self, items):
        title = backport.text(R.strings.hb_tooltips.quest.tooltip.header.unavailable())
        desc = backport.text(R.strings.hb_tooltips.quest.tooltip.body.unavailable(), vehiclesLevelFrom=7, vehiclesLevelTo=10)
        items.append(formatters.packTitleDescBlock(title=text_styles.middleTitle(title), desc=text_styles.main(desc), padding=formatters.packPadding(top=12, bottom=5, left=15)))

    def __exportMaintenanceHeader(self, items):
        title = backport.text(R.strings.hb_tooltips.quest.tooltip.header.maintenance())
        desc = backport.text(R.strings.hb_tooltips.quest.tooltip.body.maintenance())
        items.append(formatters.packTitleDescBlock(title=text_styles.middleTitle(title), desc=text_styles.main(desc), padding=formatters.packPadding(top=12, bottom=5, left=15, right=6)))

    def __exportActiveQuestsBody(self, items, vehicleQuestInfo):
        quests = vehicleQuestInfo.getAvailableQuests()
        questsCount = len(quests)
        showingCount = min(questsCount, self._MAX_QUESTS_PER_TOOLTIP)
        for i in range(showingCount):
            items.append(self.__getQuestItem(quests[i]))

        rest = questsCount - showingCount
        if rest > 0:
            items.append(self._getBottom(rest))

    def _getBottom(self, value):
        formater = text_styles.main
        icon = ''
        tooltipText = R.strings.tooltips.hangar.header.quests.bottom()
        return formatters.packTextBlockData(text=makeHtmlString('html_templates:lobby/textStyle', 'alignText', {'align': 'center',
         'message': formater('{0}{1}'.format(icon, backport.text(tooltipText, count=value)))}), padding=formatters.packPadding(top=-10, bottom=10))

    def __getCheckImageTag(self):
        return icons.makeImageTag(backport.image(R.images.gui.maps.icons.missions.icons.check_green()))
