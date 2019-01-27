# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattle/epic_prestige_progress_tooltip.py
from gui.Scaleform.daapi.view.lobby.epicBattle.epic_prestige_progress import FRONTLINE_PRESTIGE_TOKEN_TEMPLATE
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared.formatters import text_styles
from gui.shared.tooltips import TOOLTIP_TYPE, formatters
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.tooltips.vehicle import HeaderBlockConstructor, TelecomBlockConstructor, CommonStatsBlockConstructor, FootnoteBlockConstructor, AdditionalStatsBlockConstructor
from helpers import dependency, i18n, int2roman
from skeletons.gui.game_control import IEpicBattleMetaGameController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext
_TOOLTIP_MIN_WIDTH = 280
_TOOLTIP_MAX_WIDTH = 460
_REWARD_SPECIAL_ALIAS_TAG = 'specialAlias'
_REWARD_SPECIAL_AWARD_VEHICLE_TAG = 'awardVehicle'
_REWARD_SPECIAL_ARGUMENTS_TAG = 'specialArgs'

class EpicPrestigeProgressTooltip(BlocksTooltipData):
    epicMetaGameCtrl = dependency.descriptor(IEpicBattleMetaGameController)
    eventsCache = dependency.descriptor(IEventsCache)
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyCtx = dependency.descriptor(ILobbyContext)

    def __init__(self, ctx):
        super(EpicPrestigeProgressTooltip, self).__init__(ctx, TOOLTIP_TYPE.EPIC_PRESTIGE_PROGRESS_BLOCK_INFO)
        self._setContentMargin(top=0, left=0, bottom=20, right=0)

    def _packVehicleBlock(self, vehicleIntCD):
        vehicle = self.itemsCache.items.getItemByCD(int(vehicleIntCD))
        statsConfig = self.context.getStatsConfiguration(vehicle)
        paramsConfig = self.context.getParamsConfiguration(vehicle)
        leftPadding = 20
        rightPadding = 20
        blockTopPadding = -4
        leftRightPadding = formatters.packPadding(left=leftPadding, right=rightPadding)
        blockPadding = formatters.packPadding(left=leftPadding, right=rightPadding, top=blockTopPadding)
        valueWidth = 75
        textGap = -2
        vehicleBlock = list()
        vehicleBlock.append(formatters.packBuildUpBlockData(HeaderBlockConstructor(vehicle, statsConfig, leftPadding, rightPadding).construct(), padding=leftRightPadding))
        telecomBlock = TelecomBlockConstructor(vehicle, valueWidth, leftPadding, rightPadding).construct()
        if telecomBlock:
            vehicleBlock.append(formatters.packBuildUpBlockData(telecomBlock))
        if not vehicle.isRotationGroupLocked:
            commonStatsBlock = CommonStatsBlockConstructor(vehicle, paramsConfig, valueWidth, leftPadding, rightPadding).construct()
            if commonStatsBlock:
                vehicleBlock.append(formatters.packBuildUpBlockData(commonStatsBlock, gap=textGap, padding=blockPadding))
        footnoteBlock = FootnoteBlockConstructor(vehicle, paramsConfig, leftPadding, rightPadding).construct()
        if footnoteBlock:
            vehicleBlock.append(formatters.packBuildUpBlockData(footnoteBlock, gap=textGap, padding=blockPadding))
        vehicleBlock.append(formatters.packBuildUpBlockData(AdditionalStatsBlockConstructor(vehicle, paramsConfig, self.context.getParams(), valueWidth, leftPadding, rightPadding).construct(), gap=textGap, padding=blockPadding))
        return vehicleBlock

    def _packRegularAwardBlock(self, bonus):
        return formatters.packRendererTextBlockData(rendererType='AwardItemExUI', dataType='net.wg.gui.data.AwardItemVO', title=text_styles.main(bonus['title']), rendererData={'imgSource': bonus['imgSource'],
         'label': bonus['label']}, padding=formatters.packPadding(top=0, left=20, bottom=0, right=20), txtPadding=formatters.packPadding(top=15, left=5))

    def _packAwardsReceivedFootnoteBlock(self, alreadyReachedPrestigeLevel):
        if alreadyReachedPrestigeLevel:
            rewardBlockText = formatters.packImageTextBlockData(title=text_styles.statInfo(i18n.makeString(EPIC_BATTLE.PRESTIGEPROGRESS_TOOLTIP_AWARDRECEIVED)), img=RES_ICONS.MAPS_ICONS_BUTTONS_CHECKMARK, imgPadding=formatters.packPadding(left=2, top=3), padding=formatters.packPadding(top=0, left=20, bottom=0, right=20))
        else:
            rewardBlockText = formatters.packTextBlockData(text_styles.warning(i18n.makeString(EPIC_BATTLE.PRESTIGEPROGRESS_TOOLTIP_AWARDNOTYETCLAIMED)), padding=formatters.packPadding(top=0, left=20, bottom=0, right=20))
        return rewardBlockText

    def _packBlocks(self, *args):
        items = super(EpicPrestigeProgressTooltip, self)._packBlocks()
        prestigeOver = args[0]
        if prestigeOver == 0:
            return
        else:
            maxMetaLevel = self.lobbyCtx.getServerSettings().epicMetaGame.metaLevel.get('maxLevel', 0)
            quests = self.eventsCache.getAllQuests()
            currentPrestigeQuest = quests.get(FRONTLINE_PRESTIGE_TOKEN_TEMPLATE % (prestigeOver - 1), None)
            awardsVO = []
            if currentPrestigeQuest:
                bonuses = currentPrestigeQuest.getBonuses()
                awardsVO = sum([ bonus.getEpicAwardVOs(withDescription=True, iconSize='small', withCounts=True) for bonus in bonuses ], [])
            regularAwardBlocks = []
            vehicleAwardBlocks = []
            for bonus in awardsVO:
                specialAlias = bonus.get(_REWARD_SPECIAL_ALIAS_TAG, None)
                if specialAlias and specialAlias == _REWARD_SPECIAL_AWARD_VEHICLE_TAG:
                    specialArgs = bonus.get(_REWARD_SPECIAL_ARGUMENTS_TAG)
                    if specialArgs:
                        vehicleAwardBlocks = self._packVehicleBlock(specialArgs[0])
                regularAwardBlocks.append(self._packRegularAwardBlock(bonus))

            _, maxRewardClaimed = self.epicMetaGameCtrl.getSeasonData()
            pPrestigeLevel, pMetaLevel, _ = self.epicMetaGameCtrl.getPlayerLevelInfo()
            alreadyReceivedAwards = prestigeOver <= pPrestigeLevel + 1 or maxRewardClaimed
            desc = ''
            if pPrestigeLevel + 1 == prestigeOver and pMetaLevel == maxMetaLevel and not maxRewardClaimed:
                if vehicleAwardBlocks:
                    desc = text_styles.alert(EPIC_BATTLE.PRESTIGEPROGRESS_TOOLTIP_DESC_CLAIMFINALREWARD)
                else:
                    desc = text_styles.alert(i18n.makeString(EPIC_BATTLE.PRESTIGEPROGRESS_TOOLTIP_DESC_CLAIMREWARD))
            elif not alreadyReceivedAwards:
                if vehicleAwardBlocks:
                    desc = text_styles.standard(EPIC_BATTLE.PRESTIGEPROGRESS_TOOLTIP_DESC_REACHFINALMAXLEVEL)
                else:
                    desc = text_styles.standard(i18n.makeString(EPIC_BATTLE.PRESTIGEPROGRESS_TOOLTIP_DESC_REACHMAXLEVEL))
            if vehicleAwardBlocks:
                self._setWidth(_TOOLTIP_MAX_WIDTH)
                items.append(formatters.packTitleDescBlock(title=text_styles.highTitle(EPIC_BATTLE.PRESTIGEPROGRESS_TOOLTIP_TITLEFINAL), desc=desc, padding=formatters.packPadding(top=20, left=20, bottom=0, right=20)))
                items.extend(vehicleAwardBlocks)
                if regularAwardBlocks:
                    items.extend(regularAwardBlocks)
            else:
                self._setWidth(_TOOLTIP_MIN_WIDTH)
                items.append(formatters.packTitleDescBlock(title=text_styles.highTitle(i18n.makeString(EPIC_BATTLE.PRESTIGEPROGRESS_TOOLTIP_TITLE, prestigeLevel=int2roman(args[0] + 1))), desc=desc, padding=formatters.packPadding(top=20, left=20, bottom=0, right=20)))
                if regularAwardBlocks:
                    items.extend(regularAwardBlocks)
            items.append(self._packAwardsReceivedFootnoteBlock(alreadyReceivedAwards))
            return items
