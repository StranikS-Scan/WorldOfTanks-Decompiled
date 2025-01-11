# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_friends_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_friends_tooltip import NyFriendsTooltip as NyFriendsTooltipModel

class NyFriendsTooltip(ViewImpl):

    def __init__(self, kind, payload, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.NyFriendsTooltips())
        settings.model = NyFriendsTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        self.__type = kind
        self.__payload = payload
        super(NyFriendsTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NyFriendsTooltip, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(NyFriendsTooltip, self)._initialize()
        with self.viewModel.transaction() as model:
            model.setType(self.__type)
            model.setPayload(self.__payload)
