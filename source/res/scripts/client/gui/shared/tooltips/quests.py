# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/quests.py
import constants
from CurrentVehicle import g_currentVehicle
from gui import makeHtmlString
from gui.Scaleform.daapi.view.lobby.server_events import events_helpers
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.genConsts.CUSTOMIZATION_ITEM_TYPE import CUSTOMIZATION_ITEM_TYPE
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.server_events.bonuses import CustomizationsBonus
from gui.server_events import settings as quest_settings
from gui.shared.formatters import text_styles, icons
from gui.shared.tooltips import TOOLTIP_TYPE, formatters
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency
from helpers.i18n import makeString as _ms
from skeletons.gui.game_control import IQuestsController
from skeletons.gui.server_events import IEventsCache
_MAX_QUESTS_PER_TOOLTIP = 4
_MAX_BONUSES_PER_QUEST = 2

class QuestsPreviewTooltipData(BlocksTooltipData):
    _eventsCache = dependency.descriptor(IEventsCache)
    _questController = dependency.descriptor(IQuestsController)

    def __init__(self, context):
        super(QuestsPreviewTooltipData, self).__init__(context, TOOLTIP_TYPE.QUESTS)
        self._setContentMargin(top=2, left=3, bottom=3, right=3)
        self._setMargins(afterBlock=0)
        self._setWidth(297)

    def _packBlocks(self, *args, **kwargs):
        items = super(QuestsPreviewTooltipData, self)._packBlocks()
        vehicle = g_currentVehicle.item
        quests = self._questController.getQuestForVehicle(vehicle)
        quests = sorted([ q for q in quests if not q.isCompleted() ], events_helpers.questsSortFunc)
        if len(quests) > 0:
            items.append(self._getHeader(len(quests), vehicle.shortUserName, TOOLTIPS.HANGAR_HEADER_QUESTS_DESCRIPTION_VEHICLE))
            for quest in quests:
                bonusNames = []
                for bonus in quest.getBonuses():
                    bonusFormat = bonus.format()
                    if bonusFormat:
                        if isinstance(bonus, CustomizationsBonus):
                            formatStr = '#vehicle_customization:typeSwitchScreen/typeName/{0}'
                            for item in bonus.getCustomizations():
                                itemType = item.get('custType')
                                cType = CUSTOMIZATION_ITEM_TYPE.CI_TYPES.index(itemType)
                                bonusForamt = _ms(formatStr.format(cType))
                                bonusNames.append(bonusForamt)

                        else:
                            bonusNames.extend(bonusFormat.split(', '))

                isAvailable, _ = quest.isAvailable()
                items.append(self._packQuest(quest.getUserName(), bonusNames, quest_settings.isNewCommonEvent(quest), isAvailable))
                if len(items) > _MAX_QUESTS_PER_TOOLTIP:
                    break

            rest = len(quests) - len(items) + 1
            if rest > 0:
                items.append(self._getBottom(rest))
        else:

            def _filter(q):
                return q.getType() not in constants.EVENT_TYPE.SHARED_QUESTS and not q.isCompleted()

            allQuests = self._eventsCache.getQuests(filterFunc=_filter)
            if len(allQuests) > 0:
                items.append(self._getHeader(len(quests), vehicle.shortUserName, TOOLTIPS.HANGAR_HEADER_QUESTS_DESCRIPTION_VEHICLE))
                items.append(self._getBody(TOOLTIPS.HANGAR_HEADER_QUESTS_EMPTY_VEHICLE))
            else:
                items.append(self._getHeader(len(quests), vehicle.shortUserName, TOOLTIPS.HANGAR_HEADER_QUESTS_DESCRIPTION))
                items.append(self._getBody(TOOLTIPS.HANGAR_HEADER_QUESTS_EMPTY))
            items.append(self._getBottom(0))
        return items

    def _getHeader(self, count, vehicleName, description):
        return formatters.packImageTextBlockData(title=text_styles.highTitle(_ms(TOOLTIPS.HANGAR_HEADER_QUESTS_HEADER, count=count)), img=RES_ICONS.MAPS_ICONS_QUESTS_QUESTTOOLTIPHEADER, txtPadding=formatters.packPadding(top=20), txtOffset=20, desc=text_styles.main(_ms(description, vehicle=vehicleName)))

    def _getBottom(self, value):
        if value > 0:
            formater = text_styles.main
            icon = ''
            tooltipText = TOOLTIPS.HANGAR_HEADER_QUESTS_BOTTOM
        else:
            formater = text_styles.success
            icon = icons.checkmark()
            tooltipText = TOOLTIPS.HANGAR_HEADER_QUESTS_BOTTOM_EMPTY
        return formatters.packTextBlockData(text=makeHtmlString('html_templates:lobby/textStyle', 'alignText', {'align': 'center',
         'message': formater('{0}{1}'.format(icon, _ms(tooltipText, count=value)))}), padding=formatters.packPadding(top=-10, bottom=10))

    def _packQuest(self, questName, bonuses, isNew, isAvailable):
        blocks = []
        bonusesLength = len(bonuses)
        if bonusesLength > _MAX_BONUSES_PER_QUEST:
            bonuses = bonuses[:_MAX_BONUSES_PER_QUEST]
            formater = '{{}} {}'.format(text_styles.stats(_ms(TOOLTIPS.HANGAR_HEADER_QUESTS_REWARD_REST, count=bonusesLength - _MAX_BONUSES_PER_QUEST)))
        else:
            formater = '{}'
        strBonus = ', '.join(bonuses)
        title = questName if isAvailable else '{} {}'.format(icons.notAvailableRed(), questName)
        blocks.append(formatters.packImageTextBlockData(img=RES_ICONS.MAPS_ICONS_LIBRARY_NEW if isNew else '', title=text_styles.middleTitle(title), desc=text_styles.neutral(_ms(TOOLTIPS.HANGAR_HEADER_QUESTS_REWARD, rewards=text_styles.main(formater.format(strBonus)))), imgPadding=formatters.packPadding(top=-13, left=-2), txtPadding=formatters.packPadding(top=-2), txtGap=6, padding=formatters.packPadding(bottom=3 if isNew else 15), txtOffset=20))
        return formatters.packBuildUpBlockData(blocks, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)

    def _getBody(self, text):
        return formatters.packBuildUpBlockData([formatters.packTextBlockData(text=text_styles.main(text), padding=formatters.packPadding(left=20, top=-10, bottom=10))], linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)


class PersonalQuestsPreviewTooltipData(BlocksTooltipData):
    _eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, context):
        super(PersonalQuestsPreviewTooltipData, self).__init__(context, TOOLTIP_TYPE.QUESTS)
        self._setContentMargin(top=2, left=2, bottom=3, right=1)
        self._setMargins(afterBlock=0)
        self._setWidth(300)

    def _packBlocks(self, *args, **kwargs):
        quest, tile = self._findPersonalQuest()
        if quest is None or tile is None:
            return []
        else:
            items = super(PersonalQuestsPreviewTooltipData, self)._packBlocks()
            items.append(formatters.packImageTextBlockData(title=text_styles.highTitle(tile.getUserName()), img=RES_ICONS.maps_icons_quests_tiles('{}_tooltip.png'.format(tile.getIconID())), txtPadding=formatters.packPadding(top=18), txtOffset=20, desc=text_styles.middleTitle(quest.getUserName())))
            items.append(self._getBody('{}\n{}\n\n{}\n{}'.format(text_styles.middleTitle(_ms(QUESTS.QUESTTASKDETAILSVIEW_MAINCONDITIONS)), quest.getUserMainCondition(), text_styles.middleTitle(_ms(QUESTS.QUESTTASKDETAILSVIEW_ADDITIONALCONDITIONS)), quest.getUserAddCondition())))
            items.append(self._getAwardsBlock(quest))
            return items

    def _getBody(self, text):
        return formatters.packBuildUpBlockData([formatters.packTextBlockData(text=text_styles.main(text), padding=formatters.packPadding(left=20, right=20))], linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding=formatters.packPadding(bottom=18))

    def _getBonusListView(self, bonuses):
        list = []
        for bonus in bonuses:
            if bonus.isShowInGUI():
                for item in bonus.getCarouselList():
                    item.pop('isSpecial', None)
                    item.pop('tooltip', None)
                    item.pop('specialArgs', None)
                    item.pop('specialAlias', None)
                    list.append(item)

        return list

    def _getAwardsBlock(self, quest):
        items = []
        mainAwards = self._getBonusListView(quest.getBonuses(isMain=True))
        items.append(formatters.packTextBlockData(text=text_styles.main(text_styles.middleTitle(QUESTS.QUESTS_TABS_AWARD_TEXT)), padding=formatters.packPadding(left=20, top=18, right=20)))
        items.append(formatters.packQuestAwardsBlockData(mainAwards, padding=formatters.packPadding(left=20, top=-10, right=20)))
        bonuses = quest.getBonuses(isMain=False)
        addAwards = []
        for bonus in bonuses:
            bonusForamt = bonus.format()
            addAwards.append(bonusForamt)

        items.append(formatters.packTextBlockData(text='{} {}'.format(text_styles.middleTitle(QUESTS.QUESTS_TABS_ADDAWARD_TEXT), ','.join(addAwards)), padding=formatters.packPadding(left=20, right=20)))
        return formatters.packBuildUpBlockData(blocks=items, stretchBg=False, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILD_BLOCK_AWARD_BG_LINKAGE, padding=formatters.packPadding(top=-16, bottom=10), gap=10)

    def _findPersonalQuest(self):
        vehicle = g_currentVehicle.item
        vehicleLvl = vehicle.level
        vehicleType = vehicle.type
        for tile in self._eventsCache.potapov.getTiles().itervalues():
            if not tile.isUnlocked():
                continue
            for chainID, chain in tile.getQuests().iteritems():
                if tile.getChainVehicleClass(chainID) != vehicleType:
                    continue
                for quest in chain.itervalues():
                    if vehicleLvl < quest.getVehMinLevel():
                        continue
                    if quest.isInProgress():
                        return (quest, tile)
                    if quest.needToGetReward():
                        return (quest, tile)

        return (None, None)
