# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/mode_selector/items/__init__.py
import typing
from account_helpers.AccountSettings import AccountSettings, MODE_SELECTOR_BATTLE_PASS_SHOWN
from constants import ARENA_BONUS_TYPE
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_normal_card_model import BattlePassState
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController, IBootcampController
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_normal_card_model import ModeSelectorNormalCardModel
BATTLE_PASS_SEASON_ID = 'seasonId'
_arenaBonusTypeByModeName = {PREBATTLE_ACTION_NAME.RANDOM: ARENA_BONUS_TYPE.REGULAR,
 PREBATTLE_ACTION_NAME.RANKED: ARENA_BONUS_TYPE.RANKED,
 PREBATTLE_ACTION_NAME.EPIC: ARENA_BONUS_TYPE.EPIC_BATTLE,
 PREBATTLE_ACTION_NAME.BATTLE_ROYALE: ARENA_BONUS_TYPE.BATTLE_ROYALE_SOLO,
 PREBATTLE_ACTION_NAME.MAPBOX: ARENA_BONUS_TYPE.MAPBOX,
 PREBATTLE_ACTION_NAME.COMP7: ARENA_BONUS_TYPE.COMP7,
 PREBATTLE_ACTION_NAME.WINBACK: ARENA_BONUS_TYPE.WINBACK}

def setBattlePassState(itemVM):
    battlePassController = dependency.instance(IBattlePassController)
    bootcampController = dependency.instance(IBootcampController)
    arenaBonusType = _arenaBonusTypeByModeName.get(itemVM.getModeName(), ARENA_BONUS_TYPE.UNKNOWN)
    isActive = battlePassController.isEnabled()
    isPaused = battlePassController.isPaused()
    isOffSeason = not battlePassController.isSeasonStarted() or battlePassController.isSeasonFinished()
    isGameModeEnabled = battlePassController.isGameModeEnabled(arenaBonusType)
    hasStatusNotActive = bool(itemVM.getStatusNotActive())
    seasonId = battlePassController.getSeasonStartTime()
    if not isActive or isPaused or isOffSeason or not isGameModeEnabled or hasStatusNotActive:
        resetBattlePassStateForItem(itemVM)
        return
    bpSettings = AccountSettings.getSettings(MODE_SELECTOR_BATTLE_PASS_SHOWN)
    isShown = bpSettings.get(itemVM.getModeName(), False)
    isNewSeason = bpSettings.get(BATTLE_PASS_SEASON_ID, 0) != seasonId
    if bootcampController.isInBootcamp():
        state = BattlePassState.NONE
    else:
        state = BattlePassState.STATIC if isShown and not isNewSeason else BattlePassState.NEW
    itemVM.setBattlePassState(state)


def resetBattlePassStateForItem(itemVM):
    itemVM.setBattlePassState(BattlePassState.NONE)
    saveBattlePassStateForItem(itemVM.getModeName(), False)


def saveBattlePassStateForItem(modeSelectorItem, value):
    bpSettings = AccountSettings.getSettings(MODE_SELECTOR_BATTLE_PASS_SHOWN)
    bpSettings[modeSelectorItem] = value
    AccountSettings.setSettings(MODE_SELECTOR_BATTLE_PASS_SHOWN, bpSettings)


def saveBattlePassStateForItems(itemList):
    battlePassController = dependency.instance(IBattlePassController)
    if battlePassController.isEnabled():
        prevSettings = AccountSettings.getSettings(MODE_SELECTOR_BATTLE_PASS_SHOWN)
        bpSettings = {}
        for item in itemList:
            if not item.viewModel.getIsDisabled():
                bpSettings[item.modeName] = item.viewModel.getBattlePassState() != BattlePassState.NONE
            if item.modeName in prevSettings:
                bpSettings[item.modeName] = prevSettings[item.modeName]

        bpSettings[BATTLE_PASS_SEASON_ID] = battlePassController.getSeasonStartTime()
        AccountSettings.setSettings(MODE_SELECTOR_BATTLE_PASS_SHOWN, bpSettings)
