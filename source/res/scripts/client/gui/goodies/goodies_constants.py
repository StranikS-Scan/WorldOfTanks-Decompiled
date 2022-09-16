# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/goodies/goodies_constants.py
from enum import Enum
from account_helpers.AccountSettings import RECERTIFICATION_FORM_SEEN, DEMOUNT_KIT_SEEN
from gui.shared.gui_items import GUI_ITEM_TYPE
NOVELTY_OBJECTS = {GUI_ITEM_TYPE.DEMOUNT_KIT: DEMOUNT_KIT_SEEN,
 GUI_ITEM_TYPE.RECERTIFICATION_FORM: RECERTIFICATION_FORM_SEEN}

class BoosterCategory(Enum):
    PERSONAL = 'personal'
    CLAN = 'clan'
    EVENT = 'event'
