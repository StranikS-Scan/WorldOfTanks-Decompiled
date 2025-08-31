# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/prb_control/storages/white_tiger_battles_storage.py
from gui.prb_control.storages.local_storage import SessionStorage
from white_tiger_common.wt_constants import ARENA_GUI_TYPE

class WhiteTigerBattlesStorage(SessionStorage):
    _GUI_TYPE = ARENA_GUI_TYPE.WHITE_TIGER
