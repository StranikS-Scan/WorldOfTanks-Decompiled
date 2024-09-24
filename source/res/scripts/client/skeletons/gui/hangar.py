# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/hangar.py
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from gui.prb_control.items import FunctionalState

class ICarouselEventEntry(object):

    @staticmethod
    def getIsActive(state):
        raise NotImplementedError
