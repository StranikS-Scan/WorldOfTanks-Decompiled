# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/whats_new_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel
from gui.impl.gen.view_models.views.lobby.comp7.maps_model import MapsModel
from gui.impl.gen.view_models.views.lobby.comp7.page_model import PageModel
from gui.impl.gen.view_models.views.lobby.comp7.schedule_info_model import ScheduleInfoModel

class WhatsNewViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=5, commands=1):
        super(WhatsNewViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def pages(self):
        return self._getViewModel(0)

    @staticmethod
    def getPagesType():
        return PageModel

    @property
    def newMaps(self):
        return self._getViewModel(1)

    @staticmethod
    def getNewMapsType():
        return MapsModel

    @property
    def depricatedMaps(self):
        return self._getViewModel(2)

    @staticmethod
    def getDepricatedMapsType():
        return MapsModel

    @property
    def scheduleInfo(self):
        return self._getViewModel(3)

    @staticmethod
    def getScheduleInfoType():
        return ScheduleInfoModel

    def getVehicles(self):
        return self._getArray(4)

    def setVehicles(self, value):
        self._setArray(4, value)

    @staticmethod
    def getVehiclesType():
        return VehicleModel

    def _initialize(self):
        super(WhatsNewViewModel, self)._initialize()
        self._addViewModelProperty('pages', UserListModel())
        self._addViewModelProperty('newMaps', UserListModel())
        self._addViewModelProperty('depricatedMaps', UserListModel())
        self._addViewModelProperty('scheduleInfo', ScheduleInfoModel())
        self._addArrayProperty('vehicles', Array())
        self.onClose = self._addCommand('onClose')
