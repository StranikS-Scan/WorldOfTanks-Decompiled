# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/platoon/window_header_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.platoon.bonus_model import BonusModel
from gui.impl.gen.view_models.views.lobby.platoon.button_model import ButtonModel
from gui.impl.gen.view_models.views.lobby.platoon.mute_all_toggle_model import MuteAllToggleModel
from gui.impl.gen.view_models.views.lobby.platoon.no_bonus_placeholder_model import NoBonusPlaceholderModel

class WindowHeaderModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(WindowHeaderModel, self).__init__(properties=properties, commands=commands)

    @property
    def noBonusPlaceholder(self):
        return self._getViewModel(0)

    @staticmethod
    def getNoBonusPlaceholderType():
        return NoBonusPlaceholderModel

    @property
    def btnLeavePlatoon(self):
        return self._getViewModel(1)

    @staticmethod
    def getBtnLeavePlatoonType():
        return ButtonModel

    @property
    def btnMuteAll(self):
        return self._getViewModel(2)

    @staticmethod
    def getBtnMuteAllType():
        return MuteAllToggleModel

    def getBackgroundImage(self):
        return self._getString(3)

    def setBackgroundImage(self, value):
        self._setString(3, value)

    def getShowNoBonusPlaceholder(self):
        return self._getBool(4)

    def setShowNoBonusPlaceholder(self, value):
        self._setBool(4, value)

    def getShowInfoIcon(self):
        return self._getBool(5)

    def setShowInfoIcon(self, value):
        self._setBool(5, value)

    def getBonuses(self):
        return self._getArray(6)

    def setBonuses(self, value):
        self._setArray(6, value)

    @staticmethod
    def getBonusesType():
        return BonusModel

    def _initialize(self):
        super(WindowHeaderModel, self)._initialize()
        self._addViewModelProperty('noBonusPlaceholder', NoBonusPlaceholderModel())
        self._addViewModelProperty('btnLeavePlatoon', ButtonModel())
        self._addViewModelProperty('btnMuteAll', MuteAllToggleModel())
        self._addStringProperty('backgroundImage', '')
        self._addBoolProperty('showNoBonusPlaceholder', False)
        self._addBoolProperty('showInfoIcon', False)
        self._addArrayProperty('bonuses', Array())
