# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/lobby/missions/missions_helpers.py
from gui.impl.lobby.missions.missions_helpers import DefaultMissionsGuiHelper

class FrontlineMissionsGuiHelper(DefaultMissionsGuiHelper):

    @classmethod
    def isDailyMissionsSupported(cls):
        return False

    @classmethod
    def isPM3MissionsSupported(cls):
        return True
