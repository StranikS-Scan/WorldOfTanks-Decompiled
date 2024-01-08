# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/quests.py
import constants
from battle_pass_common import BATTLE_PASS_RANDOM_QUEST_ID_PREFIX
from CurrentVehicle import g_currentVehicle
from gui import makeHtmlString
from gui.impl import backport
from gui.impl.gen import R
from gui.ranked_battles.ranked_helpers import isRankedQuestID
from gui.Scaleform.daapi.view.lobby.missions import missions_helper
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.genConsts.ICON_TEXT_FRAMES import ICON_TEXT_FRAMES
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.server_events import events_helpers
from gui.server_events.awards_formatters import TokenBonusFormatter, PreformattedBonus, LABEL_ALIGN
from gui.server_events.bonuses import CustomizationsBonus
from gui.server_events.cond_formatters.tooltips import MissionsAccountRequirementsFormatter
from gui.shared.formatters import text_styles, icons
from gui.shared.gui_items import GUI_ITEM_TYPE_NAMES, GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import getTypeSmallIconPath
from gui.shared.tooltips import TOOLTIP_TYPE, formatters
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.utils import flashObject2Dict
from gui.shared.utils.functions import makeTooltip
from helpers import dependency, time_utils
from helpers.i18n import makeString as _ms
from shared_utils import findFirst
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.game_control import IQuestsController, IRankedBattlesController, IBattleRoyaleController, IComp7Controller
from battle_royale.gui.Scaleform.daapi.view.lobby.tooltips.battle_royale_tooltip_quest_helper import getQuestsDescriptionForHangarFlag, getQuestTooltipBlock
_MAX_AWARDS_PER_TOOLTIP = 5
_MAX_QUESTS_PER_TOOLTIP = 4
_MAX_BONUSES_PER_QUEST = 2
_RENT_TYPES = ('rentDays', 'rentBattles', 'rentWins')

class _StringTokenBonusFormatter(TokenBonusFormatter):

    def format(self, bonus):
        result = super(_StringTokenBonusFormatter, self).format(bonus)
        return [ b.userName for b in result ]

    def _formatComplexToken(self, complexToken, token, bonus):
        rTokenAlias = R.strings.tooltips.quests.bonuses.token
        userName = self._getUserName(complexToken.styleID)
        description = self.eventsCache.prefetcher.getTokenDetailedInfo(complexToken.styleID)
        if description is None:
            description = backport.text(rTokenAlias.body())
        tooltip = makeTooltip(userName, description if description else None)
        return PreformattedBonus(bonusName=bonus.getName(), images=self._getTokenImages(complexToken.styleID), label=self._formatBonusLabel(token.count), userName=userName, labelFormatter=self._getLabelFormatter(bonus), tooltip=tooltip, align=LABEL_ALIGN.RIGHT, isCompensation=self._isCompensation(bonus))


class QuestsPreviewTooltipData(BlocksTooltipData):
    _questController = dependency.descriptor(IQuestsController)
    _eventsCache = dependency.descriptor(IEventsCache)
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def __init__(self, context):
        super(QuestsPreviewTooltipData, self).__init__(context, TOOLTIP_TYPE.QUESTS)
        self._setContentMargin(top=2, left=3, bottom=3, right=3)
        self._setMargins(afterBlock=0)
        self._setWidth(297)

    def _getQuests(self, vehicle):
        return sorted(self._questController.getCurrentModeQuestsForVehicle(vehicle, True), key=events_helpers.questsSortFunc)

    def _packBlocks(self, *args, **kwargs):
        items = super(QuestsPreviewTooltipData, self)._packBlocks()
        vehicle = g_currentVehicle.item
        quests = self._getQuests(vehicle)
        if self.__comp7Controller.isComp7PrbActive():
            quests = [ quest for quest in quests if quest.hasBonusType(constants.ARENA_BONUS_TYPE.COMP7) ]
        if quests:
            items.append(self._getHeader(len(quests), vehicle.shortUserName, R.strings.tooltips.hangar.header.quests.description.vehicle()))
            for quest in quests:
                items.append(self.__getQuestItem(quest))
                if len(items) > _MAX_QUESTS_PER_TOOLTIP:
                    break

            rest = len(quests) - len(items) + 1
            if rest > 0 and self._isShowBottom(vehicle):
                items.append(self._getBottom(rest))
        elif not self.__battleRoyaleController.isBattleRoyaleMode():
            if self.__hasAnyUncompletedQuests():
                items.append(self._getHeader(0, vehicle.shortUserName, R.strings.tooltips.hangar.header.quests.description.vehicle()))
                items.append(self._getBody(TOOLTIPS.HANGAR_HEADER_QUESTS_EMPTY_VEHICLE))
            else:
                items.append(self._getHeader(0, vehicle.shortUserName, R.strings.tooltips.hangar.header.quests.description()))
                items.append(self._getBody(TOOLTIPS.HANGAR_HEADER_QUESTS_EMPTY))
            if self._isShowBottom(vehicle):
                items.append(self._getBottom(0))
        return items

    def __hasAnyUncompletedQuests(self):
        requestCriteria = REQ_CRITERIA.INVENTORY
        requestCriteria |= ~REQ_CRITERIA.VEHICLE.DISABLED_IN_PREM_IGR
        requestCriteria |= ~REQ_CRITERIA.VEHICLE.EXPIRED_RENT
        requestCriteria |= ~REQ_CRITERIA.VEHICLE.EVENT_BATTLE
        requestCriteria |= ~REQ_CRITERIA.VEHICLE.BATTLE_ROYALE
        vehicles = self.__itemsCache.items.getVehicles(requestCriteria).values() or []
        getCurrentModeQuestsForVehicle = self._questController.getCurrentModeQuestsForVehicle
        return any([ bool(getCurrentModeQuestsForVehicle(veh, True)) for veh in vehicles ])

    def __getQuestItem(self, quest):
        if self.__battleRoyaleController.isBattleRoyaleMode():
            return getQuestTooltipBlock(quest)
        bonusNames = []
        for bonus in quest.getBonuses():
            if bonus.getName() == 'battleToken':
                bonusNames.extend(_StringTokenBonusFormatter().format(bonus))
            bonusFormat = bonus.format()
            if bonusFormat:
                if isinstance(bonus, CustomizationsBonus):
                    for item in bonus.getCustomizations():
                        itemTypeName = item.get('custType')
                        if itemTypeName == 'projection_decal':
                            itemTypeName = GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.PROJECTION_DECAL]
                        elif itemTypeName == 'personal_number':
                            itemTypeName = GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.PERSONAL_NUMBER]
                        bonusFmt = _ms(ITEM_TYPES.customization(itemTypeName))
                        bonusNames.append(bonusFmt)

                else:
                    bonusNames.extend(bonusFormat.split(', '))

        isAvailable, _ = quest.isAvailable()
        return self._packBattlePassRandomQuest(quest.getUserName(), isAvailable) if str(quest.getID()).startswith(BATTLE_PASS_RANDOM_QUEST_ID_PREFIX) else self._packQuest(quest.getUserName(), bonusNames, isAvailable)

    def _getHeader(self, count, vehicleName, description):
        if self.__battleRoyaleController.isBattleRoyaleMode():
            questHeader = backport.text(R.strings.epic_battle.questsTooltip.epicBattle.steelhunter.header())
            img = backport.image(R.images.gui.maps.icons.quests.epic_steelhunter_quests_infotip())
            desc = getQuestsDescriptionForHangarFlag()
        else:
            questHeader = backport.text(R.strings.tooltips.hangar.header.quests.header(), count=count)
            img = backport.image(R.images.gui.maps.icons.quests.questTooltipHeader())
            desc = text_styles.main(backport.text(description, vehicle=vehicleName))
        return formatters.packImageTextBlockData(title=text_styles.highTitle(questHeader), img=img, txtPadding=formatters.packPadding(top=20), txtOffset=20, desc=desc)

    def _getBottom(self, value):
        if value > 0:
            formater = text_styles.main
            icon = ''
            tooltipText = R.strings.tooltips.hangar.header.quests.bottom()
        else:
            formater = text_styles.success
            icon = icons.checkmark()
            tooltipText = R.strings.tooltips.hangar.header.quests.bottom.empty()
        return formatters.packTextBlockData(text=makeHtmlString('html_templates:lobby/textStyle', 'alignText', {'align': 'center',
         'message': formater('{0}{1}'.format(icon, backport.text(tooltipText, count=value)))}), padding=formatters.packPadding(top=-10, bottom=10))

    def _packBattlePassRandomQuest(self, questName, isAvailable):
        blocks = []
        title = questName if isAvailable else '{} {}'.format(icons.notAvailableRed(), questName)
        blocks.append(formatters.packImageTextBlockData(title=text_styles.middleTitle(title), desc='', imgPadding=formatters.packPadding(top=-13, left=-2), txtPadding=formatters.packPadding(top=-2), txtGap=6, padding=formatters.packPadding(bottom=15), txtOffset=20))
        return formatters.packBuildUpBlockData(blocks, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)

    def _packQuest(self, questName, bonuses, isAvailable):
        blocks = []
        bonusesLength = len(bonuses)
        if bonusesLength > _MAX_BONUSES_PER_QUEST:
            bonuses = bonuses[:_MAX_BONUSES_PER_QUEST]
            formater = '{{}} {}'.format(text_styles.stats(backport.text(R.strings.tooltips.hangar.header.quests.reward.rest(), count=bonusesLength - _MAX_BONUSES_PER_QUEST)))
        else:
            formater = '{}'
        strBonus = ', '.join(bonuses)
        title = questName if isAvailable else '{} {}'.format(icons.notAvailableRed(), questName)
        blocks.append(formatters.packImageTextBlockData(title=text_styles.middleTitle(title), desc=text_styles.neutral(backport.text(R.strings.tooltips.hangar.header.quests.reward(), rewards=text_styles.main(formater.format(strBonus)))), imgPadding=formatters.packPadding(top=-13, left=-2), txtPadding=formatters.packPadding(top=-2), txtGap=6, padding=formatters.packPadding(bottom=15), txtOffset=20))
        return formatters.packBuildUpBlockData(blocks, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)

    def _getBody(self, text):
        return formatters.packBuildUpBlockData([formatters.packTextBlockData(text=text_styles.main(text), padding=formatters.packPadding(left=20, top=-10, bottom=10))], linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)

    def _isShowBottom(self, vehicle=None):
        return True


class ScheduleQuestTooltipData(BlocksTooltipData):
    _questController = dependency.descriptor(IQuestsController)

    def __init__(self, context):
        super(ScheduleQuestTooltipData, self).__init__(context, TOOLTIP_TYPE.QUESTS)
        self._setContentMargin(top=15, left=15, bottom=15, right=10)
        self._setWidth(295)

    def _packBlocks(self, *args, **kwargs):
        items = super(ScheduleQuestTooltipData, self)._packBlocks()
        items.append(formatters.packTitleDescBlock(text_styles.highTitle(TOOLTIPS.QUESTS_SCHEDULE_HEADER), text_styles.standard(TOOLTIPS.QUESTS_SCHEDULE_DESCRIPTION), padding=formatters.packPadding(bottom=3)))
        eventID = args[0]
        items.append(self._getBody(eventID))
        event = findFirst(lambda q: q.getID() == eventID, self._questController.getAllAvailableQuests())
        timerMsg = missions_helper.getMissionInfoData(event).getTimerMsg()
        if timerMsg:
            items.append(formatters.packTextBlockData(timerMsg))
        return items

    def _getBody(self, eventID):
        items = []
        source = self._questController.getAllAvailableQuests()
        svrEvents = {e.getID():e for e in source}
        event = svrEvents.get(eventID)
        weekDays = event.getWeekDays()
        if weekDays:
            days = [ _ms(MENU.datetime_weekdays_full(idx)) for idx in event.getWeekDays() ]
            items.append(self._getSubBlock(TOOLTIPS.QUESTS_SCHEDULE_WEEKDAYS, days))
        intervals = event.getActiveTimeIntervals()
        if intervals:
            times = []
            for low, high in intervals:
                times.append('{} - {}'.format(backport.getShortTimeFormat(low), backport.getShortTimeFormat(high)))

            items.append(self._getSubBlock(TOOLTIPS.QUESTS_SCHEDULE_INTERVALS, times, formatters.packPadding(top=18)))
        return formatters.packBuildUpBlockData(blocks=items, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding=formatters.packPadding(top=-3))

    def _getSubBlock(self, header, items, padding=None):
        return formatters.packTitleDescBlock(title=text_styles.middleTitle(header), desc=text_styles.main(', '.join(items)), padding=padding, descPadding=formatters.packPadding(left=20))


class UnavailableQuestTooltipData(BlocksTooltipData):
    _eventsCache = dependency.descriptor(IEventsCache)
    __rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self, context):
        super(UnavailableQuestTooltipData, self).__init__(context, TOOLTIP_TYPE.QUESTS)
        self._setWidth(298)

    def _packBlocks(self, *args, **kwargs):
        source = self._eventsCache.getQuests()
        quest = source.get(args[0])
        items = super(UnavailableQuestTooltipData, self)._packBlocks()
        questID = quest.getID()
        if isRankedQuestID(questID):
            rankedOverrides = self.__getRankedOverrides(quest)
            if rankedOverrides:
                items.extend(rankedOverrides)
                return items
        accountRequirementsFormatter = MissionsAccountRequirementsFormatter()
        requirements = accountRequirementsFormatter.format(quest.accountReqs, quest)
        reqList = self.__getList(requirements)
        if reqList:
            items.extend(self.__getListBlock(TOOLTIPS.QUESTS_UNAVAILABLE_REQUIREMENT_HEADER, reqList))
        if not (quest.vehicleReqs.isAnyVehicleAcceptable() or quest.vehicleReqs.getSuitableVehicles()):
            items.extend(self.__getNotVehicle())
        items.append(self.__getBootom(backport.text(R.strings.tooltips.quests.unavailable.bottom())))
        return items

    def __getBootom(self, text):
        return formatters.packTextBlockData(text=makeHtmlString('html_templates:lobby/textStyle', 'alignText', {'align': 'center',
         'message': text_styles.error('{0} {1}'.format(icons.notAvailable(), text))}))

    def __getList(self, items):
        blocks = []
        for item in items:
            blocks.append(formatters.packTextParameterBlockData(name=text_styles.main(item.get('text')), value=text_styles.main(item.get('bullet', '')), valueWidth=16))

        return blocks

    def __getListBlock(self, header, items, padding=None):
        return [formatters.packTextBlockData(text=text_styles.highTitle(header)), formatters.packBuildUpBlockData(items, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding=padding)]

    def __getNotVehicle(self):
        items = self.__getList([{'text': TOOLTIPS.QUESTS_UNAVAILABLE_VEHICLE_BODY,
          'bullet': TOOLTIPS.QUESTS_UNAVAILABLE_BULLET}])
        return self.__getListBlock(TOOLTIPS.QUESTS_UNAVAILABLE_VEHICLE_HEADER, items)

    def __getRankedOverrides(self, quest):
        header = body = ''
        isLeagues = self.__rankedController.isAccountMastered()
        isAnyPrimeNow = self.__rankedController.hasAvailablePrimeTimeServers()
        isAnyPrimeLeftTotal = self.__rankedController.hasPrimeTimesTotalLeft()
        isAnyPrimeLeftNext = self.__rankedController.hasPrimeTimesNextDayLeft()
        if not isAnyPrimeLeftTotal or not isAnyPrimeLeftNext and quest.isCompleted() and quest.bonusCond.isDaily():
            header = backport.text(R.strings.ranked_battles.quests.tooltip.unavailable.header.seasonEnd())
            body = backport.text(R.strings.ranked_battles.quests.tooltip.unavailable.body.seasonEnd.default())
            season = self.__rankedController.getCurrentSeason()
            if season is not None:
                seasonEnd = time_utils.getTimeDeltaFromNowInLocal(time_utils.makeLocalServerTime(season.getEndDate()))
                timeRes = R.strings.ranked_battles.quests.tooltip.unavailable.body.seasonEnd
                body = backport.getTillTimeStringByRClass(seasonEnd, timeRes)
        elif not isLeagues:
            header = backport.text(R.strings.ranked_battles.quests.tooltip.unavailable.header.notInLeagues())
            body = backport.text(R.strings.ranked_battles.quests.tooltip.unavailable.body.notInLeagues())
        elif not isAnyPrimeNow:
            header = backport.text(R.strings.ranked_battles.quests.tooltip.unavailable.header.allServersPrime())
            body = backport.text(R.strings.ranked_battles.quests.tooltip.unavailable.body.allServersPrime())
        if body and header:
            body = text_styles.main(body)
            bullet = backport.text(R.strings.tooltips.quests.unavailable.bullet())
            return [formatters.packTextBlockData(text=text_styles.highTitle(header)), formatters.packBuildUpBlockData(self.__getList([{'text': body,
               'bullet': bullet}]), linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE), self.__getBootom(backport.text(R.strings.ranked_battles.quests.tooltip.unavailable.bottom()))]
        else:
            return []


class AdditionalAwardTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(AdditionalAwardTooltipData, self).__init__(context, TOOLTIP_TYPE.QUESTS)
        self._setWidth(298)

    def _packBlocks(self, *args, **kwargs):
        items = super(AdditionalAwardTooltipData, self)._packBlocks()
        items.append(formatters.packTextBlockData(text_styles.middleTitle(TOOLTIPS.QUESTS_AWARDS_ADDITIONAL_HEADER), padding=formatters.packPadding(top=8, bottom=8)))
        for bonus in args:
            bonusDict = flashObject2Dict(bonus)
            bonusName = bonusDict.get('name', '')
            imgSource = bonusDict.get('imgSource', '')
            label = bonusDict.get('label', '')
            highlight = bonusDict.get('highlightIcon', '')
            overlay = bonusDict.get('overlayIcon', '')
            rendererData = {'imgSource': imgSource,
             'label': label,
             'highlight': highlight,
             'overlay': overlay}
            if overlay:
                rendererType = 'EquipmentAwardItemExUI'
                padding = formatters.packPadding(top=-35, bottom=-30)
            else:
                rendererType = 'AwardItemExUI'
                padding = formatters.packPadding(top=-7, bottom=-12)
            items.append(formatters.packRendererTextBlockData(rendererType=rendererType, dataType='net.wg.gui.data.AwardItemVO', title=text_styles.main(bonusName), rendererData=rendererData, padding=padding, txtPadding=formatters.packPadding(top=15, left=15), titleAtMiddle=True))
            if len(items) > _MAX_AWARDS_PER_TOOLTIP:
                count = len(args) - len(items) + 1
                if count > 0:
                    items.append(formatters.packTextBlockData(text_styles.main(backport.text(R.strings.tooltips.quests.awards.additional.bottom(), count=count))))
                break

        return items


class RentVehicleAwardTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(RentVehicleAwardTooltipData, self).__init__(context, TOOLTIP_TYPE.QUESTS)
        self._setWidth(298)

    def _packBlocks(self, *args, **kwargs):
        items = super(RentVehicleAwardTooltipData, self)._packBlocks()
        blocks = list()
        blocks.append(formatters.packTextBlockData(text_styles.middleTitle(TOOLTIPS.QUESTS_AWARDS_VEHICLERENT_HEADER), padding=formatters.packPadding(top=8)))
        blocks.append(formatters.packTextParameterWithIconBlockData(name=text_styles.premiumVehicleName(TOOLTIPS.QUESTS_AWARDS_VEHICLERENT_EXPIRE), value='', icon=ICON_TEXT_FRAMES.RENTALS, padding=formatters.packPadding(left=-60), iconYOffset=3))
        items.append(formatters.packBuildUpBlockData(blocks, padding=formatters.packPadding(bottom=-19)))
        blocks = list()
        vehiclesCount = 0
        for rentVehicleData in args:
            rentVehicleData = flashObject2Dict(rentVehicleData)
            vehicleName = rentVehicleData.get('vehicleName', '')
            vehicleType = rentVehicleData.get('vehicleType', '')
            isPremiumVehicle = rentVehicleData.get('isPremium', True)
            rentLeftCount = 0
            rentTypeName = None
            for rentType in _RENT_TYPES:
                rentTypeValue = rentVehicleData.get(rentType, 0)
                if rentTypeValue > 0:
                    rentTypeName = rentType
                    rentLeftCount = rentTypeValue
                    break

            if isPremiumVehicle:
                imgPaddings = formatters.packPadding(right=2)
            else:
                imgPaddings = formatters.packPadding(left=5, right=5, top=4)
            blocks.append(formatters.packImageTextBlockData(title=text_styles.highlightText(vehicleName), img=getTypeSmallIconPath(vehicleType, isPremiumVehicle), imgPadding=imgPaddings, txtPadding=formatters.packPadding(left=2)))
            if rentTypeName is not None and rentLeftCount > 0:
                rentCountStr = text_styles.premiumVehicleName(rentLeftCount)
                rentLeftStr = _ms(TOOLTIPS.getRentLeftTypeLabel(rentTypeName), count=rentCountStr)
                blocks.append(formatters.packTextBlockData(text_styles.main(rentLeftStr), padding=formatters.packPadding(left=28, top=-8, bottom=5)))
            vehiclesCount += 1
            if vehiclesCount >= _MAX_AWARDS_PER_TOOLTIP:
                count = len(args) - vehiclesCount
                if count > 0:
                    blocks.append(formatters.packTextBlockData(text_styles.main(backport.text(R.strings.tooltips.quests.awards.additional.bottom(), count=count))))
                break

        items.append(formatters.packBuildUpBlockData(blocks, padding=formatters.packPadding(bottom=-12)))
        return items


class MissionVehiclesConditionTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(MissionVehiclesConditionTooltipData, self).__init__(context, TOOLTIP_TYPE.QUESTS)
        self._setWidth(385)

    def _packBlocks(self, *args, **kwargs):
        items = super(MissionVehiclesConditionTooltipData, self)._packBlocks()
        blocks = [formatters.packTextBlockData(text_styles.highTitle(TOOLTIPS.QUESTS_VEHICLES_HEADER)), formatters.packTextBlockData(text_styles.main(TOOLTIPS.QUESTS_VEHICLES_DESCRIPTION))]
        lst = args[0].list
        if len(lst) > 6:
            blocks.append(formatters.packMissionVehiclesBlockData(lst[:6], padding=formatters.packPadding(top=20)))
            blocks.append(formatters.packTextBlockData(text_styles.main(backport.text(R.strings.tooltips.quests.vehicles.bottom(), count=len(lst[6:])))))
        else:
            blocks.append(formatters.packMissionVehiclesBlockData(lst, padding=formatters.packPadding(top=20)))
        items.append(formatters.packBuildUpBlockData(blocks))
        return items


class MissionVehiclesTypeTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(MissionVehiclesTypeTooltipData, self).__init__(context, TOOLTIP_TYPE.QUESTS)
        self._setWidth(385)

    def _packBlocks(self, *args, **kwargs):
        items = super(MissionVehiclesTypeTooltipData, self)._packBlocks()
        blocks = [formatters.packTextBlockData(text_styles.highTitle(TOOLTIPS.QUESTS_VEHICLES_HEADER)), formatters.packTextBlockData(text_styles.main(TOOLTIPS.QUESTS_VEHICLES_DESCRIPTION))]
        blocks.append(formatters.packMissionVehiclesTypeBlockData(args[0].list, padding=formatters.packPadding(top=20, bottom=-20)))
        items.append(formatters.packBuildUpBlockData(blocks))
        return items
