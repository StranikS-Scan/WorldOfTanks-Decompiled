# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/platoon/tiers_limit_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.platoon.button_model import ButtonModel
from gui.impl.gen.view_models.views.lobby.platoon.show_settings_button_model import ShowSettingsButtonModel

class TiersLimitModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
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

    def getShowLookingForCaption(self):
        return self._getBool(5)

    def setShowLookingForCaption(self, value):
        self._setBool(5, value)

    def getShowTiersCaption(self):
        return self._getBool(6)

    def setShowTiersCaption(self, value):
        self._setBool(6, value)

    def getHideResetButton(self):
        return self._getBool(7)

    def setHideResetButton(self, value):
        self._setBool(7, value)

    def _initialize(self):
        super(TiersLimitModel, self)._initialize()
        self._addViewModelProperty('btnResetSettings', ButtonModel())
        self._addViewModelProperty('btnShowSettings', ShowSettingsButtonModel())
        self._addStringProperty('tiers', '')
        self._addBoolProperty('isExpanded', False)
        self._addBoolProperty('isLight', False)
        self._addBoolProperty('showLookingForCaption', False)
        self._addBoolProperty('showTiersCaption', False)
        self._addBoolProperty('hideResetButton', False)
