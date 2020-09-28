# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/wt_event_exchange_reroll_dialog.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.Waiting import Waiting
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_exchange_to_re_roll_view_model import WtEventExchangeToReRollViewModel
from gui.impl.lobby.dialogs.exchange_with_items import ExchangeWithItems
from gui.shared.money import Money

class WTEventExchangeToReRoll(ExchangeWithItems):
    __slots__ = ('__boxType',)

    def __init__(self, reRollPrice, boxType):
        self.__boxType = boxType
        settings = ViewSettings(layoutID=R.views.lobby.wt_event.WtEventExchangeToLootBoxReRollView(), flags=ViewFlags.OVERLAY_VIEW, model=WtEventExchangeToReRollViewModel())
        super(WTEventExchangeToReRoll, self).__init__(settings=settings, items=[], price=Money(credits=reRollPrice))

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoaded(self, *args, **kwargs):
        super(WTEventExchangeToReRoll, self)._onLoaded(self, *args, **kwargs)
        Waiting.hide('loadPage')

    def _onLoading(self, *args, **kwargs):
        super(WTEventExchangeToReRoll, self)._onLoading(*args, **kwargs)
        Waiting.show('loadPage')
        self.viewModel.setBoxType(self.__boxType)
