# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/hangar/base/fun_vehicles_filter_component.py
from __future__ import absolute_import
import typing
from fun_random.gui.feature.util.fun_mixins import FunSubModesWatcher
from fun_random.gui.feature.util.fun_wrappers import hasDesiredSubMode
from gui.impl.lobby.hangar.base.vehicles_filter_component import VehiclesFilterComponent
from gui.shared.utils.requesters import REQ_CRITERIA
if typing.TYPE_CHECKING:
    from gui.shared.utils.requesters import RequestCriteria
FUN_RANDOM_CRITERIA = ~REQ_CRITERIA.VEHICLE.MODE_HIDDEN | ~REQ_CRITERIA.VEHICLE.BATTLE_ROYALE | ~REQ_CRITERIA.VEHICLE.EVENT_BATTLE | REQ_CRITERIA.VEHICLE.ACTIVE_IN_NATION_GROUP

class FunRandomVehiclesFilterComponent(VehiclesFilterComponent, FunSubModesWatcher):

    def __init__(self, criteria=REQ_CRITERIA.EMPTY):
        self.__baseCriteria = criteria
        self.__subModeCriteria = self.__getSubModeCriteria()
        super(FunRandomVehiclesFilterComponent, self).__init__(self.__createCriteria())

    def initialize(self):
        super(FunRandomVehiclesFilterComponent, self).initialize()
        self.startSubSelectionListening(self.__onSubModeChanged)

    def destroy(self):
        self.stopSubSelectionListening(self.__onSubModeChanged)
        super(FunRandomVehiclesFilterComponent, self).destroy()

    def __createCriteria(self):
        return self.__baseCriteria | (self.__subModeCriteria or FUN_RANDOM_CRITERIA)

    @hasDesiredSubMode()
    def __getSubModeCriteria(self):
        return self.getDesiredSubMode().getCarouselBaseCriteria()

    def __onSubModeChanged(self, *_):
        self.__subModeCriteria, oldCriteria = self.__getSubModeCriteria(), self.__subModeCriteria
        if self.__subModeCriteria != oldCriteria:
            self._setCriteria(self.__createCriteria())
