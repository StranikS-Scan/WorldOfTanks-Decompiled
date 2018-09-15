# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/miniclient/personal_missions/aspects.py
from gui.shared.formatters import text_styles
from helpers import aop
from helpers.i18n import makeString as _ms

class IsPersonalMissionsEnabled(aop.Aspect):

    def atReturn(self, cd):
        cd.change()
        return False
