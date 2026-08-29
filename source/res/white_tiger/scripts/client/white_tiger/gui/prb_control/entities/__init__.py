# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/prb_control/entities/__init__.py
from gui.impl.lobby.buy_vehicle_view import BuyVehicleWindow
from gui.prb_control.settings import FUNCTIONAL_FLAG

def isHangarShallBeLoaded(ctx):
    flags = FUNCTIONAL_FLAG.LOAD_PAGE | FUNCTIONAL_FLAG.TRAINING
    return ctx and not ctx.hasFlags(flags) and not BuyVehicleWindow.getInstances()
