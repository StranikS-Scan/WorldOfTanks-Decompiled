# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/veh_mechanics/battle/updaters/mechanics/twin_gun_updater.py
from __future__ import absolute_import
import typing
from events_handler import eventHandler
from gui.veh_mechanics.battle.updaters.mechanics.mechanics_common import VehicleMechanicUpdater
from vehicles.mechanics.mechanic_constants import VehicleMechanic
if typing.TYPE_CHECKING:
    from TwinGunController import TwinGunController

class ITwinGunView(object):

    def setDoubleBarrelMode(self, isActive):
        raise NotImplementedError


class TwinGunUpdater(VehicleMechanicUpdater):

    def __init__(self, view):
        super(TwinGunUpdater, self).__init__(VehicleMechanic.TWIN_GUN, view)
        self.__twinGunComponent = None
        return

    @eventHandler
    def onMechanicComponentCatching(self, component):
        self.__twinGunComponent = component
        component.shootingEvents.onActiveGunsUpdate += self.__onActiveGunsUpdate
        self.__onActiveGunsUpdate(component.getActiveGunIndexes())

    @eventHandler
    def onMechanicComponentReleasing(self, component):
        component.shootingEvents.onActiveGunsUpdate -= self.__onActiveGunsUpdate
        self.__twinGunComponent = None
        return

    def destroy(self):
        self.__twinGunComponent = None
        super(TwinGunUpdater, self).destroy()
        return

    def __onActiveGunsUpdate(self, _):
        self.view.setDoubleBarrelMode(self.__twinGunComponent.isDoubleBarrelMode())
