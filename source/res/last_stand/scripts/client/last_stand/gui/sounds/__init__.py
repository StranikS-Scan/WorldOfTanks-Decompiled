# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/sounds/__init__.py
import SoundGroups
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control.avatar_getter import getSoundNotifications
from last_stand.gui.ls_gui_constants import BATTLE_CTRL_ID
from LSArenaPhasesComponent import LSArenaPhasesComponent

def playSound(eventName):
    if eventName:
        SoundGroups.g_instance.playSound2D(eventName)


def playVoiceover(voiceover):
    if voiceover:
        soundNotifications = getSoundNotifications()
        if soundNotifications and hasattr(soundNotifications, 'play'):
            soundNotifications.play(voiceover)


class SoundComponentBase(object):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, parent):
        self._parent = parent

    @property
    def parent(self):
        return self._parent

    @property
    def arenaPhases(self):
        return LSArenaPhasesComponent.getInstance()

    @property
    def lsBattleGuiCtrl(self):
        return self._sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.LS_BATTLE_GUI_CTRL)

    def clearAndDestroy(self):
        self.onDestroy()
        self._parent = None
        return

    def onAvatarReady(self):
        pass

    def onDestroy(self):
        pass


class ComponentsHolder(object):

    def __init__(self, components, parent):
        self._components = [ compClass(parent) for compClass in components ]
        self._parent = parent
        self._isDestroyed = False

    def addComponents(self, components):
        if not self._isDestroyed:
            self._components.extend([ compClass(self._parent) for compClass in components ])

    def onAvatarReady(self):
        for comp in self._components:
            comp.onAvatarReady()

    def onDestroy(self):
        self._isDestroyed = True
        for comp in self._components:
            comp.clearAndDestroy()

        self._components = []
        self._parent = None
        return

    def call(self, method, *args):
        if self._isDestroyed:
            return
        else:
            for comp in self._components:
                func = getattr(comp, method, None)
                if func is not None:
                    func(*args)

            return
