# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/frontman_extra_model.py
from frameworks.wulf import Array
from historical_battles.gui.impl.gen.view_models.views.common.ability_model import AbilityModel
from historical_battles.gui.impl.gen.view_models.views.lobby.base_frontman_model import BaseFrontmanModel
from historical_battles.gui.impl.gen.view_models.views.lobby.quest_progresive_model import QuestProgresiveModel

class FrontmanExtraModel(BaseFrontmanModel):
    __slots__ = ('onVehicleChange',)

    def __init__(self, properties=11, commands=1):
        super(FrontmanExtraModel, self).__init__(properties=properties, commands=commands)

    @property
    def progress(self):
        return self._getViewModel(6)

    @staticmethod
    def getProgressType():
        return QuestProgresiveModel

    def getPerkId(self):
        return self._getNumber(7)

    def setPerkId(self, value):
        self._setNumber(7, value)

    def getPerkName(self):
        return self._getString(8)

    def setPerkName(self, value):
        self._setString(8, value)

    def getPolygon(self):
        return self._getString(9)

    def setPolygon(self, value):
        self._setString(9, value)

    def getAbilities(self):
        return self._getArray(10)

    def setAbilities(self, value):
        self._setArray(10, value)

    @staticmethod
    def getAbilitiesType():
        return AbilityModel

    def _initialize(self):
        super(FrontmanExtraModel, self)._initialize()
        self._addViewModelProperty('progress', QuestProgresiveModel())
        self._addNumberProperty('perkId', 0)
        self._addStringProperty('perkName', '')
        self._addStringProperty('polygon', '')
        self._addArrayProperty('abilities', Array())
        self.onVehicleChange = self._addCommand('onVehicleChange')
