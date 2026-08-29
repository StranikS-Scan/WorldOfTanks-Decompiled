# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/__init__.py
from __future__ import absolute_import

def getStateMachineRegistrators():
    from white_tiger.gui.impl.lobby.states import registerStates, registerTransitions
    return (registerStates, registerTransitions)


def getViewSettings():
    pass


def getBusinessHandlers():
    pass


def getContextMenuHandlers():
    pass


def registerModeToPOMapping():
    from gui.Scaleform.daapi.view.lobby.formatters.tooltips import _MODENAME_TO_PO_FILE
    from white_tiger.gui.white_tiger_gui_constants import SELECTOR_BATTLE_TYPES
    _MODENAME_TO_PO_FILE.update({SELECTOR_BATTLE_TYPES.WHITE_TIGER: 'white_tiger_lobby'})


def registerWhiteTigerTokenBonus():
    from gui.server_events.bonuses import _BONUSES
    from constants import EVENT_TYPE
    from white_tiger.gui.server_events.bonuses import whiteTigerTokensFactory
    _BONUSES['tokens'].update({'default': whiteTigerTokensFactory,
     EVENT_TYPE.BATTLE_QUEST: whiteTigerTokensFactory,
     EVENT_TYPE.TOKEN_QUEST: whiteTigerTokensFactory,
     EVENT_TYPE.PERSONAL_QUEST: whiteTigerTokensFactory,
     EVENT_TYPE.ELEN_QUEST: whiteTigerTokensFactory})
    _BONUSES['ticket'] = whiteTigerTokensFactory
    _BONUSES['lootBox'] = whiteTigerTokensFactory


def registerWhiteTigerBonusPackers():
    from gui.shared.system_factory import registerBonusPackers
    from white_tiger.gui.wt_bonus_packers import WTTokenBonusPacker
    registerBonusPackers('ticket', WTTokenBonusPacker())
