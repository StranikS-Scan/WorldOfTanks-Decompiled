# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/mode_selector/items/__init__.py
import typing
from account_helpers.AccountSettings import AccountSettings, MODE_SELECTOR_BATTLE_PASS_SHOWN
from constants import ARENA_BONUS_TYPE
from helpers import dependency
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_normal_card_model import BattlePassState
from gui.impl.lobby.mode_selector.items.items_constants import arenaBonusTypeByModeName
from skeletons.gui.game_control import IBattlePassController, IBootcampController
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_normal_card_model import ModeSelectorNormalCardModel
BATTLE_PASS_SEASON_ID = 'seasonId'

def setBattlePassState(itemVM):
    battlePassController = dependency.instance(IBattlePassController)
    bootcampController = dependency.instance(IBootcampController)
    arenaBonusType = arenaBonusTypeByModeName.get(itemVM.getModeName(), ARENA_BONUS_TYPE.UNKNOWN)
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
