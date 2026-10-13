# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/battle_result_view.py
from __future__ import absolute_import
import WWISE
from gui.impl import backport
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.impl.lobby.common.tooltips.extended_text_tooltip import ExtendedTextTooltip
from gui.impl.pub import WindowImpl, ToolTipWindow
from gui.server_events.bonuses import getNonQuestBonuses, mergeBonuses, TokensBonus
from gui.server_events.awards_formatters import AWARDS_SIZES
from gui.battle_results.settings import PLAYER_TEAM_RESULT
from gui.impl.gen import R
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.shared.money import Currency
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import DISPLAY_ALL_AWARDS
from halloween.gui.impl.gen.view_models.views.common.base_team_member_model import TeamMemberBanType
from halloween.gui.impl.gen.view_models.views.lobby.battle_result_view_model import BattleResultViewModel
from halloween.gui.impl.gen.view_models.views.lobby.reward_bonus_item_view_model import RewardBonusItemViewModel
from halloween.gui.impl.lobby.hw_helpers.bonuses_formatters import HalloweenBonusesAwardsComposer, getHWBattleResultAwardFormatter, getImgName, formatTokenBonusName
from halloween.gui.impl.lobby.tooltips.key_tooltip import KeyTooltipView
from halloween.gui.impl.lobby.widgets.battle_result_stats import BattleResultStats
from halloween.gui.sounds import playSound
from halloween.gui.sounds.sound_constants import PBS_ENTER, PBS_EXIT, VO, VOObjects, DifficultyState
from halloween.gui.game_control.halloween_artefacts_controller import getBonusPriority
from halloween.skeletons.halloween_artefacts_controller import IHalloweenArtefactsController
from halloween_common.configs.halloween_loot import lootConfigSchema
from halloween_common.halloween_constants import ArtefactsSettings, ARENA_BONUS_TYPE_TO_LEVEL
from ids_generators import SequenceIDGenerator
from halloween.gui.impl.lobby.tooltips.ability_tooltip import AbilityTooltipView
from skeletons.gui.battle_results import IBattleResultsService
from helpers import dependency
from skeletons.gui.game_control import IEventBattlesController
from skeletons.gui.lobby_context import ILobbyContext
from halloween.gui.impl.lobby.base_view import BaseView
from skeletons.account_helpers.settings_core import ISettingsCore
from gui.sounds.ambients import BattleResultsEnv
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
_R_BACKPORT_TOOLTIP = R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent()
_R_KEY_TOOLTIP = R.views.halloween.mono.lobby.tooltips.key_tooltip()
_CURRENCIES = Currency.ALL + ('xp',
 'freeXP',
 'battlePassPoints',
 formatTokenBonusName(ArtefactsSettings.KEY_TOKEN))

class BattleResultView(BaseView):
    __slots__ = ('__arenaUniqueID', '__bonusCache', '__idGen', '__tooltipCtx')
    battleResults = dependency.descriptor(IBattleResultsService)
    lobbyContext = dependency.descriptor(ILobbyContext)
    eventBattlesController = dependency.descriptor(IEventBattlesController)
    settingsCore = dependency.descriptor(ISettingsCore)
    hwArtefactCtrl = dependency.descriptor(IHalloweenArtefactsController)
    eventsCache = dependency.descriptor(IEventsCache)
    itemsCache = dependency.descriptor(IItemsCache)
    _MAX_BONUSES_IN_VIEW = 6
    __sound_env__ = BattleResultsEnv

    def __init__(self, **kwargs):
        settings = ViewSettings(R.views.halloween.mono.lobby.battle_result())
        settings.flags = ViewFlags.VIEW
        settings.model = BattleResultViewModel()
        super(BattleResultView, self).__init__(settings)
        self.__idGen = SequenceIDGenerator()
        self.__bonusCache = {}
        self.__tooltipCtx = {}
        self.__arenaUniqueID = kwargs.get('arenaUniqueId')
        self.__totalVO = self.battleResults.getResultsVO(self.__arenaUniqueID)

    @property
    def viewModel(self):
        return super(BattleResultView, self).getViewModel()

    def createContextMenu(self, event):
        statsView = self.getChildView(R.aliases.halloween.shared.TeamStats())
        return statsView.createContextMenu(event)

    def createToolTip(self, event):
        if event.contentID == _R_BACKPORT_TOOLTIP:
            tooltipId = event.getArgument('tooltipId')
            bonus = self.__bonusCache.get(tooltipId)
            if bonus:
                if bonus.itemTypeName == 'equipment':
                    window = ToolTipWindow(event, AbilityTooltipView(intCD=int(bonus.specialArgs[0]), showPriceBlock=False), self.getParentWindow())
                    window.load()
                    return window
                window = BackportTooltipWindow(createTooltipData(tooltip=bonus.tooltip, isSpecial=bonus.isSpecial, specialAlias=bonus.specialAlias, specialArgs=bonus.specialArgs, isWulfTooltip=bonus.isWulfTooltip), self.getParentWindow(), event=event)
                window.load()
                return window
        return super(BattleResultView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == _R_KEY_TOOLTIP:
            return KeyTooltipView(isPostBattle=True, ctx=self.__tooltipCtx.get(contentID, {}))
        if contentID == R.views.lobby.common.tooltips.ExtendedTextTooltip():
            text = event.getArgument('text', '')
            stringifyKwargs = event.getArgument('stringifyKwargs', '')
            return ExtendedTextTooltip(text, stringifyKwargs)
        return super(BattleResultView, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(BattleResultView, self)._onLoading(*args, **kwargs)
        if self.battleResults.areResultsPosted(self.__arenaUniqueID):
            self.__fillViewModel()
        self.setChildView(resourceID=R.aliases.halloween.shared.TeamStats(), view=BattleResultStats(totalVO=self.__totalVO, arenaUniqueID=self.__arenaUniqueID))

    def _initialize(self, *args, **kwargs):
        super(BattleResultView, self)._initialize(*args, **kwargs)
        playSound(PBS_ENTER)

    def _finalize(self):
        playSound(PBS_EXIT)
        self.__totalVO = None
        super(BattleResultView, self)._finalize()
        return

    def _subscribe(self):
        super(BattleResultView, self)._subscribe()
        self.viewModel.onClose += self._onClose

    def _unsubscribe(self):
        self.viewModel.onClose -= self._onClose
        super(BattleResultView, self)._unsubscribe()

    def __fillViewModel(self):
        totalVO = self.__totalVO
        with self.viewModel.transaction() as model:
            self.__fillCommonInfo(model, totalVO)
            self.__fillPlayerInfo(model.playerInfo, totalVO)
            self.__fillRewardsInfo(model.getRewards(), totalVO)
            self.__playVoiceover(totalVO)

    def __fillCommonInfo(self, model, totalVO):
        commonVO = totalVO['common']
        model.setIsBossDefeated(commonVO['resultShortStr'] == PLAYER_TEAM_RESULT.WIN)
        model.battleInfo.setStartDate(commonVO['arenaCreateTimeStr'])
        model.battleInfo.setDuration(commonVO['duration'])
        difficulty = ARENA_BONUS_TYPE_TO_LEVEL[commonVO['bonusType']]
        model.setDifficultyLevel(difficulty)
        model.setCurrentPhase(totalVO['hwPhase'])

    def __fillPlayerInfo(self, playerInfo, totalVO):
        playersVO = totalVO['players']
        personalVO = next((player for player in playersVO if player['isPlayer']), None)
        playerInfo.user.setUserName(personalVO['playerName'])
        playerInfo.user.setClanAbbrev(personalVO['clanAbbrev'])
        playerInfo.vehicle.setVehicleName(personalVO['vehicleName'])
        playerInfo.vehicle.setVehicleType(personalVO['vehicleType'])
        vehicleItem = self.itemsCache.items.getItemByCD(personalVO['vehicleCD'])
        playerInfo.vehicle.setVehicleIconName(vehicleItem.name.replace(':', '_'))
        playerInfo.setRespCount(personalVO['hwVehiclesRespawnCount'])
        banType = TeamMemberBanType.NOTBANNED if not personalVO['hasPenalties'] else TeamMemberBanType.WARNED
        playerInfo.setBanType(banType)
        return

    def __fillRewardsInfo(self, model, totalVO):
        rewardsVO = totalVO['rewards']
        effectivenessKeys = rewardsVO['effectivenessKeys']
        bossKeys = rewardsVO['bossKeys']
        keysBonus = self.__getKeysBonus(effectivenessKeys + bossKeys)
        questBonuses = self.__getQuestBonuses(totalVO['quests'])
        creditsBonus = self.__getCreditsBonus(rewardsVO['credits'])
        hangarLootBonuses = self.__getHangarLootBonuses(rewardsVO.get('hangarLoot', []))
        totalBonuses = creditsBonus + keysBonus + questBonuses + hangarLootBonuses
        dailyKeys = sum((self.__getKeyCountFromTokens(bonus.getTokens()) for bonus in questBonuses if bonus.getName() == 'battleToken'))
        self.__tooltipCtx[_R_KEY_TOOLTIP] = {'effective': effectivenessKeys,
         'boss': bossKeys,
         'daily': dailyKeys,
         'secret': self.__getHangarLootKeysAmount(hangarLootBonuses)}
        model.clear()
        sortedBonuses = sorted(mergeBonuses(totalBonuses), key=getBonusPriority)
        formatter = HalloweenBonusesAwardsComposer(self._MAX_BONUSES_IN_VIEW, getHWBattleResultAwardFormatter())
        bonusRewards = formatter.getFormattedBonuses(sortedBonuses, AWARDS_SIZES.BIG)
        hangarLootFormatter = HalloweenBonusesAwardsComposer(DISPLAY_ALL_AWARDS, getHWBattleResultAwardFormatter())
        hangarLootBonusRewards = hangarLootFormatter.getFormattedBonuses(mergeBonuses(hangarLootBonuses), AWARDS_SIZES.BIG)
        hangarLootBonusRewards = {(hl.images['big'], hl.userName):hl.label for hl in hangarLootBonusRewards}
        for bonus in bonusRewards:
            rewardItem = RewardBonusItemViewModel()
            tooltipId = '{}'.format(next(self.__idGen))
            self.__bonusCache[tooltipId] = bonus
            rewardItem.setName(bonus.bonusName)
            rewardItem.setValue(str(bonus.label))
            rewardItem.setIcon(getImgName(bonus.getImage(AWARDS_SIZES.BIG)))
            rewardItem.setTooltipId(tooltipId)
            if isinstance(bonus.tooltip, int):
                rewardItem.setTooltipContentId(str(bonus.tooltip))
            label = hangarLootBonusRewards.get((bonus.images['big'], bonus.userName))
            if label is not None:
                rewardItem.setIsSecretReward(True)
                amount = int(''.join(filter(str.isdigit, str(label)))) if label else 0
                if bonus.bonusName in _CURRENCIES:
                    tooltipMessage = backport.text(R.strings.battle_results.hw_battle_result.secret_reward.credits(), currency=bonus.userName, amount=backport.getIntegralFormat(amount))
                elif amount < 2:
                    tooltipMessage = backport.text(R.strings.battle_results.hw_battle_result.secret_reward.item(), item=bonus.userName)
                else:
                    tooltipMessage = backport.text(R.strings.battle_results.hw_battle_result.secret_reward.items(), item=bonus.userName, number=label)
                rewardItem.setSecretRewardTooltipMessage(tooltipMessage)
            model.addViewModel(rewardItem)

        model.invalidate()
        return

    def __playVoiceover(self, totalVO):
        commonVO = totalVO['common']
        WWISE.WW_setState(DifficultyState.GROUP, DifficultyState.VALUE(commonVO['bonusType']))
        if commonVO['resultShortStr'] == PLAYER_TEAM_RESULT.WIN:
            VOObjects.WIN.play()
        elif totalVO['hwPhase'] == totalVO['hwPhasesCount']:
            playSound(VO.LOSE_BOSS_FIGHT)
        else:
            playSound(VO.LOSE_BEFORE_BOSS_BATTLE)

    def __getLeaderboardPosition(self, players, personal, field):
        leaderboard = sorted(players, key=lambda block: block[field], reverse=True)
        return leaderboard.index(personal) + 1

    def __getCreditsBonus(self, credits):
        return getNonQuestBonuses(Currency.CREDITS, credits) if credits > 0 else []

    def __getKeysBonus(self, keys):
        return getNonQuestBonuses(TokensBonus.TOKENS, {ArtefactsSettings.KEY_TOKEN: {'count': keys}}) if keys > 0 else []

    def __getHangarLootBonuses(self, hangarLoot):
        if not hangarLoot:
            return []
        result = []
        for lootId, amount in hangarLoot.items():
            bonuses = lootConfigSchema.getModel().getBonus(lootId)
            for name, bonus in bonuses.items():
                for _ in range(0, amount):
                    result += getNonQuestBonuses(name, bonus)

        return result

    def __getHangarLootKeysAmount(self, hangarLootBonuses):
        res = 0
        for bonus in hangarLootBonuses:
            if isinstance(bonus, TokensBonus):
                keys = bonus.getTokens().get(ArtefactsSettings.KEY_TOKEN)
                if keys:
                    res += keys.count

        return res

    def __getQuestBonuses(self, quests):
        questBonuses = []
        for questProgress in quests:
            questID = questProgress['questInfo']['questID']
            quest = self.eventsCache.getAllQuests().get(questID)
            if not quest or not questProgress['awards']:
                continue
            bonuses = quest.getBonuses()
            questBonuses.extend(bonuses)

        return questBonuses

    def __getKeyCountFromTokens(self, tokens):
        artefactKeyToken = tokens.get(ArtefactsSettings.KEY_TOKEN)
        return artefactKeyToken.count if artefactKeyToken else 0


class BattleResultWindow(WindowImpl):

    def __init__(self, layer, **kwargs):
        super(BattleResultWindow, self).__init__(wndFlags=WindowFlags.WINDOW_FULLSCREEN | WindowFlags.WINDOW, layer=layer, content=BattleResultView(**kwargs))
