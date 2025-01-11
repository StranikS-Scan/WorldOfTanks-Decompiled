# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_guest_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_guest_tooltip_model import NyGuestTooltipModel, GuestType
from gui.impl.pub import ViewImpl

class NyGuestTooltip(ViewImpl):
    __slots__ = ('__guestType',)

    def __init__(self, guestType=GuestType.NY_DOG.value):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.NyGuestTooltip())
        settings.model = NyGuestTooltipModel()
        self.__guestType = guestType
        super(NyGuestTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NyGuestTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(NyGuestTooltip, self)._onLoading()
        with self.viewModel.transaction() as model:
            guestType = self.__getGusetType()
            model.setGuestType(guestType)

    def __getGusetType(self):
        guestType = self.__guestType if isinstance(self.__guestType, str) else self.__guestType.value
        if guestType == GuestType.NY_DOG.value:
            return GuestType.NY_DOG
        return GuestType.NY_CAT if guestType == GuestType.NY_CAT.value else GuestType.NY_CAT
