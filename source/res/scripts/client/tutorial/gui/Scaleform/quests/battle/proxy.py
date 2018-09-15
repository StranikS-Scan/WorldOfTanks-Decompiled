# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/gui/Scaleform/quests/battle/proxy.py
from tutorial.gui import GUIProxy

class BattleQuestsProxy(GUIProxy):

    def init(self):
        self.onGUILoaded()
        return True

    def fini(self):
        self.eManager.clear()

    def clear(self):
        self.clearChapterInfo()

    def getSceneID(self):
        pass

    def playEffect(self, effectName, args, itemRef=None, containerRef=None):
        return False

    def isEffectRunning(self, effectName, effectID=None):
        return False
