# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/personal_missions.py
from shared_utils import first, findFirst
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.daapi.view.lobby.missions import missions_helper
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import TooltipOperationAwardComposer
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.genConsts.ICON_TEXT_FRAMES import ICON_TEXT_FRAMES
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.PERSONAL_MISSIONS import PERSONAL_MISSIONS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.server_events import events_helpers
from gui.server_events.awards_formatters import AWARDS_SIZES, CompletionTokensBonusFormatter
from gui.server_events.cond_formatters.tooltips import PMTooltipConditionsFormatters
from gui.shared.formatters import text_styles, icons
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER, getTypeSmallIconPath
from gui.shared.tooltips import TOOLTIP_TYPE, formatters
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.utils import getPlayerName
from helpers import dependency
from helpers.i18n import makeString as _ms
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache

class UniqueCamouflageTooltip(BlocksTooltipData):

    def __init__(self, context):
        super(UniqueCamouflageTooltip, self).__init__(context, TOOLTIP_TYPE.PRIVATE_QUESTS)
        self._setContentMargin(top=20, left=20, bottom=20, right=20)
        self._setMargins(afterBlock=14)
        self._setWidth(330)

    def _packBlocks(self, *args, **kwargs):
        blocks = super(UniqueCamouflageTooltip, self)._packBlocks(*args, **kwargs)
        blocks.append(formatters.packTextBlockData(text_styles.main('UniqueCamouflageTooltip')))
        return blocks


class BasicFreeSheetTooltip(BlocksTooltipData):

    def __init__(self, context):
        super(BasicFreeSheetTooltip, self).__init__(context, TOOLTIP_TYPE.PRIVATE_QUESTS)
        self._setContentMargin(top=20, left=20, bottom=20, right=20)
        self._setMargins(afterBlock=16)
        self._setWidth(394)

    def _packBlocks(self):
        blocks = super(BasicFreeSheetTooltip, self)._packBlocks()
        topItems = [formatters.packTextBlockData(text_styles.highTitle(TOOLTIPS.PERSONALMISSIONS_FREESHEET_TITLE)), formatters.packImageBlockData(RES_ICONS.MAPS_ICONS_PERSONALMISSIONS_FREE_SHEET_BIG, BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(top=-5, bottom=11))]
        blocks.append(formatters.packBuildUpBlockData(topItems))
        infoBlock = self._getInfoBlock()
        if infoBlock is not None:
            blocks.append(infoBlock)
        bottomItems = []
        for block in self._getDescriptionBlock():
            if block is not None:
                bottomItems.append(block)

        blocks.append(formatters.packBuildUpBlockData(bottomItems))
        return blocks

    def _getInfoBlock(self):
        return None

    def _getDescriptionBlock(self):
        return []


class FreeSheetTooltip(BasicFreeSheetTooltip):

    def _getDescriptionBlock(self):
        return (self._getMainBlock(), self._getFooterBlock())

    def _getMainBlock(self):
        return formatters.packBuildUpBlockData([formatters.packTextBlockData(text_styles.middleTitle(TOOLTIPS.PERSONALMISSIONS_FREESHEET_HOWTOGET_TITLE), padding=formatters.packPadding(bottom=-2)), formatters.packTextBlockData(text_styles.main(TOOLTIPS.PERSONALMISSIONS_FREESHEET_HOWTOGET_DESCR))], padding=formatters.packPadding(top=-4))

    def _getFooterBlock(self):
        return formatters.packBuildUpBlockData([formatters.packTextBlockData(text_styles.middleTitle(TOOLTIPS.PERSONALMISSIONS_FREESHEET_HOWTOUSE_TITLE), padding=formatters.packPadding(bottom=-2)), formatters.packTextBlockData(text_styles.main(TOOLTIPS.PERSONALMISSIONS_FREESHEET_HOWTOUSE_DESCR))], padding=formatters.packPadding(top=16))


class FreeSheetReturnTooltip(FreeSheetTooltip):

    def _getInfoBlock(self):
        return formatters.packBuildUpBlockData([formatters.packTextParameterWithIconBlockData(text_styles.neutral(TOOLTIPS.PERSONALMISSIONS_FREESHEET_INFO), '', ICON_TEXT_FRAMES.ATTENTION, padding=formatters.packPadding(left=-60, bottom=-2))], linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding=formatters.packPadding(top=-7, bottom=-3))


class FreeSheetNotEnoughTooltip(FreeSheetTooltip):

    def _getInfoBlock(self):
        return formatters.packBuildUpBlockData([formatters.packTextParameterWithIconBlockData(text_styles.alert(TOOLTIPS.PERSONALMISSIONS_FREESHEET_NOTENOUGH), '', ICON_TEXT_FRAMES.ALERT, padding=formatters.packPadding(left=-60, bottom=-2))], linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding=formatters.packPadding(top=-7, bottom=-3))

    def _getFooterBlock(self):
        return None


class FreeSheetUsedTooltip(BasicFreeSheetTooltip):

    def _getDescriptionBlock(self):
        return (formatters.packBuildUpBlockData([formatters.packTextParameterWithIconBlockData(text_styles.concatStylesToMultiLine(text_styles.middleTitle(TOOLTIPS.PERSONALMISSIONS_FREESHEET_USED_HEADER), text_styles.main(TOOLTIPS.PERSONALMISSIONS_FREESHEET_USED_TEXT)), '', ICON_TEXT_FRAMES.LOCK, padding=formatters.packPadding(left=-60, bottom=-2))]),)


class BadgeTooltipData(BlocksTooltipData):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, context):
        super(BadgeTooltipData, self).__init__(context, TOOLTIP_TYPE.PRIVATE_QUESTS)
        self._setContentMargin(top=20, left=20, bottom=20, right=20)
        self._setMargins(afterBlock=16)
        self._setWidth(364)

    def _packBlocks(self, badgeID):
        blocks = super(BadgeTooltipData, self)._packBlocks()
        badge = self.__itemsCache.items.getBadges()[badgeID]
        tooltipData = [formatters.packTextBlockData(text_styles.highTitle(badge.getUserName())), formatters.packImageBlockData(badge.getHugeIcon(), BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(top=-5, bottom=11))]
        if g_currentVehicle.isPresent():
            vehicle = g_currentVehicle.item
            tooltipData.append(formatters.packBadgeInfoBlockData(badge.getThumbnailIcon(), vehicle.iconContour, text_styles.bonusPreviewText(getPlayerName()), text_styles.bonusPreviewText(vehicle.shortUserName)))
        blocks.append(formatters.packBuildUpBlockData(tooltipData))
        blocks.append(formatters.packTextBlockData(text_styles.main(TOOLTIPS.PERSONALMISSIONS_BADGE_DESCR)))
        return blocks


def _formatCompleteCount(completedQuestsCount, totalCount):
    return text_styles.bonusAppliedText(completedQuestsCount) if completedQuestsCount == totalCount else text_styles.stats(completedQuestsCount)


class OperationTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(OperationTooltipData, self).__init__(context, TOOLTIP_TYPE.PRIVATE_QUESTS)
        self._setContentMargin(top=2, left=2, bottom=3, right=1)
        self._setMargins(afterBlock=0)
        self._setWidth(369)

    def _packBlocks(self, *args, **kwargs):
        items = super(OperationTooltipData, self)._packBlocks()
        operation = self.context.buildItem(*args, **kwargs)
        items.append(self._getTitleBlock(operation))
        items.append(self._getMissionsBlock(operation))
        formatter = TooltipOperationAwardComposer()
        bonuses = formatter.getFormattedBonuses(operation, size=AWARDS_SIZES.BIG, gap=5)
        if bonuses:
            items.append(self._getAwardsBlock(bonuses, operation))
        items.append(self._getStatusBlock(operation))
        return items

    @classmethod
    def _getTitleBlock(cls, operation):
        return formatters.packImageTextBlockData(title=text_styles.highTitle(_ms(TOOLTIPS.PERSONALMISSIONS_OPERATION_TITLE, name=operation.getShortUserName())), img=RES_ICONS.getPersonalMissionOperationTile(operation.getIconID()), txtPadding=formatters.packPadding(top=20), txtOffset=17)

    @classmethod
    def _getMissionsBlock(cls, operation):
        items = []
        completedQuests = operation.getCompletedQuests()
        completedQuestsIDs = set(completedQuests.keys())
        totalCount = operation.getQuestsCount()
        items.append(formatters.packTextBlockData(text=text_styles.concatStylesWithSpace(text_styles.middleTitle(TOOLTIPS.PERSONALMISSIONS_OPERATION_MISSIONS_TITLE), _formatCompleteCount(len(completedQuests), totalCount), text_styles.standard('/ %s' % totalCount)), padding=formatters.packPadding(top=8, left=17)))
        for vehicleType in VEHICLE_TYPES_ORDER:
            _, quests = operation.getChainByVehicleType(vehicleType)
            completedCount = len(completedQuestsIDs.intersection(quests.keys()))
            chainSize = operation.getChainSize()
            items.append(formatters.packTitleDescParameterWithIconBlockData(title=text_styles.concatStylesWithSpace(_formatCompleteCount(completedCount, chainSize), text_styles.standard('/ %s' % chainSize)), value=text_styles.main(MENU.classesShort(vehicleType)), icon=getTypeSmallIconPath(vehicleType), iconPadding=formatters.packPadding(top=3, left=10), titlePadding=formatters.packPadding(left=10), padding=formatters.packPadding(left=156, bottom=-9)))

        return formatters.packBuildUpBlockData(blocks=items, padding=formatters.packPadding(top=-14, bottom=30), gap=10)

    @classmethod
    def _getAwardsBlock(cls, bonuses, operation):
        items = []
        text = TOOLTIPS.PERSONALMISSIONS_OPERATION_AWARDS_TITLE_DONE
        if operation.isAwardAchieved():
            text = TOOLTIPS.PERSONALMISSIONS_OPERATION_AWARDS_TITLE_EXCELLENTDONE
        items.append(formatters.packTextBlockData(text=text_styles.middleTitle(text), padding=formatters.packPadding(top=8, left=7)))
        items.append(formatters.packAwardsExBlockData(bonuses, columnWidth=90, rowHeight=80, horizontalGap=10, renderersAlign=formatters.RENDERERS_ALIGN_CENTER, padding=formatters.packPadding(top=10, bottom=18, left=10)))
        return formatters.packBuildUpBlockData(blocks=items, stretchBg=False, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WIDE_AWARD_BIG_BG_LINKAGE, padding=formatters.packPadding(top=-16, left=10, bottom=10), gap=10)

    def _getStatusBlock(self, operation):
        if not operation.isUnlocked():
            block = formatters.packBuildUpBlockData([formatters.packAlignedTextBlockData(text=text_styles.concatStylesWithSpace(icons.markerBlocked(-2), text_styles.error(TOOLTIPS.PERSONALMISSIONS_OPERATION_FOOTER_TITLE_NOTAVAILABLE)), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(top=-5)), formatters.packAlignedTextBlockData(text=text_styles.main(TOOLTIPS.PERSONALMISSIONS_OPERATION_FOOTER_DESCR_DOPREVOPERATION), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(bottom=14))])
        elif operation.isFullCompleted():
            block = formatters.packAlignedTextBlockData(text=text_styles.concatStylesWithSpace(icons.doubleCheckmark(1), text_styles.bonusAppliedText(TOOLTIPS.PERSONALMISSIONS_OPERATION_FOOTER_TITLE_EXCELLENTDONE)), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(top=-5, bottom=12))
        elif operation.isAwardAchieved():
            data = [formatters.packAlignedTextBlockData(text=text_styles.concatStylesWithSpace(icons.checkmark(-2), text_styles.bonusAppliedText(TOOLTIPS.PERSONALMISSIONS_OPERATION_FOOTER_TITLE_DONE)), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(top=-5))]
            currentCount = operation.getFreeTokensCount()
            totalCount = operation.getFreeTokensTotalCount()
            if currentCount < totalCount:
                data.append(formatters.packAlignedTextBlockData(text=text_styles.concatStylesToSingleLine(text_styles.main(TOOLTIPS.PERSONALMISSIONS_OPERATION_FOOTER_DESCR_FREESHEETS), missions_helper.AWARD_SHEET_ICON, text_styles.bonusAppliedText(currentCount), text_styles.main(' / %s' % totalCount)), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(bottom=14)))
            else:
                currentCount = len(operation.getFullCompletedQuests(True))
                totalCount = operation.getQuestsCount()
                data.append(formatters.packAlignedTextBlockData(text=text_styles.concatStylesToSingleLine(text_styles.main(TOOLTIPS.PERSONALMISSIONS_OPERATION_FOOTER_DESCR_QUESTSFULLYDONE), text_styles.bonusAppliedText(currentCount), text_styles.main(' / %s' % totalCount)), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(bottom=14)))
            block = formatters.packBuildUpBlockData(data)
        elif operation.isInProgress():
            currentCount, totalCount = operation.getTokensCount()
            block = formatters.packBuildUpBlockData([formatters.packAlignedTextBlockData(text=text_styles.concatStylesWithSpace(icons.inProgress(-1), text_styles.neutral(TOOLTIPS.PERSONALMISSIONS_OPERATION_FOOTER_TITLE_INPROGRESS)), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(top=-5)), formatters.packAlignedTextBlockData(text=text_styles.concatStylesToSingleLine(text_styles.main(TOOLTIPS.PERSONALMISSIONS_OPERATION_FOOTER_DESCR_COMPLETIONTOKENS), text_styles.bonusAppliedText(currentCount), text_styles.main(' / %s' % totalCount)), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(bottom=14))])
        elif not operation.hasRequiredVehicles():
            block = formatters.packBuildUpBlockData([formatters.packAlignedTextBlockData(text=text_styles.concatStylesWithSpace(icons.markerBlocked(-2), text_styles.error(TOOLTIPS.PERSONALMISSIONS_OPERATION_FOOTER_TITLE_NOTAVAILABLE)), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(top=-5)), formatters.packAlignedTextBlockData(text=text_styles.main(TOOLTIPS.PERSONALMISSIONS_OPERATION_FOOTER_DESCR_NOVEHICLE), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(bottom=14))])
        else:
            block = formatters.packBuildUpBlockData([formatters.packAlignedTextBlockData(text=text_styles.stats(TOOLTIPS.PERSONALMISSIONS_OPERATION_FOOTER_TITLE_AVAILABLE), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(top=-5)), formatters.packAlignedTextBlockData(text=text_styles.main(TOOLTIPS.PERSONALMISSIONS_OPERATION_FOOTER_DESCR_SELECTQUEST), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(bottom=14))])
        return block


class PersonalMissionInfoTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(PersonalMissionInfoTooltipData, self).__init__(context, TOOLTIP_TYPE.PRIVATE_QUESTS)
        self._setContentMargin(top=20, left=20, bottom=20, right=20)
        self._setWidth(364)

    def _packBlocks(self, *args, **kwargs):
        eventID = args[0]
        quest = events_helpers.getPersonalMissionsCache().getQuests()[int(eventID)]
        description = '\n\n'.join([quest.getUserDescription(), quest.getUserAdvice()])
        blocks = [formatters.packTextBlockData(text_styles.concatStylesToMultiLine(text_styles.highTitle(PERSONAL_MISSIONS.DETAILEDVIEW_INFOPANEL_HEADER), text_styles.main(description)))]
        return blocks


class PersonalMissionsMapRegionTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(PersonalMissionsMapRegionTooltipData, self).__init__(context, TOOLTIP_TYPE.PRIVATE_QUESTS)
        self._setContentMargin(left=2)
        self._setMargins(afterBlock=0)
        self._setWidth(369)
        self._hasOrCondition = False
        self.quest = None
        return

    def _getPersonalMission(self, *args, **kwargs):
        return self.context.buildItem(*args, **kwargs)

    def _packBlocks(self, *args, **kwargs):
        items = super(PersonalMissionsMapRegionTooltipData, self)._packBlocks()
        self.quest = self._getPersonalMission(*args, **kwargs)
        if self.quest:
            isMain = None
            if not self.quest.isMainCompleted():
                isMain = True
            conditions = PMTooltipConditionsFormatters().format(self.quest, isMain)
            orConditions = [ q for q in conditions if q.isInOrGroup ]
            andConditions = [ q for q in conditions if not q.isInOrGroup ]
            self._hasOrCondition = bool(orConditions)
            blocksData = []
            blocksData.append(self._getTitleBlock())
            blocksData.append(self._getConditionsTitleBlock())
            if not self._hasOrCondition:
                blocksData.append(self._getAndConditionsBlock(andConditions, padding=formatters.packPadding(bottom=22)))
                items.append(formatters.packBuildUpBlockData(blocksData))
            else:
                items.append(formatters.packBuildUpBlockData(blocksData))
                items.append(self._getOrConditionBlock(orConditions))
                if andConditions:
                    items.append(self._getAndConditionsBlock(andConditions, padding=formatters.packPadding(top=-13, bottom=22)))
            items.append(self._getAwardsBlock(self.quest))
            items.append(self._getStatusBlock(self.quest))
        return items

    def _getTitleBlock(self, padding=None):
        padding = padding or {}
        padding['top'] = 10
        padding['left'] = 17
        return formatters.packTextBlockData(text=text_styles.highTitle(self.quest.getUserName()), padding=padding)

    def _getConditionsTitleBlock(self):
        padding = {}
        if self._hasOrCondition:
            padding['bottom'] = 10
        if not self.quest.isMainCompleted():
            titleKey = TOOLTIPS.PERSONALMISSIONS_MAPREGION_CONDITIONS_TITLE
        else:
            titleKey = TOOLTIPS.PERSONALMISSIONS_MAPREGION_CONDITIONS_TITLE_EXCELLENT
        padding['top'] = 10
        padding['left'] = 17
        return formatters.packTextBlockData(text=text_styles.middleTitle(titleKey), padding=padding)

    @classmethod
    def _getAndConditionsBlock(cls, conditions, padding):
        items = []
        for c in conditions:
            items.append(formatters.packImageTextBlockData(title=c.title, img=c.icon, txtPadding=formatters.packPadding(left=-21), imgPadding=formatters.packPadding(top=-34), padding=formatters.packPadding(top=10, left=30), ignoreImageSize=True))

        return formatters.packBuildUpBlockData(blocks=items, padding=padding, gap=13)

    @classmethod
    def _getOrConditionBlock(cls, conditions):
        items = []
        conditionsCount = len(conditions)
        for idx, c in enumerate(conditions, start=1):
            items.append(formatters.packImageTextBlockData(title=c.title, img=c.icon, txtPadding=formatters.packPadding(left=-21), imgPadding=formatters.packPadding(top=-34), padding=formatters.packPadding(left=30), ignoreImageSize=True))
            if idx < conditionsCount:
                items.append(formatters.packTextBlockData(text=text_styles.neutral(TOOLTIPS.VEHICLE_TEXTDELIMITER_OR), padding=formatters.packPadding(top=-7, bottom=-11, left=99)))

        return formatters.packBuildUpBlockData(blocks=items, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding=formatters.packPadding(top=-6, bottom=15), gap=13)

    @classmethod
    def _getAwardsBlock(cls, quest):
        items = []
        linkage = BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WIDE_AWARD_BIG_BG_LINKAGE
        textPadding = formatters.packPadding(top=-8, left=16, bottom=20)
        if quest.isDone():
            titleKey = TOOLTIPS.PERSONALMISSIONS_MAPREGION_AWARDS_TITLE_ALLRECEIVED
            linkage = BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WIDE_AWARD_SMALL_BG_LINKAGE
            textPadding['bottom'] = 10
        elif not quest.isMainCompleted():
            titleKey = TOOLTIPS.PERSONALMISSIONS_MAPREGION_AWARDS_TITLE_DONE
        else:
            titleKey = TOOLTIPS.PERSONALMISSIONS_MAPREGION_AWARDS_TITLE_EXCELLENTDONE
        items.append(formatters.packTextBlockData(text=text_styles.middleTitle(titleKey), padding=textPadding))
        if not quest.isDone():
            bonuses = missions_helper.getPersonalMissionAwardsFormatter().getFormattedBonuses(quest.getBonuses(isMain=not quest.isMainCompleted()), size=AWARDS_SIZES.BIG)
            items.append(formatters.packAwardsExBlockData(bonuses, columnWidth=90, rowHeight=80, horizontalGap=10, renderersAlign=formatters.RENDERERS_ALIGN_CENTER, padding=formatters.packPadding(bottom=20, left=10)))
        return formatters.packBuildUpBlockData(blocks=items, stretchBg=False, linkage=linkage)

    @classmethod
    def _getStatusBlock(cls, quest):
        isAvailable, reason = quest.isAvailable()
        if not isAvailable:
            if reason == 'noVehicle':
                key = TOOLTIPS.PERSONALMISSIONS_MAPREGION_FOOTER_TITLE_NOVEHICLE
            else:
                key = TOOLTIPS.PERSONALMISSIONS_MAPREGION_FOOTER_TITLE_NOTAVAILABLE
            text = text_styles.concatStylesWithSpace(icons.markerBlocked(-2), text_styles.error(key))
        elif quest.isInProgress():
            if quest.areTokensPawned():
                label = _ms(TOOLTIPS.PERSONALMISSIONS_MAPREGION_FOOTER_TITLE_SHEETRECOVERYINPROGRESS, icon=missions_helper.AWARD_SHEET_ICON, count=quest.getPawnCost())
                text = text_styles.concatStylesWithSpace(icons.inProgress(-1), text_styles.neutral(label))
            else:
                text = text_styles.concatStylesWithSpace(icons.inProgress(-1), text_styles.neutral(TOOLTIPS.PERSONALMISSIONS_MAPREGION_FOOTER_TITLE_INPROGRESS))
        elif quest.isCompleted():
            if quest.areTokensPawned():
                text = text_styles.concatStylesWithSpace(icons.checkmark(-2), text_styles.bonusAppliedText(TOOLTIPS.PERSONALMISSIONS_MAPREGION_FOOTER_TITLE_DONEFREESHEET), missions_helper.AWARD_SHEET_ICON, text_styles.stats('x%s' % quest.getPawnCost()))
            else:
                text = text_styles.concatStylesWithSpace(icons.checkmark(-2), text_styles.bonusAppliedText(TOOLTIPS.PERSONALMISSIONS_MAPREGION_FOOTER_TITLE_DONE))
        else:
            text = text_styles.main(TOOLTIPS.PERSONALMISSIONS_MAPREGION_FOOTER_TITLE_AVAILABLE)
        return formatters.packAlignedTextBlockData(text=text, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(top=-5, bottom=-5))


class PersonalMissionPreviewTooltipData(PersonalMissionsMapRegionTooltipData):

    def _getPersonalMission(self, *args, **kwargs):
        vehicle = g_currentVehicle.item
        vehicleLvl = vehicle.level
        vehicleType = vehicle.type
        for operation in self.context.eventsCache.personalMissions.getOperations().itervalues():
            if not operation.isUnlocked():
                continue
            for chainID, chain in operation.getQuests().iteritems():
                if operation.getChainVehicleClass(chainID) != vehicleType:
                    continue
                for quest in chain.itervalues():
                    if vehicleLvl < quest.getVehMinLevel():
                        continue
                    if quest.isInProgress():
                        return quest

        return None


class TankwomanTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(TankwomanTooltipData, self).__init__(context, TOOLTIP_TYPE.PRIVATE_QUESTS)
        self._setContentMargin(top=20, left=20, bottom=20, right=20)
        self._setWidth(364)

    def _packBlocks(self, *args, **kwargs):
        blocks = [formatters.packImageTextBlockData(title=text_styles.highTitle(PERSONAL_MISSIONS.TANKWOMANTOOLTIPDATA_TITLE), desc=text_styles.standard(PERSONAL_MISSIONS.TANKWOMANTOOLTIPDATA_SUBTITLE), img=RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_BIG_TANKWOMAN), formatters.packBuildUpBlockData([formatters.packTextBlockData(text_styles.middleTitle(PERSONAL_MISSIONS.TANKWOMANTOOLTIPDATA_DESC_TITLE), padding=formatters.packPadding(bottom=4)), formatters.packTextBlockData(text_styles.main(PERSONAL_MISSIONS.TANKWOMANTOOLTIPDATA_DESC_BODY), padding=formatters.packPadding(bottom=7))], linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding=formatters.packPadding(top=-7, bottom=-3)), formatters.packBuildUpBlockData([formatters.packTextBlockData(text_styles.middleTitle(PERSONAL_MISSIONS.TANKWOMANTOOLTIPDATA_ADVANTAGES_TITLE), padding=formatters.packPadding(bottom=20)),
          self.__makeImageBlock(RES_ICONS.MAPS_ICONS_PERSONALMISSIONS_MAIN_100, PERSONAL_MISSIONS.TANKWOMANTOOLTIPDATA_ADVANTAGES_NATION, 4, 16, 10),
          self.__makeImageBlock('../maps/icons/tankmen/skills/big/new_skill.png', PERSONAL_MISSIONS.TANKWOMANTOOLTIPDATA_ADVANTAGES_NEWPERK),
          self.__makeImageBlock('../maps/icons/tankmen/skills/big/brotherhood.png', PERSONAL_MISSIONS.TANKWOMANTOOLTIPDATA_ADVANTAGES_BROTHERHOOD)])]
        return blocks

    def __makeImageBlock(self, icon, text, imgPaddingLeft=15, imgPaddingRight=30, imgPaddingTop=0):
        return formatters.packImageTextBlockData(title=text_styles.main(text), desc='', img=icon, imgPadding=formatters.packPadding(left=imgPaddingLeft, right=imgPaddingRight, top=imgPaddingTop), padding=formatters.packPadding(bottom=20))


class TankModuleTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(TankModuleTooltipData, self).__init__(context, TOOLTIP_TYPE.PRIVATE_QUESTS)
        self._setContentMargin(top=20, left=20, bottom=20, right=20)
        self._setWidth(336)

    def _packBlocks(self, operationID, vehicleType):
        pmController = dependency.instance(IEventsCache).personalMissions
        operation = pmController.getOperations()[operationID]
        chainID, _ = operation.getChainByVehicleType(vehicleType)
        finalQuest = operation.getFinalQuests()[chainID]
        bonus = findFirst(lambda q: q.getName() == 'completionTokens', finalQuest.getBonuses('tokens'))
        formattedBonus = first(CompletionTokensBonusFormatter().format(bonus))
        operationTitle = str(operation.getVehicleBonus().userName).replace(' ', '&nbsp;')
        if finalQuest.isCompleted():
            statusText = self.__getObtainedStatus()
        elif pmController.mayPawnQuest(finalQuest):
            statusText = self.__getAvailableStatus(finalQuest.getPawnCost())
        else:
            statusText = self.__getNotObtainedStatus()
        vehIcon = RES_ICONS.vehicleTypeInactiveOutline(vehicleType)
        blocks = [formatters.packImageTextBlockData(title=text_styles.highTitle(formattedBonus.userName), desc=text_styles.standard(_ms(PERSONAL_MISSIONS.OPERATIONTITLE_TITLE, title=operationTitle)), img=formattedBonus.getImage(AWARDS_SIZES.BIG), imgPadding=formatters.packPadding(right=20), txtPadding=formatters.packPadding(top=10)), formatters.packBuildUpBlockData([formatters.packImageTextBlockData(title=text_styles.main(_ms(PERSONAL_MISSIONS.TANKMODULETOOLTIPDATA_INFO, vehName=text_styles.neutral(operationTitle))), img=RES_ICONS.MAPS_ICONS_LIBRARY_ATTENTIONICONFILLED, imgPadding=formatters.packPadding(left=8, right=10, top=2))], linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding=formatters.packPadding(top=-7, bottom=-3))]
        if not finalQuest.isCompleted():
            blocks.append(formatters.packBuildUpBlockData([formatters.packTextBlockData(text_styles.middleTitle(PERSONAL_MISSIONS.TANKMODULETOOLTIPDATA_HELP_TITLE), padding=formatters.packPadding(bottom=4)), formatters.packImageTextBlockData(title=text_styles.main(_ms(PERSONAL_MISSIONS.TANKMODULETOOLTIPDATA_HELP_BODY, vehType=_ms(PERSONAL_MISSIONS.chainNameByVehicleType(vehicleType)))), img=vehIcon, imgPadding=formatters.packPadding(right=2))]))
        blocks.append(formatters.packAlignedTextBlockData(text=statusText, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER))
        return blocks

    def __getObtainedStatus(self):
        return text_styles.concatStylesWithSpace(icons.checkmark(-2), text_styles.statInfo(PERSONAL_MISSIONS.TANKMODULETOOLTIPDATA_STATUS_OBTAINED))

    def __getNotObtainedStatus(self):
        return text_styles.critical(PERSONAL_MISSIONS.TANKMODULETOOLTIPDATA_STATUS_NOTOBTAINED)

    def __getAvailableStatus(self, pawnsCount):
        return text_styles.warning(_ms(PERSONAL_MISSIONS.TANKMODULETOOLTIPDATA_STATUS_AVAILABLE, count=pawnsCount, img=icons.makeImageTag(RES_ICONS.MAPS_ICONS_PERSONALMISSIONS_FREE_SHEET, 24, 24, -6, 0)))
