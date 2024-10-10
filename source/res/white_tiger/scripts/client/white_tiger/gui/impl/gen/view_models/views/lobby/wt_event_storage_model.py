# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/wt_event_storage_model.py
from white_tiger.gui.impl.gen.view_models.views.lobby.wt_event_guaranteed_award import WtEventGuaranteedAward
from white_tiger.gui.impl.gen.view_models.views.lobby.wt_event_portal_availability import WtEventPortalAvailability
from white_tiger.gui.impl.gen.view_models.views.lobby.wt_event_portals_base import WtEventPortalsBase

class WtEventStorageModel(WtEventPortalsBase):
    __slots__ = ('onPortalClick',)

    def __init__(self, properties=11, commands=3):
        super(WtEventStorageModel, self).__init__(properties=properties, commands=commands)

    @property
    def hunterPortal(self):
        return self._getViewModel(7)

    @staticmethod
    def getHunterPortalType():
        return WtEventPortalAvailability

    @property
    def bossPortal(self):
        return self._getViewModel(8)

    @staticmethod
    def getBossPortalType():
        return WtEventPortalAvailability

    @property
    def tankPortal(self):
        return self._getViewModel(9)

    @staticmethod
    def getTankPortalType():
        return WtEventPortalAvailability

    @property
    def guaranteedAward(self):
        return self._getViewModel(10)

    @staticmethod
    def getGuaranteedAwardType():
        return WtEventGuaranteedAward

    def _initialize(self):
        super(WtEventStorageModel, self)._initialize()
        self._addViewModelProperty('hunterPortal', WtEventPortalAvailability())
        self._addViewModelProperty('bossPortal', WtEventPortalAvailability())
        self._addViewModelProperty('tankPortal', WtEventPortalAvailability())
        self._addViewModelProperty('guaranteedAward', WtEventGuaranteedAward())
        self.onPortalClick = self._addCommand('onPortalClick')
