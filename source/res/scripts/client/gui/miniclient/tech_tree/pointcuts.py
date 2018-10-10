# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/miniclient/tech_tree/pointcuts.py
import aspects
from helpers import aop

class OnTechTreePopulate(aop.Pointcut):

    def __init__(self):
        aop.Pointcut.__init__(self, 'gui.Scaleform.daapi.view.lobby.techtree.techtree_page', 'TechTree', '_populate', aspects=(aspects.OnTechTreePopulate,))


class OnBuyVehicle(aop.Pointcut):

    def __init__(self, config):
        aop.Pointcut.__init__(self, 'gui.Scaleform.daapi.view.lobby.vehicle_obtain_windows', 'VehicleBuyWindow', 'submit', aspects=(aspects.OnBuyVehicle(config),))


class OnRestoreVehicle(aop.Pointcut):

    def __init__(self, config):
        aop.Pointcut.__init__(self, 'gui.Scaleform.daapi.view.lobby.vehicle_obtain_windows', 'VehicleRestoreWindow', 'submit', aspects=(aspects.OnRestoreVehicle(config),))
