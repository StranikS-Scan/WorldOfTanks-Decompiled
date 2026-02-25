# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/fun_random/__init__.py
from __future__ import absolute_import
from fun_random.gui.shared.fun_system_factory import registerModeAssetsPackConfigPath
from fall_tanks.gui.fun_random.sub_modes import registerFallTanksSubModes

def registerFallTanksFunRandom():
    registerModeAssetsPackConfigPath('fall_tanks', 'fall_tanks/gui/configs/gamemodes/fun_modes/assets_packs/fun_assets_fall_tanks.xml')
    registerFallTanksSubModes()
