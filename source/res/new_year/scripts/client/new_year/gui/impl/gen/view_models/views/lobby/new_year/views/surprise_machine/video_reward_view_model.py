# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/surprise_machine/video_reward_view_model.py
from frameworks.wulf import ViewModel

class VideoRewardViewModel(ViewModel):
    __slots__ = ('closeRewardVehicle', 'showVehicle')

    def __init__(self, properties=5, commands=2):
        super(VideoRewardViewModel, self).__init__(properties=properties, commands=commands)

    def getVehicleName(self):
        return self._getString(0)

    def setVehicleName(self, value):
        self._setString(0, value)

    def getVehicleLvl(self):
        return self._getNumber(1)

    def setVehicleLvl(self, value):
        self._setNumber(1, value)

    def getVehicleType(self):
        return self._getString(2)

    def setVehicleType(self, value):
        self._setString(2, value)

    def getIsElite(self):
        return self._getBool(3)

    def setIsElite(self, value):
        self._setBool(3, value)

    def getIsMainViewVisible(self):
        return self._getBool(4)

    def setIsMainViewVisible(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(VideoRewardViewModel, self)._initialize()
        self._addStringProperty('vehicleName', '')
        self._addNumberProperty('vehicleLvl', 0)
        self._addStringProperty('vehicleType', '')
        self._addBoolProperty('isElite', False)
        self._addBoolProperty('isMainViewVisible', True)
        self.closeRewardVehicle = self._addCommand('closeRewardVehicle')
        self.showVehicle = self._addCommand('showVehicle')
