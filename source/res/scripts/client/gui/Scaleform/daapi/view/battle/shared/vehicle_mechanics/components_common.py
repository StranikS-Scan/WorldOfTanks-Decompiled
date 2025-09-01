# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/vehicle_mechanics/components_common.py
import typing
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent
if typing.TYPE_CHECKING:
    from gui.veh_mechanics.battle.updaters.updaters_common import IViewUpdater

class VehicleMechanicDAAPIComponent(BaseDAAPIComponent):

    def __init__(self):
        super(VehicleMechanicDAAPIComponent, self).__init__()
        self.__updaters = []

    def _populate(self):
        super(VehicleMechanicDAAPIComponent, self)._populate()
        self.__updaters = self._getViewUpdaters()
        self._initializeUpdaters()

    def _dispose(self):
        self._finalizeUpdaters()
        del self.__updaters[:]
        super(VehicleMechanicDAAPIComponent, self)._dispose()

    def _getViewUpdaters(self):
        return []

    def _initializeUpdaters(self):
        for updater in self.__updaters:
            updater.initialize()

    def _finalizeUpdaters(self):
        for updater in self.__updaters:
            updater.finalize()
