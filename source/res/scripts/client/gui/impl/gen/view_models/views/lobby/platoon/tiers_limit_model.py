# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/platoon/tiers_limit_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.platoon.button_model import ButtonModel
from gui.impl.gen.view_models.views.lobby.platoon.show_settings_button_model import ShowSettingsButtonModel

class TiersLimitModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(TiersLimitModel, self).__init__(properties=properties, commands=commands)

    @property
    def btnResetSettings(self):
        return self._getViewModel(0)

    @property
    def btnShowSettings(self):
        return self._getViewModel(1)

    def getTiers(self):
        return self._getString(2)

    def setTiers(self, value):
        self._setString(2, value)

    def getIsExpanded(self):
        return self._getBool(3)

    def setIsExpanded(self, value):
        self._setBool(3, value)

    def getIsLight(self):
        return self._getBool(4)

    def setIsLight(self, value):
        self._setBool(4, value)

    def getHasSettingsButton(self):
        return self._getBool(5)

    def setHasSettingsButton(self, value):
        self._setBool(5, value)

    def getHasLookingForCaption(self):
        return self._getBool(6)

    def setHasLookingForCaption(self, value):
        self._setBool(6, value)

    def getHasTiersCaption(self):
        return self._getBool(7)

    def setHasTiersCaption(self, value):
        self._setBool(7, value)

    def getHasResetButton(self):
        return self._getBool(8)

    def setHasResetButton(self, value):
        self._setBool(8, value)

    def _initialize(self):
        super(TiersLimitModel, self)._initialize()
        self._addViewModelProperty('btnResetSettings', ButtonModel())
        self._addViewModelProperty('btnShowSettings', ShowSettingsButtonModel())
        self._addStringProperty('tiers', '')
        self._addBoolProperty('isExpanded', False)
        self._addBoolProperty('isLight', False)
        self._addBoolProperty('hasSettingsButton', False)
        self._addBoolProperty('hasLookingForCaption', False)
        self._addBoolProperty('hasTiersCaption', False)
        self._addBoolProperty('hasResetButton', False)
