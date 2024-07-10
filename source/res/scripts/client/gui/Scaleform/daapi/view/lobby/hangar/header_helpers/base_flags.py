# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/header_helpers/base_flags.py
import typing
from typing import Dict, List, Optional, Union
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle

class IQuestsFlag(object):

    @classmethod
    def isFlagSuitable(cls, questType):
        raise NotImplementedError

    @classmethod
    def formatQuests(cls, vehicle, params):
        raise NotImplementedError

    @classmethod
    def showQuestsInfo(cls, questType, questID):
        raise NotImplementedError
