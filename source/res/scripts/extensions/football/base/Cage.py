# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/extensions/football/base/Cage.py
import BigWorld
from wotdecorators import noexcept
from debug_utils import *

class Cage(BigWorld.Base):

    def __init__(self):
        BigWorld.Base.__init__(self)
        self.shouldAutoBackup = BigWorld.NEXT_ONLY

    @noexcept
    def createCellNearHere(self, cellMailbox):
        self.createCellEntity(cellMailbox)

    def onRestore(self):
        self.smartDestroy()

    def onGetCell(self):
        self.shouldAutoBackup = BigWorld.NEXT_ONLY

    def onLoseCell(self):
        self.destroy()

    @noexcept
    def smartDestroy(self):
        if hasattr(self, 'cell'):
            self.destroyCellEntity()
        else:
            self.destroy()
