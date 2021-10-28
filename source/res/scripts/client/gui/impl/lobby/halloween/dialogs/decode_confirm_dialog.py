# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/halloween/dialogs/decode_confirm_dialog.py
from gui.impl.dialogs.sub_views.footer.event_single_price_footer import EventSinglePrice
from gui.impl.dialogs.sub_views.top_right.event_money_balance import EventMoneyBalance
from gui.impl.gen import R
from gui.impl import backport
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from gui.impl.dialogs.dialog_template import DialogTemplateView
from skeletons.gui.game_event_controller import IGameEventController
from gui.impl.dialogs.dialog_template_button import CancelButton, ConfirmButton
from gui.impl.dialogs.sub_views.content.simple_text_content import SimpleTextContent
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders as Placeholder
from gui.impl.gen.view_models.views.dialogs.dialog_template_button_view_model import ButtonType

class DecodeConfirmDialog(DialogTemplateView):
    _itemsCache = dependency.descriptor(IItemsCache)
    _gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, price, layoutID=None, uniqueID=None, *args, **kwargs):
        super(DecodeConfirmDialog, self).__init__(layoutID, uniqueID, *args, **kwargs)
        self.__price = price

    def _onLoading(self, *args, **kwargs):
        self.setSubView(Placeholder.TITLE, SimpleTextContent(backport.text(R.strings.event.hangar.interrogation.confirm_buy.label())))
        self.setSubView(Placeholder.TOP_RIGHT, EventMoneyBalance())
        self.setSubView(Placeholder.FOOTER, EventSinglePrice(backport.text(R.strings.event.tradeStyles.confirmationCost()), self.__price.amount, self.__price.currency))
        self.addButton(ConfirmButton(R.strings.event.hangar.interrogation.confirm_buy.labelExecute(), buttonType=ButtonType.PRIMARY))
        self.addButton(CancelButton())
        super(DecodeConfirmDialog, self)._onLoading(*args, **kwargs)
