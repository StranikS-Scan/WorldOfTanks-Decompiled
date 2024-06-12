# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/early_access/shared/actions/__init__.py
from gui.shared.gui_items.items_actions.factory import registerAction
from gui.impl.lobby.early_access.shared.actions.early_access_actions import BuyEarlyAccessTokensAction
BUY_EARLY_ACCESS_TOKENS = 'buyEarlyAccessTokens'
registerAction(BUY_EARLY_ACCESS_TOKENS, BuyEarlyAccessTokensAction)
