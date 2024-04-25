# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/prb_control/prb_dev.py
import Keys
from gui import InputHandler
from gui.development.dev_prebattle import createDevPrbEntry
from historical_battles_common.hb_constants_extension import ARENA_BONUS_TYPE, ARENA_GUI_TYPE

def prbDevSubscribe(ctx):
    InputHandler.g_instance.onKeyDown += handleKeyDown


def prbDevUnsubscribe(ctx):
    InputHandler.g_instance.onKeyDown -= handleKeyDown


def handleKeyDown(event):
    if event.key is Keys.KEY_O and event.isCtrlDown():
        createDevPrbEntry(bonusType=ARENA_BONUS_TYPE.HISTORICAL_BATTLES, arenaGuiType=ARENA_GUI_TYPE.HISTORICAL_BATTLES)
