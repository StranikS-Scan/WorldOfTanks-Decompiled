# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/shared/gui_items/items_actions/__init__.py
from gui.shared.gui_items.items_actions.factory import registerAction
from armory_yard.gui.shared.gui_items.items_actions.actions import CollectRewardsAction, BuyStepTokensAction
COLLECT_REWARDS = 'collectRewards'
BUY_STEP_TOKENS = 'buyStepTokens'

def registerActions():
    registerAction(COLLECT_REWARDS, CollectRewardsAction)
    registerAction(BUY_STEP_TOKENS, BuyStepTokensAction)
