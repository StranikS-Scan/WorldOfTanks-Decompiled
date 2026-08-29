# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/portals/wt_tank_portal_view_model.py
from white_tiger.gui.impl.gen.view_models.views.lobby.common.wt_run_portal_model import WtRunPortalModel
from white_tiger.gui.impl.gen.view_models.views.lobby.portals.main_prize_model import MainPrizeModel
from white_tiger.gui.impl.gen.view_models.views.lobby.portals.wt_base_portals_view_model import WtBasePortalsViewModel

class WtTankPortalViewModel(WtBasePortalsViewModel):
    __slots__ = ('onGoBack', 'onRunPortal', 'onPreviewTank')

    def __init__(self, properties=4, commands=5):
        super(WtTankPortalViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def portalRun(self):
        return self._getViewModel(1)

    @staticmethod
    def getPortalRunType():
        return WtRunPortalModel

    @property
    def mainPrize(self):
        return self._getViewModel(2)

    @staticmethod
    def getMainPrizeType():
        return MainPrizeModel

    def getBackButtonText(self):
        return self._getString(3)

    def setBackButtonText(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(WtTankPortalViewModel, self)._initialize()
        self._addViewModelProperty('portalRun', WtRunPortalModel())
        self._addViewModelProperty('mainPrize', MainPrizeModel())
        self._addStringProperty('backButtonText', '')
        self.onGoBack = self._addCommand('onGoBack')
        self.onRunPortal = self._addCommand('onRunPortal')
        self.onPreviewTank = self._addCommand('onPreviewTank')
