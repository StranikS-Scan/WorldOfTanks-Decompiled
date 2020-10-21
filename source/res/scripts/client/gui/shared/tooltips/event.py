# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/event.py
import time
from constants import HE19EnergyPurposes
from gui import makeHtmlString
from gui.Scaleform.daapi.view.lobby.event_boards.formaters import formatTimeAndDate
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.genConsts.ICON_TEXT_FRAMES import ICON_TEXT_FRAMES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.entities.listener import IGlobalListener
from gui.server_events import events_helpers
from gui.server_events.events_helpers import isHalloween, isHalloweenAFK
from gui.server_events.game_event.commander_event_progress import _BONUS_TANKMEN, _BONUS_BATTLE_TOKEN
from gui.shared.formatters import text_styles, icons
from gui.shared.gui_items import Tankman
from gui.shared.gui_items.Tankman import getFullUserName, getRoleUserName
from gui.shared.gui_items.Vehicle import getTypeBigIconPath, VEHICLE_TAGS
from gui.shared.tooltips import TOOLTIP_TYPE, formatters, ToolTipBaseData
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.tooltips.formatters import packBuildUpBlockData
from gui.shared.tooltips.quests import QuestsPreviewTooltipData
from helpers import dependency, int2roman
from helpers.i18n import makeString as _ms
from helpers.time_utils import getTodayStartingTimeUTC, getTimeStructInLocal
from items import vehicles
from skeletons.gui.game_control import IQuestsController
from skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from vehicle import VehicleInfoTooltipData, HeaderBlockConstructor, StatusBlockConstructor

class EventBonusesInfoTooltipData(BlocksTooltipData, IGlobalListener):
    _gameEventController = dependency.descriptor(IGameEventController)
    _itemsCache = dependency.descriptor(IItemsCache)
    _eventsCache = dependency.descriptor(IEventsCache)
    _BLOCK_WIDTH = 300
    _ICON_TOKEN = '../maps/icons/event/token_he19_money.png'

    def __init__(self, context):
        super(EventBonusesInfoTooltipData, self).__init__(context, TOOLTIP_TYPE.TANKMAN)

    def _packBlocks(self, questId, bonusName, icon, **kwargs):
        self.config = self._gameEventController.getVehicleSettings()
        items = super(EventBonusesInfoTooltipData, self)._packBlocks()
        if bonusName == _BONUS_TANKMEN and questId is not None:
            bonus = self._getTankmanBonus(questId)
            items.append(self._getHeaderBlockTankman(bonus))
            items.append(self._getIconBlock(bonus))
            items.append(self._getCommonStatsBlock(bonus))
            items.append(self._getHintBlock())
        elif bonusName == _BONUS_BATTLE_TOKEN:
            items.append(self._getHeaderBlockForBonusToken())
            items.append(self._getIconBlockBonusToken(icon if icon is not None else self._ICON_TOKEN))
            items.append(self._getDescriptionBlockBonusToken())
            items.append(self._getEventCoinsBlock())
            items.append(self._getHowToGetInfoBlockBonusToken())
            items.append(self._getEndingInfoBlockBonusToken())
        return items

    def _getTankmanBonus(self, questId):
        quest = next(self._eventsCache.getHiddenQuests(lambda q: q.getID() == questId).itervalues(), None)
        return None if quest is None else next((bonus for bonus in quest.getBonuses() if bonus.getName() == _BONUS_TANKMEN), None)

    def _getHeaderBlockForBonusToken(self):
        return formatters.packBuildUpBlockData([formatters.packTextBlockData(text=text_styles.highTitle(backport.text(R.strings.tooltips.quests.bonuses.token.header.he19_money())))], blockWidth=self._BLOCK_WIDTH)

    def _getIconBlockBonusToken(self, icon):
        return formatters.packBuildUpBlockData([formatters.packImageBlockData(img=icon, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER)], blockWidth=self._BLOCK_WIDTH, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER)

    def _getDescriptionBlockBonusToken(self):
        return formatters.packBuildUpBlockData([formatters.packTextBlockData(text=text_styles.main(backport.text(R.strings.tooltips.quests.bonuses.token.body.he19_money())))], blockWidth=self._BLOCK_WIDTH)

    def _getEventCoinsBlock(self):
        coinsCount = self._gameEventController.getShop().getCoins()
        eventCoinsBlock = formatters.packMoneyAndXpValueBlock(value=text_styles.eventCoin(backport.getIntegralFormat(coinsCount)), icon=ICON_TEXT_FRAMES.HW20_EVENT_COIN, iconYoffset=5, paddingBottom=0)
        return packBuildUpBlockData([eventCoinsBlock], linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding=formatters.packPadding(left=30), blockWidth=self._BLOCK_WIDTH)

    def _getHowToGetInfoBlockBonusToken(self):
        return formatters.packBuildUpBlockData([formatters.packTextBlockData(text=text_styles.middleTitle(backport.text(R.strings.tooltips.quests.bonuses.token.he19_money.howToGet()))), formatters.packTextBlockData(text=text_styles.main(text_styles.concatStylesToMultiLine(backport.text(R.strings.tooltips.quests.bonuses.token.he19_money.howToGetVariants()))))], blockWidth=self._BLOCK_WIDTH)

    def _getEndingInfoBlockBonusToken(self):
        finishDate = self._eventsCache.getEventFinishTime()
        date = backport.getShortDateFormat(finishDate)
        times = backport.getShortTimeFormat(finishDate)
        text = text_styles.standard(backport.text(R.strings.tooltips.quests.bonuses.token.he19_money.specialConditionsDesc()).format(text_styles.standard(date), text_styles.standard(times)))
        infoBlock = formatters.packTextParameterWithIconBlockData(name=text, value='', icon=ICON_TEXT_FRAMES.ATTENTION1, nameOffset=10, padding=formatters.packPadding(left=-60, bottom=-2))
        return formatters.packBuildUpBlockData([infoBlock], blockWidth=self._BLOCK_WIDTH)

    def _getHeaderBlockTankman(self, bonus):
        data = bonus.getTankmenData()
        if data:
            fullUserName = getFullUserName(data[0].nationID, data[0].firstNameID, data[0].lastNameID)
        else:
            fullUserName = ''
        title = text_styles.highTitle(text_styles.highTitle(fullUserName))
        description = text_styles.concatStylesWithSpace(text_styles.main(backport.text(R.strings.event.event.bonuses.toMode())), text_styles.stats(backport.text(R.strings.event.event.bonuses.Modes())))
        return formatters.packBuildUpBlockData([formatters.packImageTextBlockData(title=title, desc=description)], blockWidth=self._BLOCK_WIDTH)

    def _getInnerBlock(self, bonus):
        innerBlock = []
        if bonus:
            data = bonus[0].getTankmenData()
            innerBlock.append(formatters.packTextBlockData(text=makeHtmlString('html_templates:lobby/textStyle', 'grayTitle', {'message': _ms(TOOLTIPS.HANGAR_CREW_ASSIGNEDTO)})))
            vehIntCD = vehicles.makeIntCompactDescrByID('vehicle', data[0].nationID, data[0].vehicleTypeID)
            nativeVehicle = self._itemsCache.items.getItemByCD(vehIntCD)
            innerBlock.append(formatters.packImageTextBlockData(img=nativeVehicle.iconContour, txtGap=-4, padding=formatters.packPadding(bottom=0, top=10, left=0), title=text_styles.stats(nativeVehicle.shortUserName), desc=text_styles.stats('#menu:header/vehicleType/%s' % nativeVehicle.type)))
        return formatters.packBuildUpBlockData(innerBlock, padding=formatters.packPadding(left=0, top=-5, bottom=0), linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, blockWidth=self._BLOCK_WIDTH)

    def _getCommonStatsBlock(self, bonus):
        commonStatsBlock = []
        data = bonus.getTankmenData()
        dataGroup = bonus.getTankmenGroups()
        vehIntCD = vehicles.makeIntCompactDescrByID('vehicle', data[0].nationID, data[0].vehicleTypeID)
        vehName = text_styles.main(self._itemsCache.items.getItemByCD(vehIntCD).shortUserName)
        roleUserName = getRoleUserName(data[0].role)
        roleLevel = dataGroup[data[0].vehicleTypeID]['roleLevel']
        commonStatsBlock.append(formatters.packTextBlockData(text=makeHtmlString('html_templates:lobby/textStyle', 'grayTitle', {'message': _ms(TOOLTIPS.HANGAR_CREW_SPECIALTY_SKILLS)})))
        commonStatsBlock.append(formatters.packTextParameterBlockData(text_styles.main(roleUserName + ' ') + vehName, text_styles.stats(str(roleLevel) + '%'), valueWidth=90, padding=formatters.packPadding(left=0, right=0, top=5, bottom=0)))
        for skill in data[0].skills:
            commonStatsBlock.append(formatters.packTextParameterBlockData(text_styles.main(Tankman.getSkillUserName(skill)), text_styles.stats('100%'), valueWidth=90))

        commonStatsBlock.append(formatters.packTextParameterBlockData(text_styles.main(_ms(TOOLTIPS.BARRACKS_TANKMEN_RECOVERY_NEWSKILL)), text_styles.stats('2x100%'), valueWidth=90))
        return formatters.packBuildUpBlockData(commonStatsBlock, gap=5, blockWidth=self._BLOCK_WIDTH)

    def _getHintBlock(self):
        return formatters.packBuildUpBlockData([formatters.packImageTextBlockData(title=text_styles.middleTitle(backport.text(R.strings.event.event.bonuses.LearnedSkills()))),
         formatters.packImageBlockData(img='../maps/icons/tankmen/skills/big/commander_sixthSense.png', padding=formatters.packPadding(left=52)),
         formatters.packImageBlockData(img='../maps/icons/tankmen/skills/big/new_skill.png', padding=formatters.packPadding(top=-52, left=116)),
         formatters.packImageBlockData(img='../maps/icons/tankmen/skills/big/new_skill.png', padding=formatters.packPadding(top=-52, left=176))], padding=formatters.packPadding(left=0, top=-5, bottom=0), blockWidth=self._BLOCK_WIDTH, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)

    def _getIconBlock(self, bonus):
        data = bonus.getTankmenData()
        path = Tankman.getBigIconPath(data[0].nationID, data[0].iconID)
        return formatters.packBuildUpBlockData([formatters.packImageBlockData(img=path, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(left=0, top=0, bottom=0))], blockWidth=self._BLOCK_WIDTH)


class EventTankRentInfoTooltipData(BlocksTooltipData, IGlobalListener):
    _gameEventController = dependency.descriptor(IGameEventController)
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, context):
        super(EventTankRentInfoTooltipData, self).__init__(context, TOOLTIP_TYPE.QUESTS)

    def _packBlocks(self, vehicleId, cost, **kwargs):
        self.config = self._gameEventController.getVehiclesController()
        items = super(EventTankRentInfoTooltipData, self)._packBlocks()
        items.append(self._getHeaderBlock(vehicleId))
        items.append(self._getDescriptionBlockInfo())
        items.append(self._getHowToGetBlockInfo(cost))
        items.append(self._getFinalBlcokInfo())
        return items

    def _getHeaderBlock(self, vehicleId):
        return formatters.packTextBlockData(text=text_styles.highTitle(self.itemsCache.items.getItemByCD(vehicleId).shortUserName))

    def _getDescriptionBlockInfo(self):
        return formatters.packTextBlockData(text=text_styles.concatStylesWithSpace(text_styles.main(backport.text(R.strings.event.tooltip.vehicle.premium_rent.description1())), text_styles.main(backport.text(R.strings.event.tooltip.vehicle.premium_rent.description2()))))

    def _getHowToGetBlockInfo(self, cost):
        return formatters.packBuildUpBlockData([formatters.packTextBlockData(text=text_styles.middleTitle(backport.text(R.strings.event.tooltip.vehicle.premium_rent.howToGet()))), formatters.packTextBlockData(text=text_styles.concatStylesToMultiLine(text_styles.main(backport.text(R.strings.event.tooltip.vehicle.premium_rent.howToGetDesc()))))])

    def _getFinalBlcokInfo(self):
        return formatters.packTextBlockData(text=text_styles.main(backport.text(R.strings.event.tooltip.vehicle.premium_rent.description3())))


class EventTankRepairInfoTooltipData(BlocksTooltipData, IGlobalListener):
    _gameEventController = dependency.descriptor(IGameEventController)
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, context):
        super(EventTankRepairInfoTooltipData, self).__init__(context, TOOLTIP_TYPE.QUESTS)
        self._setWidth(320)

    def _packBlocks(self, **kwargs):
        self.config = self._gameEventController.getVehiclesController()
        items = super(EventTankRepairInfoTooltipData, self)._packBlocks()
        items.append(self._getHeaderBlock())
        items.append(self._getDescriptionBlockInfo())
        return items

    def _getHeaderBlock(self):
        return formatters.packTextBlockData(text=text_styles.highTitle(backport.text(R.strings.event.tooltip.vehicle.repair.header())))

    def _getDescriptionBlockInfo(self):
        return formatters.packBuildUpBlockData([self._getIconBlockInfo(), self._getDescriptionFormatter(1, text_styles.main)], gap=10, padding=formatters.packPadding(top=10))

    def _getDescriptionFormatter(self, descriptionIndex, style):
        return formatters.packTextBlockData(text=style(backport.text(R.strings.event.tooltip.vehicle.repair.dyn('description{}'.format(descriptionIndex))())))

    def _getIconBlockInfo(self):
        return formatters.packImageBlockData(img=self._getIcon(), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, width=180, height=135, padding=formatters.packPadding(top=-25, bottom=10))

    def _getIcon(self):
        return backport.image(R.images.gui.maps.icons.event.manageCrew.medium.heal())


class EventCrewBoosterInfoTooltipData(EventTankRepairInfoTooltipData):

    def _getHeaderBlock(self):
        return formatters.packTextBlockData(text=text_styles.highTitle(backport.text(R.strings.event.tooltip.vehicle.booster.header())))

    def _getDescriptionFormatter(self, descriptionIndex, style):
        return formatters.packTextBlockData(text=style(backport.text(R.strings.event.tooltip.vehicle.booster.dyn('description{}'.format(descriptionIndex))())))

    def _getIcon(self):
        return backport.image(R.images.gui.maps.icons.event.manageCrew.medium.booster())


class EventCommanderInBattle(BlocksTooltipData, IGlobalListener):
    _gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, context):
        super(EventCommanderInBattle, self).__init__(context, TOOLTIP_TYPE.QUESTS)

    def _packBlocks(self, vehTypeCompactDesc, **kwargs):
        vehicle = self.context.buildItem(vehTypeCompactDesc, **kwargs)
        items = super(EventCommanderInBattle, self)._packBlocks()
        header = backport.text(R.strings.tooltips.event.commander.canNotUse.inBattle.title())
        text = backport.text(R.strings.tooltips.event.commander.canNotUse.inBattle.description(), name=vehicle.shortUserName)
        items.append(formatters.packTextBlockData(text=text_styles.statusAlert(header)))
        items.append(formatters.packTextBlockData(text=text_styles.standard(text)))
        return items


class EventCreditsErrorTooltipData(BlocksTooltipData, IGlobalListener):
    _gameEventController = dependency.descriptor(IGameEventController)
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, context):
        super(EventCreditsErrorTooltipData, self).__init__(context, TOOLTIP_TYPE.QUESTS)

    def _packBlocks(self, needValue, **kwargs):
        self.config = self._gameEventController.getVehiclesController()
        items = super(EventCreditsErrorTooltipData, self)._packBlocks()
        header = backport.text(R.strings.tooltips.vehicleStatus.notEnoughCredits.header())
        text = backport.text(R.strings.tooltips.vehicleStatus.notEnoughCredits.text())
        needFormatted = text_styles.credits(needValue)
        neededText = text_styles.concatStylesToSingleLine(text_styles.error(backport.text(R.strings.storage.blueprints.card.convertRequired())), ' ', needFormatted, ' ', icons.credits())
        items.append(formatters.packTextBlockData(text=text_styles.highTitle(header)))
        items.append(formatters.packTextBlockData(text=neededText))
        items.append(formatters.packTextBlockData(text=text_styles.standard(text)))
        return items


class EventTokenErrorTooltipData(BlocksTooltipData, IGlobalListener):
    _gameEventController = dependency.descriptor(IGameEventController)
    itemsCache = dependency.descriptor(IItemsCache)
    _TOKEN_SIZE = 12
    _TOKEN_VSPACE = -1

    def __init__(self, context):
        super(EventTokenErrorTooltipData, self).__init__(context, None)
        self._setMargins(afterBlock=0, afterSeparator=0)
        return

    def _packBlocks(self, needValue, **kwargs):
        self.config = self._gameEventController.getVehiclesController()
        items = super(EventTokenErrorTooltipData, self)._packBlocks()
        header = backport.text(R.strings.event.tradeStyles.notEnoughTokensHeader())
        text = backport.text(R.strings.event.tradeStyles.notEnoughTokensBody())
        items.append(formatters.packTextBlockData(text=text_styles.eventNotEnoughtTokens(header) + '\n' + text_styles.standard(text)))
        return items


class EventGoldErrorTooltipData(BlocksTooltipData, IGlobalListener):
    _gameEventController = dependency.descriptor(IGameEventController)
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, context):
        super(EventGoldErrorTooltipData, self).__init__(context, None)
        self._setMargins(afterBlock=0, afterSeparator=0)
        return

    def _packBlocks(self, needValue, **kwargs):
        self.config = self._gameEventController.getVehiclesController()
        items = super(EventGoldErrorTooltipData, self)._packBlocks()
        header = backport.text(R.strings.event.tradeStyles.notEnoughGoldHeader())
        needFormatted = text_styles.gold(needValue)
        neededText = text_styles.concatStylesToSingleLine(needFormatted, ' ', icons.gold())
        text = backport.text(R.strings.event.tradeStyles.notEnoughGoldBody(), money=neededText)
        items.append(formatters.packTextBlockData(text=text_styles.highTitle(header)))
        items.append(formatters.packTextBlockData(text=text_styles.standard(text)))
        return items


class EventBannerInfoTooltipData(BlocksTooltipData, IGlobalListener):
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, context):
        super(EventBannerInfoTooltipData, self).__init__(context, TOOLTIP_TYPE.QUESTS)
        self._setContentMargin(top=1, left=1, right=1)
        self._setMargins(afterBlock=0)
        self._setWidth(300)

    def _packBlocks(self, **kwargs):
        items = super(EventBannerInfoTooltipData, self)._packBlocks()
        items.append(self._getHeaderBlock())
        items.append(self._getFinalBlcokInfo())
        return items

    def _getHeaderBlock(self):
        timeToEnd = self.eventsCache.getEventFinishTimeLeft()
        descTimeToEnd = backport.getTillTimeStringByRClass(timeToEnd, R.strings.tooltips.battleTypes.event)
        return formatters.packImageTextBlockData(title=text_styles.highTitle(backport.text(R.strings.tooltips.battleTypes.event.header())), img=RES_ICONS.MAPS_ICONS_EVENT_EVENTBANNERHEADER, txtPadding=formatters.packPadding(top=10), txtOffset=10, desc=descTimeToEnd)

    def _getFinalBlcokInfo(self):
        return formatters.packTextBlockData(text=text_styles.main(backport.text(R.strings.tooltips.battleTypes.event.body())), padding=formatters.packPadding(left=10, right=10))


class EventVehicleInfoTooltipData(VehicleInfoTooltipData, IGlobalListener):

    def _getCrewIconBlock(self):
        tImg = RES_ICONS.MAPS_ICONS_MESSENGER_ICONCONTACTS
        return [formatters.packImageBlockData(img=tImg, alpha=0)]

    def _getHeaderBlockConstructorDescr(self):
        return EventHeaderBlockConstructor

    def _getStatusBlockConstructorDescr(self):
        return EventStatusBlockConstructor


class EventHeaderBlockConstructor(HeaderBlockConstructor):

    def construct(self):
        block = []
        headerBlocks = []
        if self.vehicle.isElite:
            bgLinkage = BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_ELITE_VEHICLE_BG_LINKAGE
        else:
            bgLinkage = BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_NORMAL_VEHICLE_BG_LINKAGE
        nameStr = text_styles.highTitle(self.vehicle.userName)
        typeStr = text_styles.main(backport.text(R.strings.event.vehicleTooltip.header.vehicleType.event.dyn(self.vehicle.type)()))
        levelStr = text_styles.concatStylesWithSpace(text_styles.stats(int2roman(self.vehicle.level)), text_styles.standard(_ms(TOOLTIPS.VEHICLE_LEVEL)))
        icon = getTypeBigIconPath(self.vehicle.type, self.vehicle.isElite)
        headerBlocks.append(formatters.packImageTextBlockData(title=nameStr, desc=text_styles.concatStylesToMultiLine(levelStr + ' ' + typeStr, ''), img=icon, imgPadding=formatters.packPadding(left=10, top=-15), txtGap=-9, txtOffset=99, padding=formatters.packPadding(top=15, bottom=-15 if self.vehicle.isFavorite else -21)))
        isEventPremium = VEHICLE_TAGS.EVENT_PREMIUM_VEHICLE in self.vehicle.tags
        if isEventPremium:
            description = backport.text(R.strings.event.vehicleTooltip.header.doubleXP())
            headerBlocks.append(formatters.packImageTextBlockData(desc=text_styles.main(description), img=RES_ICONS.MAPS_ICONS_EVENT_CAROUSELEX2, imgPadding=formatters.packPadding(left=50, top=4), txtGap=-9, txtOffset=99))
        block.append(formatters.packBuildUpBlockData(headerBlocks, stretchBg=False, linkage=bgLinkage, padding=formatters.packPadding(left=-self.leftPadding)))
        return block


class EventStatusBlockConstructor(StatusBlockConstructor):
    _gameEventController = dependency.descriptor(IGameEventController)

    def construct(self):
        if not self._gameEventController.getVehiclesController().hasEnergy(HE19EnergyPurposes.healing.name, self.vehicle.intCD):
            block = []
            header = text_styles.critical(backport.text(R.strings.event.vehicleTooltip.vehicleIsBroken()))
            block.append(formatters.packAlignedTextBlockData(header, BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER))
            return (block, False)
        return super(EventStatusBlockConstructor, self).construct()


class EventCommandersInfoTooltipData(BlocksTooltipData, IGlobalListener):
    _gameEventController = dependency.descriptor(IGameEventController)
    _eventsCache = dependency.descriptor(IEventsCache)
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, context):
        self.vehicle = None
        super(EventCommandersInfoTooltipData, self).__init__(context, TOOLTIP_TYPE.QUESTS)
        self._setWidth(400)
        return

    def _packBlocks(self, vehicleId, timeLeft, isEventPremium, **kwargs):
        self.vehicle = self.context.buildItem(vehicleId, **kwargs)
        items = super(EventCommandersInfoTooltipData, self)._packBlocks()
        items.append(self._getHeaderBlock(vehicleId, isEventPremium, timeLeft))
        items.append(self._getDescriptionBlockInfo(self._gameEventController.getCommander(vehicleId)))
        items.append(self._getEndingInfoBlockBonusToken())
        return items

    def _getHeaderBlock(self, vehicleId, isEventPremium, timeLeft):
        blocks = []
        blocks.append(formatters.packTextBlockData(text=text_styles.highTitle(backport.text(R.strings.tooltips.event.commanders.header()).format(self.vehicle.userName))))
        if isEventPremium:
            blocks.append(formatters.packGlowTextBlockData(text=text_styles.purpleText(backport.text(R.strings.tooltips.event.commanders.premium())), color=5657586))
        if timeLeft:
            blocks.append(formatters.packTextBlockData(text=text_styles.main(backport.text(R.strings.tooltips.event.healing.description())), padding=formatters.packPadding(top=-2)))
            blocks.append(formatters.packGlowTextBlockData(text=text_styles.vehicleStatusCriticalTextSmall(timeLeft), strength=4))
        commanderIcon = self._gameEventController.getVehicleSettings().getTankManIcon(vehicleId)
        blocks.append(formatters.packImageBlockData(img=commanderIcon, width=162, height=175, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(left=-5)))
        progressIcon = backport.image(R.images.gui.maps.icons.event.tooltips.tokenProgress())
        blocks.append(formatters.packImageBlockData(img=progressIcon, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(top=-65, right=5)))
        blocks.append(formatters.packTextBlockData(text=text_styles.main(makeHtmlString('html_templates:lobby/tooltips', 'event_commander_description1')), padding=formatters.packPadding(top=-5)))
        return formatters.packBuildUpBlockData(blocks, padding=formatters.packPadding(bottom=-4))

    def _getDescriptionBlockInfo(self, commander):
        blocks = []
        infinityIcon = backport.image(R.images.gui.maps.icons.event.tooltips.infinity())
        blocks.append(formatters.packImageBlockData(img=infinityIcon, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(top=-8, bottom=3, left=-3)))
        icon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_EVENT_TOKEN_HE19_MONEY, width=13, height=13, vSpace=-2)
        coins = 0
        item = commander.getMaxProgressItem()
        if item:
            coins = item.getCoinsReward()
        blocks.append(formatters.packTextWithBgBlockData(text=text_styles.main(backport.text(R.strings.tooltips.event.commanders.description2(), coins=text_styles.coinsText(str(coins)), icon=icon))))
        return formatters.packBuildUpBlockData(blocks, padding=formatters.packPadding(bottom=-6), linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)

    def _getEndingInfoBlockBonusToken(self):
        finishTime = self._eventsCache.getEventFinishTime()
        date = backport.getShortDateFormat(finishTime)
        times = backport.getShortTimeFormat(finishTime)
        return formatters.packTextBlockData(text=text_styles.main(backport.text(R.strings.tooltips.event.commanders.footer()).format(date, times)))


class EventMissionInfoTooltipData(BlocksTooltipData, IGlobalListener):
    _gameEventController = dependency.descriptor(IGameEventController)
    itemsCache = dependency.descriptor(IItemsCache)
    _BLOCK_WIDTH = 300

    def __init__(self, context):
        self.vehicle = None
        super(EventMissionInfoTooltipData, self).__init__(context, TOOLTIP_TYPE.QUESTS)
        self._setWidth(self._BLOCK_WIDTH)
        return

    def _packBlocks(self, header, icon, totalProgress, currentProgress, rewards, status, **kwargs):
        items = super(EventMissionInfoTooltipData, self)._packBlocks()
        blocks = []
        blocks.append(self._getIconBlock(icon))
        blocks.append(self._getTitleBlock(header))
        blocks.append(self._getProgressBlock(currentProgress, totalProgress))
        blocks.append(self._packRewards(rewards))
        items.append(formatters.packBuildUpBlockData(blocks, padding=formatters.packPadding(left=0, top=15, bottom=0), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER))
        items.append(self._getFinalBlockInfo(status))
        return items

    def _getIconBlock(self, missionIcon):
        return formatters.packBuildUpBlockData([formatters.packImageBlockData(img=missionIcon, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER)])

    def _getTitleBlock(self, descr):
        return formatters.packAlignedTextBlockData(text_styles.highTitle(descr), BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER)

    def _getProgressBlock(self, currentProgress, totalProgress):
        progress = ''
        if totalProgress > 0:
            progress = text_styles.concatStylesToSingleLine(text_styles.goldTextNormalCard(int(currentProgress)), text_styles.highTitle(' / '), text_styles.highTitle(int(totalProgress)))
        return formatters.packAlignedTextBlockData(progress, BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER)

    def _getDescriptionBlockInfo(self, descr):
        return formatters.packAlignedTextBlockData(text_styles.highTitle(descr), BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER)

    def _packRewards(self, rewards):
        return formatters.packBuildUpBlockData([ self.__packSingleReward(reward) for reward in rewards ], layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_HORIZONTAL, padding=formatters.packPadding(left=20, right=20, top=15), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER)

    def __packSingleReward(self, reward):
        iconBlock = formatters.packImageBlockData(img=reward.icon, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER)
        textBlock = formatters.packAlignedTextBlockData(text=reward.label, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(top=5))
        return formatters.packBuildUpBlockData(blocks=[iconBlock, textBlock], blockWidth=72, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(top=-8, bottom=-6))

    def _getFinalBlockInfo(self, status):
        return formatters.packAlignedTextBlockData(text_styles.stats(status), BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER)


class EventSelectorWarningTooltip(BlocksTooltipData):

    def __init__(self, context):
        super(EventSelectorWarningTooltip, self).__init__(context, None)
        self._setWidth(width=400)
        return

    def _packBlocks(self, *args, **kwargs):
        items = super(EventSelectorWarningTooltip, self)._packBlocks(*args, **kwargs)
        items.append(self._getHeaderBlock())
        items.append(self._getInfoBlock())
        return items

    def _getHeaderBlock(self):
        return formatters.packBuildUpBlockData([formatters.packTextBlockData(text=text_styles.middleTitle(backport.text(R.strings.tooltips.battleTypes.event.header()))), formatters.packTextBlockData(text=text_styles.main(backport.text(R.strings.tooltips.battleTypes.event.body())))])

    def _getInfoBlock(self):
        return formatters.packTextBlockData(text=text_styles.concatStylesWithSpace(icons.info(), text_styles.stats(backport.text(R.strings.tooltips.battleTypes.event.description()))))


class EventBanInfoToolTipData(BlocksTooltipData):
    _WIDTH = 400

    def __init__(self, context):
        super(EventBanInfoToolTipData, self).__init__(context, TOOLTIP_TYPE.QUESTS)
        self._setWidth(self._WIDTH)

    def _packBlocks(self, banExpiryTime, **kwargs):
        items = super(EventBanInfoToolTipData, self)._packBlocks(banExpiryTime, **kwargs)
        self._item = self.context.buildItem(banExpiryTime, **kwargs)
        items.append(self._packHeader())
        items.append(self._packDescription())
        items.append(self._packExpiration(banExpiryTime))
        return items

    def _packHeader(self):
        return formatters.packTitleDescBlock(title=text_styles.middleTitle(backport.text(R.strings.tooltips.event.lobby.ban.header())), desc=text_styles.main(makeHtmlString('html_templates:lobby/tooltips/eventBanTooltip/', 'header')))

    def _packDescription(self):
        return formatters.packTitleDescBlock(title=text_styles.middleTitle(backport.text(R.strings.tooltips.event.lobby.ban.quest())), desc=text_styles.main(makeHtmlString('html_templates:lobby/tooltips/eventBanTooltip/', 'quest')), blocksLinkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)

    def _packExpiration(self, banExpiryTime):
        return formatters.packAlignedTextBlockData(text=text_styles.main(backport.text(R.strings.tooltips.event.lobby.ban.expiration(), value=formatTimeAndDate(banExpiryTime))), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(top=-1, bottom=-6))


class HalloweenQuestsPreviewTooltipData(QuestsPreviewTooltipData):

    def _getQuestList(self, vehicle):
        return sorted([ q for q in self._questController.getQuestForVehicle(vehicle) if (isHalloween(q.getGroupID()) or isHalloweenAFK(q.getGroupID())) and q.isAvailable()[0] and not q.isCompleted() ], key=events_helpers.questsSortFunc)

    def _getHeader(self, count, vehicleName, description):
        return formatters.packImageTextBlockData(title=text_styles.highTitle(backport.text(R.strings.tooltips.hangar.header.halloween.quests.header(), count=count)), img=backport.image(R.images.gui.maps.icons.event.quests.questHalloweenTooltipHeader()), txtPadding=formatters.packPadding(top=20), txtOffset=20, desc=text_styles.main(backport.text(description, vehicle=vehicleName)))

    def _getAllQuestsCompleteBlock(self):
        newDayUTC = getTodayStartingTimeUTC()
        localtime = getTimeStructInLocal(newDayUTC)
        return formatters.packBuildUpBlockData([formatters.packTextBlockData(text=text_styles.main(backport.text(R.strings.tooltips.event.header.quests.empty(), hour=time.strftime('%H', localtime), min=time.strftime('%M', localtime))), padding=formatters.packPadding(left=20, top=-10, bottom=10))], linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)


class HalloweenTokenBonusesInfoTooltipData(BlocksTooltipData):
    _WIDTH = 360
    _eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, context):
        super(HalloweenTokenBonusesInfoTooltipData, self).__init__(context, None)
        self._setWidth(width=self._WIDTH)
        return

    def _packBlocks(self, styleID, tokenID, *args, **kwargs):
        items = []
        rTextToken = R.strings.tooltips.quests.bonuses.token
        rImgToken = R.images.gui.maps.icons.event.tokens
        header = backport.text(rTextToken.header.dyn(styleID)())
        description = backport.text(rTextToken.body.dyn(styleID)())
        image = backport.image(rImgToken.c_180x135.dyn(styleID)())
        items.append(formatters.packImageTextBlockData(img=image, title=text_styles.highTitle(header), desc=text_styles.main(description), descPadding=formatters.packPadding(top=157), imgPadding=formatters.packPadding(left=72, top=40), txtOffset=1, txtGap=-1))
        count = self._eventsCache.questsProgress.getTokenCount(tokenID)
        valuePainted = text_styles.highlightText(count) if count > 0 else text_styles.statsDecrease(count)
        items.append(formatters.packBuildUpBlockData([formatters.packTitleDescParameterWithIconBlockData(value=valuePainted, icon=backport.image(rImgToken.c_36x36.dyn(styleID)()), title=text_styles.main(backport.text(R.strings.tooltips.header.buttons.available())), padding=formatters.packPadding(left=105), valuePadding=formatters.packPadding(bottom=4), iconPadding=formatters.packPadding(top=-8, left=4), titlePadding=formatters.packPadding(left=5, bottom=2))], linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding=formatters.packPadding(bottom=-11)))
        items.append(formatters.packTextBlockData('', padding=formatters.packPadding(bottom=-20)))
        return items


class EventTokenInfoTooltipData(BlocksTooltipData):
    _gameEventController = dependency.descriptor(IGameEventController)
    itemsCache = dependency.descriptor(IItemsCache)
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, context):
        super(EventTokenInfoTooltipData, self).__init__(context, TOOLTIP_TYPE.QUESTS)
        self._setWidth(320)

    def _packBlocks(self, tokenID, styleID, **kwargs):
        self.config = self._gameEventController.getVehiclesController()
        items = super(EventTokenInfoTooltipData, self)._packBlocks()
        items.append(self._getHeaderBlock(styleID))
        items.append(self._getDescriptionBlockInfo(styleID))
        return items

    def _getHeaderBlock(self, styleID):
        return formatters.packTextBlockData(text=text_styles.highTitle(backport.text(R.strings.tooltips.quests.bonuses.token.header.dyn(styleID)())))

    def _getDescriptionBlockInfo(self, styleID):
        return formatters.packBuildUpBlockData([self._getIconBlockInfo(styleID), self._getDescriptionFormatter(styleID, text_styles.main)], gap=10, padding=formatters.packPadding(top=10))

    def _getDescriptionFormatter(self, styleID, style):
        date = backport.getShortDateFormat(self.eventsCache.getEventFinishTime())
        return formatters.packTextBlockData(text=style(backport.text(R.strings.tooltips.quests.bonuses.token.description.dyn(styleID)(), date=date)))

    def _getIconBlockInfo(self, styleID):
        return formatters.packImageBlockData(img=backport.image(R.images.gui.maps.icons.quests.bonuses.event.dyn(styleID)()), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER)


class EventNoSuitableVehicleForQuest(ToolTipBaseData):
    _questController = dependency.descriptor(IQuestsController)
    _DEFAULT_LEVELS = (1, 10)

    def __init__(self, context):
        super(EventNoSuitableVehicleForQuest, self).__init__(context, TOOLTIP_TYPE.QUESTS)

    def getDisplayableData(self, *args, **kwargs):
        headerText = backport.text(R.strings.tooltips.hangar.header.halloween.noVehicle.header())
        levelMin, levelMax = self._getLevels()
        bodyText = backport.text(R.strings.tooltips.hangar.header.halloween.noVehicle.body(), min=int2roman(levelMin), max=int2roman(levelMax))
        return {'header': headerText,
         'body': bodyText}

    def _getLevels(self):
        quests = [ q for q in self._questController.getAllAvailableQuests() if (isHalloweenAFK(q.getGroupID()) or isHalloween(q.getGroupID())) and not q.isCompleted() and q.isAvailable()[0] ]
        levelList = set()
        for q in quests:
            vehicleDescr = q.vehicleReqs.getConditions().find('vehicleDescr')
            if vehicleDescr:
                _, _, level, _, _ = vehicleDescr.getParsedConditions()
                if level is not None:
                    levelList |= level

        return self._DEFAULT_LEVELS if not levelList else (min(levelList), max(levelList))
