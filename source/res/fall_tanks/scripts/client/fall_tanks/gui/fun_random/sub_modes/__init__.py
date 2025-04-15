# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/fun_random/sub_modes/__init__.py
from fun_random.gui.shared.fun_system_factory import registerFunRandomSubMode
from fall_tanks_constants import FunSubModeImpl
from fall_tanks.gui.fun_random.sub_modes.fall_tanks_sub_mode import FallTanksSubMode

def registerFallTanksSubModes():
    registerFunRandomSubMode(FunSubModeImpl.FALL_TANKS, FallTanksSubMode)
