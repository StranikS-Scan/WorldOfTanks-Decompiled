# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/event.py
from constants import EPIC_PERF_GROUP
from gui import makeHtmlString
from gui.Scaleform.daapi.view.lobby.event_boards.formaters import formatTimeAndDate
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.impl import backport
from gui.impl.backport.backport_tooltip import DecoratedTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.secret_event.general_tooltip_model import GeneralTooltipModel
from gui.impl.lobby.secret_event import EnergyMixin
from gui.impl.lobby.secret_event.general_info_tip import GeneralInfoTip
from gui.server_events.awards_formatters import TokenBonusFormatter
from gui.server_events.events_helpers import isSecretEvent, isPremium, isDailyQuest
from gui.server_events.formatters import parseComplexToken
from gui.shared.formatters import text_styles, icons
from gui.shared.gui_items.Vehicle import getTypeBigIconPath
from gui.shared.tooltips import formatters, TOOLTIP_TYPE, ToolTipBaseData
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.tooltips.quests import QuestsPreviewTooltipData
from gui.shared.tooltips.vehicle import VehicleInfoTooltipData, HeaderBlockConstructor
from helpers import dependency, int2roman
from helpers.time_utils import getTillTimeString
from items import vehicles
from shared_utils import first
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IEpicBattleMetaGameController
from skeletons.gui.game_control import IEventProgressionController
from skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.server_events import IEventsCache

class EventSelectorWarningTooltip(BlocksTooltipData):
    settingsCore = dependency.descriptor(ISettingsCore)
    eventCache = dependency.descriptor(IGameEventController)
    epicBattleMetaGameController = dependency.descriptor(IEpicBattleMetaGameController)

    def __init__(self, context):
        super(EventSelectorWarningTooltip, self).__init__(context, None)
        self._setContentMargin(top=17, left=18, bottom=20, right=20)
        self._setMargins(afterBlock=20)
        self._setWidth(width=367)
        return

    def _packBlocks(self, *args, **kwargs):
        items = super(EventSelectorWarningTooltip, self)._packBlocks(*args, **kwargs)
        items.append(self.__packHeaderBlock())
        if self.eventCache.isEnabled():
            items.append(self.__getPerformanceWarningText())
        else:
            block = formatters.packTitleDescBlock(title=text_styles.concatStylesWithSpace(icons.alert(), text_styles.alert(backport.text(R.strings.event.selectorTooltip.possibleLowPerformance.title()))), desc=text_styles.main(backport.text(R.strings.event.selectorTooltip.possibleLowPerformance.description())), padding=formatters.packPadding(top=15))
            items.append(block)
        return items

    def __packHeaderBlock(self):
        return formatters.packTitleDescBlock(title=text_styles.highTitle(backport.text(R.strings.event.selectorTooltip.header())), desc=text_styles.main(backport.text(R.strings.event.selectorTooltip.description())), gap=1, padding=formatters.packPadding(bottom=-6))

    def __getPerformanceWarningText(self):
        performanceGroup = self.epicBattleMetaGameController.getPerformanceGroup()
        if performanceGroup == EPIC_PERF_GROUP.HIGH_RISK:
            block = formatters.packTitleDescBlock(title=text_styles.concatStylesWithSpace(icons.markerBlocked(), text_styles.error(backport.text(R.strings.event.selectorTooltip.assuredLowPerformance.title()))), desc=text_styles.main(backport.text(R.strings.event.selectorTooltip.assuredLowPerformance.description())), padding=formatters.packPadding(top=15))
        elif performanceGroup == EPIC_PERF_GROUP.MEDIUM_RISK:
            block = formatters.packTitleDescBlock(title=text_styles.concatStylesWithSpace(icons.alert(), text_styles.alert(backport.text(R.strings.event.selectorTooltip.possibleLowPerformance.title()))), desc=text_styles.main(backport.text(R.strings.event.selectorTooltip.possibleLowPerformance.description())), padding=formatters.packPadding(top=15))
        else:
            block = formatters.packTextBlockData(text=text_styles.concatStylesWithSpace(icons.info(), text_styles.main(backport.text(R.strings.event.selectorTooltip.informativeLowPerformance.description()))), padding=formatters.packPadding(top=15))
        return block


class SecretEventGeneralIInfoData(BlocksTooltipData):
    _WIDTH = 400
    gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, context):
        super(SecretEventGeneralIInfoData, self).__init__(context, TOOLTIP_TYPE.EVENT)
        self._setWidth(self._WIDTH)

    def _packBlocks(self, *args, **kwargs):
        items = super(SecretEventGeneralIInfoData, self)._packBlocks()
        endDate = self.gameEventController.getEventFinishTime()
        dateFormatted = formatTimeAndDate(endDate)
        datePainted = text_styles.neutral(dateFormatted)
        items.append(formatters.packTextBlockData(text=text_styles.main(makeHtmlString('html_templates:lobby/tooltips/event', 'herotank_title', {'date': datePainted}))))
        return items


class SecretEventSquadTooltipData(BlocksTooltipData):
    _WIDTH = 350

    def __init__(self, context):
        super(SecretEventSquadTooltipData, self).__init__(context, TOOLTIP_TYPE.EVENT)
        self._setWidth(self._WIDTH)

    def _packBlocks(self, *args, **kwargs):
        items = super(SecretEventSquadTooltipData, self)._packBlocks()
        items.append(self._getRoadToBerlin())
        items.append(self._getBerlin())
        items.append(self._getInfo())
        return items

    def _getRoadToBerlin(self):
        return formatters.packTextBlockData(text=text_styles.main(makeHtmlString('html_templates:lobby/tooltips/squad_window', 'roadToBerlin')))

    def _getBerlin(self):
        return formatters.packTextBlockData(text=text_styles.main(makeHtmlString('html_templates:lobby/tooltips/squad_window', 'Berlin')))

    def _getInfo(self):
        return formatters.packTextBlockData(text=text_styles.main(makeHtmlString('html_templates:lobby/tooltips/squad_window', 'PlayInfo')))


class SecretEventSubdivisionPumpingTooltipData(BlocksTooltipData):
    _WIDTH = 350

    def __init__(self, context):
        super(SecretEventSubdivisionPumpingTooltipData, self).__init__(context, TOOLTIP_TYPE.EVENT)
        self._setWidth(self._WIDTH)

    def _packBlocks(self, *args, **kwargs):
        items = super(SecretEventSubdivisionPumpingTooltipData, self)._packBlocks()
        items.append(formatters.packTextBlockData(text=text_styles.main(makeHtmlString('html_templates:lobby/tooltips/event/subdivision_pumping', 'header'))))
        items.append(formatters.packTextBlockData(text=text_styles.main(makeHtmlString('html_templates:lobby/tooltips/event/subdivision_pumping', 'middle'))))
        items.append(formatters.packTextBlockData(text=text_styles.main(makeHtmlString('html_templates:lobby/tooltips/event/subdivision_pumping', 'footer'))))
        return items


class SecretEventSquadGeneralInfo(BlocksTooltipData):
    _WIDTH = 362

    def __init__(self, context):
        super(SecretEventSquadGeneralInfo, self).__init__(context, TOOLTIP_TYPE.EVENT)
        self._setWidth(self._WIDTH)

    def _constructHeader(self):
        header = []
        header.append(formatters.packTextBlockData(text_styles.highTitle(backport.text(R.strings.event.menu.subdivision()))))
        header.append(formatters.packImageBlockData(backport.image(R.images.gui.maps.icons.secretEvent.infotipTanks()), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(top=28, left=5, bottom=35)))
        header.append(formatters.packTextBlockData(text_styles.main(makeHtmlString('html_templates:lobby/tooltips/event/squad_general_info', 'header'))))
        return header

    def _constructBody(self):
        body = []
        body.append(formatters.packTextBlockData(text_styles.middleTitle(backport.text(R.strings.tooltips.secret_event.squadInfo.newLevel()))))
        body.append(formatters.packTextBlockData(text_styles.main(makeHtmlString('html_templates:lobby/tooltips/event/squad_general_info', 'body'))))
        return body

    def _packBlocks(self, *args, **kwargs):
        tooltipBlocks = super(SecretEventSquadGeneralInfo, self)._packBlocks(*args, **kwargs)
        tooltipBlocks.append(formatters.packBuildUpBlockData(self._constructHeader()))
        tooltipBlocks.append(formatters.packBuildUpBlockData(self._constructBody(), linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE))
        tooltipBlocks.append(formatters.packTextBlockData(text_styles.main(makeHtmlString('html_templates:lobby/tooltips/event/squad_general_info', 'footer'))))
        return tooltipBlocks


class SecretEventCommanderReviveSkillTooltipData(BlocksTooltipData):
    _WIDTH = 400
    _COUNT = 3
    _BEFORE_FIRST_USING = 40
    _BEFORE_SECOND_USING = 50
    _BEFORE_THIRD_USING = 60

    def __init__(self, context):
        super(SecretEventCommanderReviveSkillTooltipData, self).__init__(context, TOOLTIP_TYPE.EVENT)
        self._setWidth(self._WIDTH)

    def _constructHeader(self):
        header = []
        icon = backport.image(R.images.gui.maps.icons.secretEvent.abilities.respawn())
        title = backport.text(R.strings.tooltips.secret_event.respawnAbility.title.header())
        passiveAbilityText = backport.text(R.strings.tooltips.secret_event.passiveAbility())
        body = backport.text(R.strings.tooltips.secret_event.respawnAbility.title.body())
        header.append(formatters.packImageTextBlockData(img=icon, title=text_styles.highTitle(title), desc=text_styles.vehicleStatusInfoText(passiveAbilityText), imgPadding=formatters.packPadding(top=-15, left=-25)))
        header.append(formatters.packTextBlockData(text=text_styles.standard(body), padding=formatters.packPadding(left=68, top=-35)))
        return header

    def _constructBody(self):
        onUse = backport.text(R.strings.tooltips.equipment.effect())
        desc = backport.text(R.strings.tooltips.secret_event.respawnAbility.body())
        return formatters.packTitleDescBlock(title=text_styles.highTitle(onUse), desc=text_styles.main(desc), padding=formatters.packPadding(left=70), blocksLinkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)

    def _packParameterBlock(self, name, value, measureUnits):
        return formatters.packTextParameterBlockData(name=text_styles.main(name) + text_styles.standard(measureUnits), value=text_styles.stats(value), valueWidth=180, padding=formatters.packPadding(left=-5))

    def _packBlocks(self, *args, **kwargs):
        tooltipBlocks = super(SecretEventCommanderReviveSkillTooltipData, self)._packBlocks(*args, **kwargs)
        tooltipBlocks.append(formatters.packBuildUpBlockData(self._constructHeader()))
        tooltipBlocks.append(self._constructBody())
        return tooltipBlocks


class SecretEventCommanderSkillTooltipData(BlocksTooltipData):
    _WIDTH = 400
    _LEFT_PADDING_BLOCKS = 50

    def __init__(self, context):
        super(SecretEventCommanderSkillTooltipData, self).__init__(context, TOOLTIP_TYPE.EVENT)
        self._setWidth(self._WIDTH)

    def _packParameterBlock(self, name, value, measureUnits):
        return formatters.packTextParameterBlockData(name=text_styles.main(name) + text_styles.standard(measureUnits), value=text_styles.stats(value), valueWidth=self._LEFT_PADDING_BLOCKS, padding=formatters.packPadding(left=-5))

    def _constructHeader(self, skill):
        header = []
        icon = backport.image(R.images.gui.maps.icons.secretEvent.abilities.c_48x48.dyn(skill.iconName)())
        level = int(skill.name[-1])
        levelStr = backport.text(R.strings.tooltips.vehicleSelector.sorting.vehLvl.header())
        titleText = text_styles.concatStylesToMultiLine(text_styles.highTitle(skill.userString), text_styles.concatStylesWithSpace(text_styles.middleTitle(int2roman(level)), text_styles.tooltipHaveText(levelStr.lower())))
        header.append(formatters.packImageTextBlockData(img=icon, title=titleText, txtPadding=formatters.packPadding(left=8)))
        return header

    def _packBlocks(self, *args, **kwargs):
        tooltipBlocks = super(SecretEventCommanderSkillTooltipData, self)._packBlocks(*args, **kwargs)
        skillID = args[0] if args else None
        skill = vehicles.g_cache.equipments().get(skillID)
        if not skill:
            return tooltipBlocks
        else:
            header = self._constructHeader(skill)
            tooltipBlocks.append(formatters.packBuildUpBlockData(header))
            onUse = backport.text(R.strings.tooltips.equipment.onUse())
            tooltipBlocks.append(formatters.packTitleDescBlock(title=text_styles.middleTitle(onUse), desc=text_styles.main(skill.description), padding=formatters.packPadding(left=56), blocksLinkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE))
            return tooltipBlocks


class SE20BattleQuestBonusFormatter(TokenBonusFormatter):

    def format(self, bonus):
        result = []
        for b in super(SE20BattleQuestBonusFormatter, self).format(bonus):
            name = b.userName
            if b.label:
                name += ' ({})'.format(b.label)
            result.append(name)

        return result

    def _formatBonusLabel(self, count):
        return 'x{}'.format(count)


class SecretQuestsPreviewTooltipData(QuestsPreviewTooltipData):
    _eventProgressionController = dependency.descriptor(IEventProgressionController)
    _bonusFormatter = SE20BattleQuestBonusFormatter

    def _getHeaderImage(self):
        return backport.image(R.images.gui.maps.icons.quests.questSecretEventTooltipHeader())

    def _getTitle(self, count):
        return backport.text(R.strings.tooltips.secret_event.hangar.header.quests.header(), count=count)

    def _getQuests(self):
        return [ q for q in super(SecretQuestsPreviewTooltipData, self)._getQuests() if q.isAvailable()[0] and isSecretEvent(q.getGroupID()) and not isDailyQuest(q.getID()) and not isPremium(q.getID()) and q.getID() not in self._eventProgressionController.questIDs ]


class SecretEventBannerInfoTooltipData(BlocksTooltipData):
    _WIDTH = 400
    gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, context):
        super(SecretEventBannerInfoTooltipData, self).__init__(context, TOOLTIP_TYPE.EVENT)
        self._setWidth(self._WIDTH)

    def _packBlocks(self, *args, **kwargs):
        items = super(SecretEventBannerInfoTooltipData, self)._packBlocks()
        banner = R.strings.tooltips.secret_event.banner
        items.append(formatters.packTextBlockData(text=text_styles.main(makeHtmlString('html_templates:lobby/tooltips/event/banner_info', 'header'))))
        certificates = sum((item.getEnergiesCount() for item in self.gameEventController.getCommanders().itervalues()))
        items.append(formatters.packBuildUpBlockData([formatters.packTitleDescParameterWithIconBlockData(value=text_styles.highlightText(certificates), icon=backport.image(R.images.gui.maps.icons.secretEvent.certificate()), title=text_styles.main(backport.text(banner.have())), padding=formatters.packPadding(left=105), valuePadding=formatters.packPadding(bottom=4), iconPadding=formatters.packPadding(top=-2, left=4), titlePadding=formatters.packPadding(left=5, bottom=2))], linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding=formatters.packPadding(bottom=-7)))
        items.append(formatters.packTextBlockData(text=text_styles.main(makeHtmlString('html_templates:lobby/tooltips/event/banner_info', 'berlin'))))
        isBerlinStarted = self.gameEventController.isBerlinStarted()
        if not isBerlinStarted:
            berlinStartTimeLeft = int(self.gameEventController.getBerlinStartTimeLeft())
            timeLoc = getTillTimeString(berlinStartTimeLeft, TOOLTIPS.SECRET_EVENT_BANNER_TIMELEFT, removeLeadingZeros=True)
            items.append(formatters.packBuildUpBlockData([formatters.packTitleDescParameterWithIconBlockData(value=text_styles.tutorial(timeLoc), icon=backport.image(R.images.gui.maps.icons.library.ClockIcon_1()), title=text_styles.main(backport.text(banner.beforeBerlin())), padding=formatters.packPadding(left=103), valuePadding=formatters.packPadding(), iconPadding=formatters.packPadding(top=-7, right=4), titlePadding=formatters.packPadding(right=4))], linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding=formatters.packPadding(bottom=-19)))
        endDate = self.gameEventController.getEventFinishTime()
        dateFormatted = formatTimeAndDate(endDate)
        datePainted = text_styles.neutral(dateFormatted)
        items.append(formatters.packTextBlockData(text=text_styles.main(backport.text(banner.footer(), date=datePainted))))
        return items


class SecretEventEnergyDiscount(BlocksTooltipData):
    _WIDTH = 360
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, context):
        super(SecretEventEnergyDiscount, self).__init__(context, TOOLTIP_TYPE.EVENT)
        self._setWidth(self._WIDTH)

    def _packBlocks(self, *args, **kwargs):
        items = super(SecretEventEnergyDiscount, self)._packBlocks(*args, **kwargs)
        htmlTemplate = 'html_templates:lobby/tooltips/event/event_discount'
        body = makeHtmlString(htmlTemplate, 'top')
        items.append(formatters.packImageTextBlockData(img=backport.image(R.images.gui.maps.icons.secretEvent.tokens.c_124x124.se20_energy_general_x15_discount()), title=text_styles.highTitle(backport.text(R.strings.tooltips.quests.bonuses.token.header.se20_energy_general_x15_discount())), desc=text_styles.main(body), descPadding=formatters.packPadding(top=160), imgPadding=formatters.packPadding(left=100, top=30), txtOffset=1, txtGap=-1))
        currentCount = 0
        tokenID = first(args)
        if tokenID:
            currentCount = self.eventsCache.questsProgress.getTokenCount(tokenID)
        valuePainted = text_styles.highlightText(currentCount) if currentCount > 0 else text_styles.statsDecrease(currentCount)
        items.append(formatters.packBuildUpBlockData([formatters.packTitleDescParameterWithIconBlockData(value=valuePainted, icon=backport.image(R.images.gui.maps.icons.secretEvent.token()), title=text_styles.main(backport.text(R.strings.tooltips.secret_event.banner.have())), padding=formatters.packPadding(left=105), valuePadding=formatters.packPadding(bottom=4), iconPadding=formatters.packPadding(top=-4, left=4), titlePadding=formatters.packPadding(left=5, bottom=2))], linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding=formatters.packPadding(bottom=-7)))
        items.append(formatters.packTextBlockData(''))
        return items


class _SecretEventBonusInfoConstructor(BlocksTooltipData, EnergyMixin):
    _WIDTH = 360
    gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, context):
        super(_SecretEventBonusInfoConstructor, self).__init__(context, TOOLTIP_TYPE.EVENT)
        self._setWidth(self._WIDTH)

    def _getMainPart(self, items, img, title, body):
        items.append(formatters.packImageTextBlockData(img=img, title=text_styles.highTitle(title), desc=text_styles.main(body), descPadding=formatters.packPadding(top=180), imgPadding=formatters.packPadding(left=65, top=30), txtOffset=1, txtGap=-1))

    def _getDescriptionPart(self, items, currentCount, modifier):
        valuePainted = text_styles.highlightText(currentCount) if currentCount > 0 else text_styles.statsDecrease(currentCount)
        items.append(formatters.packBuildUpBlockData([formatters.packTitleDescParameterWithIconBlockData(value=valuePainted, icon=backport.image(R.images.gui.maps.icons.secretEvent.certificate()), title=text_styles.tooltipHaveText(backport.text(R.strings.tooltips.secret_event.banner.have())), padding=formatters.packPadding(left=105), valuePadding=formatters.packPadding(bottom=4), iconPadding=formatters.packPadding(top=-2, left=4), titlePadding=formatters.packPadding(left=5, bottom=2))], linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding=formatters.packPadding(bottom=-7)))
        howToGet = backport.text(R.strings.tooltips.quests.bonuses.token.howToGet.se_energy())
        htmlTemplate = 'html_templates:lobby/tooltips/event/bonus_info'
        items.append(formatters.packTitleDescBlock(title=text_styles.middleTitle(howToGet), desc=text_styles.main(makeHtmlString(htmlTemplate, 'middlex{}'.format(modifier)))))

    def _getHangarFootagePart(self, items, currentCount, isCurrent):
        if isCurrent:
            items.append(formatters.packAlignedTextBlockData(text=text_styles.statInfo(backport.text(R.strings.tooltips.quests.bonuses.token.se_energy.will_be_applied())), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER))
        elif currentCount > 0:
            items.append(formatters.packAlignedTextBlockData(text=text_styles.statInfo(backport.text(R.strings.tooltips.quests.bonuses.token.se_energy.in_storage())), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER))
        else:
            items.append(formatters.packAlignedTextBlockData(text=text_styles.statusAlert(backport.text(R.strings.tooltips.quests.bonuses.token.se_energy.not_in_storage())), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER))

    def _getPostBattleFottagePart(self, items, pointsDiff, isApplied):
        htmlTemplate = 'html_templates:lobby/tooltips/event/bonus_info'
        pointsInfo = makeHtmlString(htmlTemplate, 'points_footer', ctx={'points': pointsDiff})
        items.append(formatters.packAlignedTextBlockData(text=text_styles.main(pointsInfo), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER))
        if isApplied:
            items.append(formatters.packAlignedTextBlockData(text=text_styles.statInfo(backport.text(R.strings.tooltips.quests.bonuses.token.se_energy.applied())), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER))
        else:
            items.append(formatters.packAlignedTextBlockData(text=text_styles.statusAlert(backport.text(R.strings.tooltips.quests.bonuses.token.se_energy.ended())), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER))

    def _getInfoByID(self, energyID):
        commanderProgress = self.gameEventController.getCommanderByEnergy(energyID)
        energyData = self.getEnergyData(commanderProgress, energyID, forceEnabled=True)
        img = backport.image(energyData.hangarIcon)
        title = backport.text(R.strings.tooltips.quests.bonuses.token.header.dyn(parseComplexToken(energyID).styleID)())
        htmlTemplate = 'html_templates:lobby/tooltips/event/bonus_info'
        body = makeHtmlString(htmlTemplate, 'top', ctx={'modifier': energyData.modifier})
        currentCount = energyData.currentCount
        currentEnergy = commanderProgress.getCurrentEnergy()
        isCurrent = currentEnergy is not None and energyID == currentEnergy.energyID
        return (img,
         title,
         body,
         currentCount,
         energyData.modifier,
         isCurrent)


class SecretEventBonusBasicTooltipData(_SecretEventBonusInfoConstructor):

    def _packBlocks(self, *args, **kwargs):
        items = super(SecretEventBonusBasicTooltipData, self)._packBlocks(*args, **kwargs)
        energyID = args
        img, title, body, currentCount, modifier, _ = self._getInfoByID(energyID)
        self._getMainPart(items, img, title, body)
        self._getDescriptionPart(items, currentCount, modifier)
        return items


class SecretEventBonusHangarData(_SecretEventBonusInfoConstructor):

    def _packBlocks(self, *args, **kwargs):
        items = super(SecretEventBonusHangarData, self)._packBlocks(*args, **kwargs)
        energyID = args
        img, title, body, currentCount, modifier, isCurrent = self._getInfoByID(energyID)
        self._getMainPart(items, img, title, body)
        self._getDescriptionPart(items, currentCount, modifier)
        self._getHangarFootagePart(items, currentCount, isCurrent)
        return items


class SecretEventBonusPostBattleTooltipData(_SecretEventBonusInfoConstructor):

    def _packBlocks(self, *args, **kwargs):
        items = super(SecretEventBonusPostBattleTooltipData, self)._packBlocks(*args, **kwargs)
        energyID, pointsDiff, isApplied = args
        img, title, body, currentCount, modifier, _ = self._getInfoByID(energyID)
        self._getMainPart(items, img, title, body)
        self._getDescriptionPart(items, currentCount, modifier)
        self._getPostBattleFottagePart(items, pointsDiff, isApplied)
        return items


class SecretEventPointsInfoTooltipData(BlocksTooltipData):
    _WIDTH = 360
    gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, context):
        super(SecretEventPointsInfoTooltipData, self).__init__(context, TOOLTIP_TYPE.EVENT)
        self._setWidth(self._WIDTH)

    def _packBlocks(self, *args, **kwargs):
        items = super(SecretEventPointsInfoTooltipData, self)._packBlocks(*args, **kwargs)
        img = backport.image(R.images.gui.maps.icons.secretEvent.tokenIconLarge())
        title = backport.text(R.strings.tooltips.quests.bonuses.token.se20_front_1_event_points.header())
        body = backport.text(R.strings.tooltips.quests.bonuses.token.se20_front_1_event_points.body())
        howToGet = backport.text(R.strings.tooltips.quests.bonuses.token.se20_front_1_event_points.howToGet())
        howToGetVariants = backport.text(R.strings.tooltips.quests.bonuses.token.se20_front_1_event_points.howToGetVariants())
        htmlTemplate = 'html_templates:lobby/tooltips/event'
        additionalInfo = makeHtmlString(htmlTemplate, 'berlin')
        items.append(formatters.packImageTextBlockData(img=img, title=text_styles.highTitle(title), desc=text_styles.main(body), descPadding=formatters.packPadding(top=170), imgPadding=formatters.packPadding(left=98, top=40), txtOffset=1, txtGap=-1))
        items.append(formatters.packTitleDescBlock(title=text_styles.middleTitle(howToGet), desc=text_styles.main(howToGetVariants), blocksLinkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE))
        items.append(formatters.packTextBlockData(text=text_styles.main(additionalInfo)))
        return items


class BattleResultStatTooltipData(BlocksTooltipData):
    _WIDTH = 360

    def __init__(self, context):
        super(BattleResultStatTooltipData, self).__init__(context, TOOLTIP_TYPE.EVENT)
        self._setWidth(self._WIDTH)

    def _packBlocks(self, values=None, descriptions=None):
        items = super(BattleResultStatTooltipData, self)._packBlocks()
        title, body, image = self._getContent()
        items.append(formatters.packImageTextBlockData(makeHtmlString('html_templates:eventResult', 'statsHeader', {'text': backport.text(title)}), img=backport.image(image), txtPadding={'left': 18,
         'top': 9,
         'bottom': 1}, padding={'left': 2,
         'top': 7,
         'bottom': -42}, imgPadding=formatters.packPadding(left=-21, top=-21, right=-21)))
        items.append(formatters.packTextBlockData(makeHtmlString('html_templates:lobby/battle_results', 'tooltip_terms_label', {'text': backport.text(body)})))
        if values is not None and descriptions is not None:
            packer = formatters.packTextParameterBlockData
            blocks = [ packer(value=values[i], name=descriptions[i]) for i in range(0, len(values)) ]
            blockToInsert = formatters.packBuildUpBlockData(blocks)
            items.append(blockToInsert)
        return items

    def _getContent(self):
        pass


class BattleResultKillTooltipData(BattleResultStatTooltipData):

    def _getContent(self):
        tooltipAcc = R.strings.battle_results.common.tooltip
        return (tooltipAcc.kill.header(), tooltipAcc.kill_1.description(), R.images.gui.maps.icons.secretEvent.battleResult.kill())


class BattleResultDamageTooltipData(BattleResultStatTooltipData):

    def _getContent(self):
        damageAcc = R.strings.battle_results.common.tooltip.damage
        return (damageAcc.header(), damageAcc.description(), R.images.gui.maps.icons.secretEvent.battleResult.damage())


class BattleResultAssistTooltipData(BattleResultStatTooltipData):

    def _getContent(self):
        assistAcc = R.strings.battle_results.common.tooltip.assist
        return (assistAcc.header(), assistAcc.description(), R.images.gui.maps.icons.secretEvent.battleResult.assist())


class BattleResultArmorTooltipData(BattleResultStatTooltipData):

    def _getContent(self):
        armorAcc = R.strings.battle_results.common.tooltip.armor
        return (armorAcc.header(), armorAcc.description(), R.images.gui.maps.icons.secretEvent.battleResult.armor())


class BattleResultMissionTooltipData(BlocksTooltipData):
    _WIDTH = 420

    def __init__(self, context):
        super(BattleResultMissionTooltipData, self).__init__(context, TOOLTIP_TYPE.EVENT)
        self._setWidth(self._WIDTH)

    def _packBlocks(self):
        items = super(BattleResultMissionTooltipData, self)._packBlocks()
        objectivesAcc = R.strings.event.resultScreen.tooltip.objectives
        items.append(formatters.packImageTextBlockData(makeHtmlString('html_templates:eventResult', 'missionHeader', {'text': backport.text(objectivesAcc.header())}), makeHtmlString('html_templates:eventResult', 'missionDescr', {'text': backport.text(objectivesAcc.descr())}), img=backport.image(R.images.gui.maps.icons.secretEvent.battleResult.objectives()), txtPadding={'left': 10}, padding={'left': 2,
         'top': 7}))
        return items


class SecretEventProgressionTooltipData(BlocksTooltipData):
    _WIDTH = 360
    gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, context):
        super(SecretEventProgressionTooltipData, self).__init__(context, TOOLTIP_TYPE.EVENT)
        self._setWidth(self._WIDTH)

    def _packBlocks(self, showClickInfo=True):
        items = super(SecretEventProgressionTooltipData, self)._packBlocks()
        progressionInfo = R.strings.tooltips.secret_event.progressionInfo
        img = backport.image(R.images.gui.maps.icons.secretEvent.missions.mission_108x140())
        title = backport.text(progressionInfo.title())
        info = backport.text(progressionInfo.info())
        items.append(formatters.packImageTextBlockData(img=img, title=text_styles.highTitle(title), desc=text_styles.main(makeHtmlString('html_templates:lobby/tooltips/event/mission_info', 'header')), descPadding=formatters.packPadding(top=170), imgPadding=formatters.packPadding(left=98, top=40), txtOffset=1, txtGap=-1))
        items.append(formatters.packTextBlockData(text=text_styles.main(info)))
        if showClickInfo:
            clickInfo = backport.text(progressionInfo.click())
            items.append(formatters.packTextBlockData(text=text_styles.main(clickInfo)))
        return items


class EventHeaderBlockConstructor(HeaderBlockConstructor):

    def construct(self):
        block = []
        headerBlocks = []
        vehicleType = TOOLTIPS.tankcaruseltooltip_vehicletype_normal(self.vehicle.type)
        bgLinkage = BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_NORMAL_VEHICLE_BG_LINKAGE
        nameStr = text_styles.highTitle(self.vehicle.userName)
        typeStr = text_styles.main(vehicleType)
        fullDescription = text_styles.main(self.vehicle.fullDescription)
        icon = getTypeBigIconPath(self.vehicle.type, False)
        headerBlocks.append(formatters.packImageTextBlockData(title=nameStr, desc=text_styles.concatStylesToMultiLine(typeStr, fullDescription, ''), descPadding=formatters.packPadding(top=9), img=icon, imgPadding=formatters.packPadding(left=10, top=-15), txtGap=-9, txtOffset=99, padding=formatters.packPadding(top=15, bottom=-15 if self.vehicle.isFavorite else -21)))
        block.append(formatters.packBuildUpBlockData(headerBlocks, stretchBg=False, linkage=bgLinkage, padding=formatters.packPadding(left=-self.leftPadding)))
        return block


class EventVehicleInfoTooltipData(VehicleInfoTooltipData):
    headerBlockConstructor = EventHeaderBlockConstructor


class EventCommanderCharacteristicsTooltipData(BlocksTooltipData):
    _WIDTH = 340

    def __init__(self, context):
        super(EventCommanderCharacteristicsTooltipData, self).__init__(context, TOOLTIP_TYPE.EVENT)
        self._setWidth(self._WIDTH)

    def _packBlocks(self, charName=None, iconPrefix='', *args, **kwargs):
        blocks = super(EventCommanderCharacteristicsTooltipData, self)._packBlocks(*args, **kwargs)
        characterNameItem = backport.text(R.strings.event.tank_params.dyn(charName)())
        icon = backport.image(R.images.gui.maps.icons.secretEvent.vehParams.dyn(iconPrefix.format(charName))())
        descr = backport.text(R.strings.event.tank_params.desc.dyn(charName)())
        blocks.append(formatters.packImageTextBlockData(title=text_styles.highTitle(characterNameItem), img=icon, imgPadding=formatters.packPadding(top=-15, left=-25), txtPadding=formatters.packPadding(left=-15), desc=text_styles.main(descr)))
        return blocks


class EventResultGeneralContentWindowData(ToolTipBaseData):

    def __init__(self, context):
        super(EventResultGeneralContentWindowData, self).__init__(context, TOOLTIPS_CONSTANTS.EVENT_RESULT_GENERAL)

    def getDisplayableData(self, generalId, *args, **kwargs):
        return DecoratedTooltipWindow(GeneralInfoTip(R.views.lobby.secretEvent.GeneralTooltip(), generalId, GeneralTooltipModel.RESULT), useDecorator=False)
