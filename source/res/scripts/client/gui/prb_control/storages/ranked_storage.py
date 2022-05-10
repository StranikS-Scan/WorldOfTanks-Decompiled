# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/storages/ranked_storage.py
from gui.prb_control.storages.local_storage import SessionStorage, ARENA_GUI_TYPE

class RankedStorage(SessionStorage):
    _GUI_TYPE = ARENA_GUI_TYPE.RANKED
