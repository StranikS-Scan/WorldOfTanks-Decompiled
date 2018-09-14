# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/miniclient/login/aspects.py
from helpers import aop

class ShowBGWallpaper(aop.Aspect):

    def __init__(self):
        super(ShowBGWallpaper, self).__init__()

    def atCall(self, cd):
        super(ShowBGWallpaper, self).atCall(cd)
        cd.self.showWallpaper(showSwitchButton=False)
        cd.avoid()
