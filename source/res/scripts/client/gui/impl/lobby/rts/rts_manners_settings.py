# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/rts/rts_manners_settings.py
from itertools import izip
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Dict

class RtsMannersSettings(dict):

    def __init__(self, roster):
        super(RtsMannersSettings, self).__init__()
        self.load(roster)

    def load(self, roster):
        if not roster:
            return
        for intCD, manner in izip(roster['vehicles'], roster['rtsManners']):
            if intCD and manner:
                self[intCD] = manner
