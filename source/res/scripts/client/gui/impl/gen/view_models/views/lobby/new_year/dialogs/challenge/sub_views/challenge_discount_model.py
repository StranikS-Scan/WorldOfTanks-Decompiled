# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/dialogs/challenge/sub_views/challenge_discount_model.py
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel
from gui.impl.gen.view_models.views.lobby.new_year.dialogs.challenge.sub_views.challenge_base_model import ChallengeBaseModel

class ChallengeDiscountModel(ChallengeBaseModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=2):
        super(ChallengeDiscountModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleInfo(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleInfoType():
        return VehicleInfoModel

    def getDiscountInPercent(self):
        return self._getNumber(1)

    def setDiscountInPercent(self, value):
        self._setNumber(1, value)

    def getErrorMessage(self):
        return self._getString(2)

    def setErrorMessage(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(ChallengeDiscountModel, self)._initialize()
        self._addViewModelProperty('vehicleInfo', VehicleInfoModel())
        self._addNumberProperty('discountInPercent', 0)
        self._addStringProperty('errorMessage', '')
