# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/sounds/__init__.py
from __future__ import absolute_import
import SoundGroups
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control.avatar_getter import getSoundNotifications
from halloween.gui.halloween_gui_constants import BATTLE_CTRL_ID
from HWArenaPhasesComponent import HWArenaPhasesComponent

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
        return HWArenaPhasesComponent.getInstance()

    @property
    def hwBattleGuiCtrl(self):
        return self._sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.HW_BATTLE_GUI_CTRL)

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

    def extend(self, components, parent):
        self._components.extend([ compClass(parent) for compClass in components ])

    def onAvatarReady(self):
        for comp in self._components:
            comp.onAvatarReady()

    def onDestroy(self):
        for comp in self._components:
            comp.clearAndDestroy()

        self._components = []

    def call(self, method, *args):
        for comp in self._components:
            func = getattr(comp, method, None)
            if func is not None:
                func(*args)

        return
