# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/vehicle_mechanics/components_common.py
from __future__ import absolute_import
import typing
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent
from gui.veh_mechanics.battle.updaters.updaters_common import ViewUpdatersCollection
if typing.TYPE_CHECKING:
    from gui.veh_mechanics.battle.updaters.updaters_common import IViewUpdater

class VehicleMechanicDAAPIComponent(BaseDAAPIComponent):

    def __init__(self):
        super(VehicleMechanicDAAPIComponent, self).__init__()
        self.__updatersCollection = ViewUpdatersCollection()

    def _populate(self):
        super(VehicleMechanicDAAPIComponent, self)._populate()
        self.__updatersCollection.initialize(self._getViewUpdaters())

    def _dispose(self):
        self.__updatersCollection.finalize()
        super(VehicleMechanicDAAPIComponent, self)._dispose()

    def _destroy(self):
        self.__updatersCollection.destroy()
        super(VehicleMechanicDAAPIComponent, self)._destroy()

    def _getViewUpdaters(self):
        return []
