# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/avatar_components/visual_script_controller.py
import cPickle
import VSE

class VisualScriptController(object):

    def __init__(self):
        self.__enabled = False

    def onBecomePlayer(self):
        self.__enabled = True

    def onBecomeNonPlayer(self):
        self.__enabled = False

    def handleKey(self, isDown, key, mods):
        pass

    def handleScriptEventFromServer(self, eventName, planName, params, targetAspects, eventScope):
        if self.__enabled:
            if eventScope.startswith('ArenaT:') and self.arena is not None:
                eventScope = 'ArenaT:' + str(self.arena.arenaUniqueID)
            VSE.passEventToVisualScript(eventName, planName, cPickle.loads(params), targetAspects, eventScope)
        return
