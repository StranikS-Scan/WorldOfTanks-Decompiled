# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/states_registration.py
from __future__ import absolute_import
import gui.impl.lobby.hangar.states as hangar
import gui.impl.lobby.hangar.playlists_states as playlists

def registerStates(machine):
    hangar.registerStates(machine)
    playlists.registerStates(machine)


def registerTransitions(machine):
    hangar.registerTransitions(machine)
