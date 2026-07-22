# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/lobby/tooltips/golden_ticket_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency
from mt_birthday.gui.impl.gen.view_models.views.lobby.tooltips.gold_ticket_tooltip_model import GoldTicketTooltipModel
from mt_birthday.skeletons.mt_birthday_controller import ITanksBirthdayController

class GoldTicketTooltip(ViewImpl):
    __tankBirthdayController = dependency.descriptor(ITanksBirthdayController)

    def __init__(self):
        settings = ViewSettings(layoutID=R.views.mt_birthday.lobby.tooltips.GoldTicketTooltip(), model=GoldTicketTooltipModel())
        super(GoldTicketTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(GoldTicketTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(GoldTicketTooltip, self)._onLoading()
        self.viewModel.setCurrencyCount(self.__tankBirthdayController.getGoldenTicketsCount())
