# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/gen/view_models/views/lobby/portal_lobby_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from portal.gui.impl.gen.view_models.views.lobby.complexity_level_widget import ComplexityLevelWidget
from portal.gui.impl.gen.view_models.views.lobby.portal_ammunition_panel import PortalAmmunitionPanel
from portal.gui.impl.gen.view_models.views.lobby.portal_carousel_tank_model import PortalCarouselTankModel
from portal.gui.impl.gen.view_models.views.lobby.portal_quest_widget import PortalQuestWidget

class PortalLobbyViewModel(ViewModel):
    __slots__ = ('onClose', 'onAboutEvent', 'onShopClicked', 'onProgressionClicked', 'onComplexityChange', 'onVehicleSelect', 'onMoveSpace', 'onStartMoving', 'onUpgradeVehicle', 'onShowSettings')

    def __init__(self, properties=4, commands=10):
        super(PortalLobbyViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def tanks(self):
        return self._getViewModel(0)

    @staticmethod
    def getTanksType():
        return PortalCarouselTankModel

    @property
    def portalAmmunitionPanel(self):
        return self._getViewModel(1)

    @staticmethod
    def getPortalAmmunitionPanelType():
        return PortalAmmunitionPanel

    @property
    def portalQuestWidget(self):
        return self._getViewModel(2)

    @staticmethod
    def getPortalQuestWidgetType():
        return PortalQuestWidget

    @property
    def complexityLevelWidget(self):
        return self._getViewModel(3)

    @staticmethod
    def getComplexityLevelWidgetType():
        return ComplexityLevelWidget

    def _initialize(self):
        super(PortalLobbyViewModel, self)._initialize()
        self._addViewModelProperty('tanks', UserListModel())
        self._addViewModelProperty('portalAmmunitionPanel', PortalAmmunitionPanel())
        self._addViewModelProperty('portalQuestWidget', PortalQuestWidget())
        self._addViewModelProperty('complexityLevelWidget', ComplexityLevelWidget())
        self.onClose = self._addCommand('onClose')
        self.onAboutEvent = self._addCommand('onAboutEvent')
        self.onShopClicked = self._addCommand('onShopClicked')
        self.onProgressionClicked = self._addCommand('onProgressionClicked')
        self.onComplexityChange = self._addCommand('onComplexityChange')
        self.onVehicleSelect = self._addCommand('onVehicleSelect')
        self.onMoveSpace = self._addCommand('onMoveSpace')
        self.onStartMoving = self._addCommand('onStartMoving')
        self.onUpgradeVehicle = self._addCommand('onUpgradeVehicle')
        self.onShowSettings = self._addCommand('onShowSettings')
