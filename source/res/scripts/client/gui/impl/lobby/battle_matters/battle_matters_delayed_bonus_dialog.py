# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_matters/battle_matters_delayed_bonus_dialog.py
import typing
from gui.impl import backport
from gui.impl.dialogs.dialog_template import DialogTemplateView
from gui.impl.dialogs.dialog_template_button import ConfirmButton, CancelButton
from gui.impl.dialogs.sub_views.title.simple_text_title import SimpleTextTitle
from gui.impl.gen import R
from gui.impl.lobby.battle_matters.battle_matters_exchange_rewards import BattleMattersExchangeRewards
from gui.shared.gui_items.Vehicle import getNationLessName
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders as Placeholder
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle

class BattleMattersDelayedBonusDialog(DialogTemplateView):
    __slots__ = ('__vehicleUserName', '__vehicleName')

    def __init__(self, vehicle):
        super(BattleMattersDelayedBonusDialog, self).__init__()
        self.__vehicleUserName = vehicle.userName
        self.__vehicleName = getNationLessName(vehicle.name)

    def _onLoading(self, *args, **kwargs):
        self.setSubView(Placeholder.TITLE, SimpleTextTitle(backport.text(R.strings.battle_matters.bonusDelayed.dialog.title(), vehicleName=self.__vehicleUserName)))
        content = BattleMattersExchangeRewards(self.__vehicleName, self.__vehicleUserName)
        self.setSubView(Placeholder.CONTENT, content)
        self.addButton(ConfirmButton(R.strings.offers.giftDialog.submit()))
        self.addButton(CancelButton())
        super(BattleMattersDelayedBonusDialog, self)._onLoading(*args, **kwargs)
