# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/lobby/user_missions/fort_rush_missions_helper.py
from __future__ import absolute_import
from gui.impl.lobby.missions.missions_helpers import DefaultMissionsGuiHelper

class FortRushMissionsGuiHelper(DefaultMissionsGuiHelper):

    @classmethod
    def isDailyMissionsSupported(cls):
        return True

    @classmethod
    def isPM3MissionsSupported(cls):
        return False
