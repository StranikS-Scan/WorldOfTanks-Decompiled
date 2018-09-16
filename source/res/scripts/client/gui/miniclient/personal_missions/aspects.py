# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/miniclient/personal_missions/aspects.py
from helpers import aop

class IsPersonalMissionsEnabled(aop.Aspect):

    def atReturn(self, cd):
        cd.change()
        return False
