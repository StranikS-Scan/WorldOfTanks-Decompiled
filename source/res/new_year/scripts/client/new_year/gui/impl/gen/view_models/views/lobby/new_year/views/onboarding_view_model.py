# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/onboarding_view_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.components.ny_currency_panel_model import NyCurrencyPanelModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.city.ny_city_marker_model import NyCityMarkerModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.ny_back_button_model import NyBackButtonModel

class CameraState(IntEnum):
    NOT_EXIST = -1
    NOT_INSTALLED = 0
    INSTALLED = 1
    IN_TRANSITION = 2


class OnboardingState(IntEnum):
    DEFAULT = 0
    FIR = 1
    PANORAMA = 2


class OnboardingViewModel(ViewModel):
    __slots__ = ('onClose', 'onLevelUp', 'onHoverMarker', 'onHoverOutMarker', 'onMouseOver3dScene', 'onMoveSpace', 'onMoveTo', 'onGoToFirObject')

    def __init__(self, properties=6, commands=8):
        super(OnboardingViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def backButton(self):
        return self._getViewModel(0)

    @staticmethod
    def getBackButtonType():
        return NyBackButtonModel

    @property
    def firMarker(self):
        return self._getViewModel(1)

    @staticmethod
    def getFirMarkerType():
        return NyCityMarkerModel

    @property
    def currencyPanel(self):
        return self._getViewModel(2)

    @staticmethod
    def getCurrencyPanelType():
        return NyCurrencyPanelModel

    def getAnimationCurrency(self):
        return self._getNumber(3)

    def setAnimationCurrency(self, value):
        self._setNumber(3, value)

    def getCurrentState(self):
        return OnboardingState(self._getNumber(4))

    def setCurrentState(self, value):
        self._setNumber(4, value.value)

    def getCameraState(self):
        return CameraState(self._getNumber(5))

    def setCameraState(self, value):
        self._setNumber(5, value.value)

    def _initialize(self):
        super(OnboardingViewModel, self)._initialize()
        self._addViewModelProperty('backButton', NyBackButtonModel())
        self._addViewModelProperty('firMarker', NyCityMarkerModel())
        self._addViewModelProperty('currencyPanel', NyCurrencyPanelModel())
        self._addNumberProperty('animationCurrency', 0)
        self._addNumberProperty('currentState')
        self._addNumberProperty('cameraState')
        self.onClose = self._addCommand('onClose')
        self.onLevelUp = self._addCommand('onLevelUp')
        self.onHoverMarker = self._addCommand('onHoverMarker')
        self.onHoverOutMarker = self._addCommand('onHoverOutMarker')
        self.onMouseOver3dScene = self._addCommand('onMouseOver3dScene')
        self.onMoveSpace = self._addCommand('onMoveSpace')
        self.onMoveTo = self._addCommand('onMoveTo')
        self.onGoToFirObject = self._addCommand('onGoToFirObject')
