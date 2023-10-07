# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/prb_control/storage/halloween_storage.py
from gui.prb_control.storages.local_storage import SessionStorage
from halloween_common.halloween_constants import ARENA_GUI_TYPE

class HalloweenStorage(SessionStorage):
    _GUI_TYPE = ARENA_GUI_TYPE.HALLOWEEN_BATTLES
