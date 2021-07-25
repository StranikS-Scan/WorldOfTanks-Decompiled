# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/crew2/perk/settings.py
from constants import ITEM_DEFS_PATH
from crew2.perk.matrices import PerkMatrices
DEF_PERK_SETTINGS_PATH = ITEM_DEFS_PATH + 'crew2/perks/'

class PerkSettings(object):

    def __init__(self, path):
        matricesPath = path + 'matrices.xml'
        self._matrices = PerkMatrices(matricesPath)

    @property
    def matrices(self):
        return self._matrices
