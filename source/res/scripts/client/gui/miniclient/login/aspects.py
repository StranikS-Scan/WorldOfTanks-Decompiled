# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/miniclient/login/aspects.py
from helpers import aop

class ShowBGInsteadVideo(aop.Aspect):

    def __init__(self):
        super(ShowBGInsteadVideo, self).__init__()

    def atCall(self, cd):
        super(ShowBGInsteadVideo, self).atCall(cd)
        cd.self._showOnlyStaticBackground()
        cd.avoid()
