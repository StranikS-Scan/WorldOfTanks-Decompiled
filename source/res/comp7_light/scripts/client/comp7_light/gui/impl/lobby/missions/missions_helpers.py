# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/lobby/missions/missions_helpers.py
from gui.impl.lobby.missions.missions_helpers import DefaultMissionsGuiHelper

class Comp7LightMissionsGuiHelper(DefaultMissionsGuiHelper):

    @classmethod
    def isDailyMissionsSupported(cls):
        return True

    @classmethod
    def isPM3MissionsSupported(cls):
        return False
