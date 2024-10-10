# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/early_access/early_access_vehicle_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.early_access.early_access_vehicle_model import EarlyAccessVehicleModel

class EarlyAccessVehicleViewModel(ViewModel):
    __slots__ = ('onSelectVehicle', 'onCompare', 'onShowVehiclePreview', 'onShowInHangar', 'onBuyVehicle', 'onAboutEvent', 'onBackToHangar', 'onBackToPrevScreen', 'onBuyTokens', 'onGoToQuests', 'onMoveSpace', 'onStartMoving', 'onAnimationFinished')
    ARG_VEHICLE_CD = 'vehicleCD'

    def __init__(self, properties=10, commands=13):
        super(EarlyAccessVehicleViewModel, self).__init__(properties=properties, commands=commands)

    def getCurrentDate(self):
        return self._getNumber(0)

    def setCurrentDate(self, value):
        self._setNumber(0, value)

    def getStartDate(self):
        return self._getNumber(1)

    def setStartDate(self, value):
        self._setNumber(1, value)

    def getEndDate(self):
        return self._getNumber(2)

    def setEndDate(self, value):
        self._setNumber(2, value)

    def getEndProgressionDate(self):
        return self._getNumber(3)

    def setEndProgressionDate(self, value):
        self._setNumber(3, value)

    def getFeatureState(self):
        return self._getString(4)

    def setFeatureState(self, value):
        self._setString(4, value)

    def getCurrentVehicleCD(self):
        return self._getNumber(5)

    def setCurrentVehicleCD(self, value):
        self._setNumber(5, value)

    def getTokensBalance(self):
        return self._getNumber(6)

    def setTokensBalance(self, value):
        self._setNumber(6, value)

    def getVehicles(self):
        return self._getArray(7)

    def setVehicles(self, value):
        self._setArray(7, value)

    @staticmethod
    def getVehiclesType():
        return EarlyAccessVehicleModel

    def getIsFromTechTree(self):
        return self._getBool(8)

    def setIsFromTechTree(self, value):
        self._setBool(8, value)

    def getIsQuestWidgetEnabled(self):
        return self._getBool(9)

    def setIsQuestWidgetEnabled(self, value):
        self._setBool(9, value)

    def _initialize(self):
        super(EarlyAccessVehicleViewModel, self)._initialize()
        self._addNumberProperty('currentDate', 0)
        self._addNumberProperty('startDate', 0)
        self._addNumberProperty('endDate', 0)
        self._addNumberProperty('endProgressionDate', 0)
        self._addStringProperty('featureState', '')
        self._addNumberProperty('currentVehicleCD', 0)
        self._addNumberProperty('tokensBalance', 0)
        self._addArrayProperty('vehicles', Array())
        self._addBoolProperty('isFromTechTree', False)
        self._addBoolProperty('isQuestWidgetEnabled', False)
        self.onSelectVehicle = self._addCommand('onSelectVehicle')
        self.onCompare = self._addCommand('onCompare')
        self.onShowVehiclePreview = self._addCommand('onShowVehiclePreview')
        self.onShowInHangar = self._addCommand('onShowInHangar')
        self.onBuyVehicle = self._addCommand('onBuyVehicle')
        self.onAboutEvent = self._addCommand('onAboutEvent')
        self.onBackToHangar = self._addCommand('onBackToHangar')
        self.onBackToPrevScreen = self._addCommand('onBackToPrevScreen')
        self.onBuyTokens = self._addCommand('onBuyTokens')
        self.onGoToQuests = self._addCommand('onGoToQuests')
        self.onMoveSpace = self._addCommand('onMoveSpace')
        self.onStartMoving = self._addCommand('onStartMoving')
        self.onAnimationFinished = self._addCommand('onAnimationFinished')
