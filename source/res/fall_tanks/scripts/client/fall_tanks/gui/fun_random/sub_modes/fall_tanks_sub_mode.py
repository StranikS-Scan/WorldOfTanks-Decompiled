# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/fun_random/sub_modes/fall_tanks_sub_mode.py
from fun_random.gui.feature.sub_modes.base_sub_mode import FunBaseSubMode
from fall_tanks.gui.impl.lobby.fall_tanks_ammunition_setup import FallTanksAmmunitionSetupView

class FallTanksSubMode(FunBaseSubMode):
    __slots__ = ()

    def getAmmoSetupViewAlias(self):
        return FallTanksAmmunitionSetupView.__name__
