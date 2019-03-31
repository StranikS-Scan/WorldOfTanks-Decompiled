# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/GameLoading.py
# Compiled at: 2019-03-28 16:05:52
import BigWorld
import GUI
import ResMgr
from debug_utils import LOG_DEBUG
from gui.Scaleform.Flash import Flash
from helpers import i18n

class GameLoading(Flash):

    def __init__(self, component=None):
        Flash.__init__(self, 'GameLoading.swf')
        self.call('Stage.Update', list(GUI.screenResolution()))
        self.__loadVersion()
        BigWorld.WGC_prepareLogin()
        isKorea = BigWorld.WGC_getRealm() == u'asia' or ResMgr.isFile('../korea_grac')
        self.call('Loading.showAgeRating', [isKorea])

    def onLoad(self, dataSection):
        self.active(True)

    def onBound(self):
        pass

    def setProgress(self, value):
        self.call('setProgress', [value])

    def addMessage(self, message):
        LOG_DEBUG(message)

    def reset(self):
        self.call('setProgress', [0])

    def __loadVersion(self):
        sec = ResMgr.openSection('../version.xml')
        version = i18n.makeString(sec.readString('appname')) + ' ' + sec.readString('version')
        self.call('Login.SetVersion', [version])
