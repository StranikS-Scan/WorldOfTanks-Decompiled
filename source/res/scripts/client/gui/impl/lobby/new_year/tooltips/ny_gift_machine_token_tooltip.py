# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_gift_machine_token_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_gift_machine_token_tooltip_model import NyGiftMachineTokenTooltipModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.new_year import INewYearController

class NyGiftMachineTokenTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.NyGiftMachineTokenTooltip())
        settings.model = NyGiftMachineTokenTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        super(NyGiftMachineTokenTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NyGiftMachineTokenTooltip, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(NyGiftMachineTokenTooltip, self)._initialize()
        _nyController = dependency.instance(INewYearController)
        with self.viewModel.transaction() as tx:
            tx.setTokenCount(_nyController.currencies.getCoinsCount())
            adventCalendarState = kwargs.get('adventCalendarState')
            if adventCalendarState:
                tx.setAdventCalendarState(adventCalendarState)
                tx.setAdventCalendarDoorsToOpenAmount(kwargs.get('adventCalendarDoorsToOpenAmount', 0))
                tx.setIsAdventCalendarPostEvent(kwargs.get('isAdventCalendarPostEvent', False))
