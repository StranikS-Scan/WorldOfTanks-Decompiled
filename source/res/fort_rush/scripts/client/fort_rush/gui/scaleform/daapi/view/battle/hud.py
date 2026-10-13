# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/scaleform/daapi/view/battle/hud.py
from __future__ import absolute_import
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.impl import IGuiLoader
from fort_rush.gui.impl.battle.fort_rush_hud import FortRushHudView

class FortRushHudComponent(object):
    FORT_RUSH_HUD_R = R.views.fort_rush.mono.battle.fort_rush_hud()
    gui = dependency.descriptor(IGuiLoader)

    @property
    def hud(self):
        return self.gui.windowsManager.getViewByLayoutID(self.FORT_RUSH_HUD_R)
