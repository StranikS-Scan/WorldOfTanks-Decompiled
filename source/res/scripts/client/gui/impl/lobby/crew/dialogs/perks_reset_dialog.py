# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/dialogs/perks_reset_dialog.py
import time
import typing
from base_crew_dialog_template_view import BaseCrewDialogTemplateView
from chat_shared import SYS_MESSAGE_TYPE
from gui import SystemMessages
from gui.customization.shared import getPurchaseGoldForCredits, getPurchaseMoneyState, MoneyForPurchase
from gui.impl import backport
from gui.impl.dialogs.dialog_template_button import CancelButton, ConfirmButton
from gui.impl.dialogs.sub_views.content.simple_text_content import SimpleTextContent
from gui.impl.dialogs.sub_views.title.simple_text_title import SimpleTextTitle
from gui.impl.dialogs.sub_views.top_right.money_balance import MoneyBalance
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders
from gui.impl.lobby.crew.dialogs.price_cards_content.perks_reset_price_list import PerksResetPriceList
from gui.impl.pub.dialog_window import DialogButtons
from gui.shared import event_dispatcher
from gui.shared.gui_items.Tankman import Tankman, getRolePossessiveCaseUserName
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.gui_items.processors.tankman import TankmanDropSkills
from gui.shared.utils import decorators
from gui.shop import showBuyGoldForCrew
from helpers import dependency
from messenger import MessengerEntry
from skeletons.gui.shared import IItemsCache
from uilogging.crew.logging_constants import CrewViewKeys, CrewDialogKeys
from uilogging.epic_battle.constants import EpicBattleLogActions
from uilogging.epic_battle.loggers import EpicBattleTooltipLogger
if typing.TYPE_CHECKING:
    pass
_LOC = R.strings.dialogs.perksRest

class PerksResetDialog(BaseCrewDialogTemplateView):
    __slots__ = ('_tankman', '_priceListContent', '_uiEpicBattleLogger', '_isFreePerkReset')
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, tankmanId):
        super(PerksResetDialog, self).__init__()
        self._tankman = self._itemsCache.items.getTankman(tankmanId)
        self._uiEpicBattleLogger = EpicBattleTooltipLogger()
        self._isFreePerkReset = self._tankman.descriptor.isFreeDropSkills()
        if not self._isFreePerkReset:
            self._priceListContent = PerksResetPriceList(tankmanId)

    def _onLoading(self, *args, **kwargs):
        role = getRolePossessiveCaseUserName(self._tankman.role, self._tankman.isFemale)
        self.setSubView(DefaultDialogPlaceHolders.TITLE, SimpleTextTitle(str(backport.text(_LOC.title(), tankmanRole=role))))
        self.setBackgroundImagePath(R.images.gui.maps.icons.windows.background())
        if self._isFreePerkReset:
            self.setSubView(DefaultDialogPlaceHolders.CONTENT, SimpleTextContent(_LOC.free.description()))
        else:
            self.setSubView(DefaultDialogPlaceHolders.TOP_RIGHT, MoneyBalance())
            self.setSubView(DefaultDialogPlaceHolders.CONTENT, self._priceListContent)
        self.addButton(ConfirmButton(_LOC.submit(), isDisabled=not self._isFreePerkReset))
        self.addButton(CancelButton(_LOC.cancel()))
        self._uiEpicBattleLogger.log(EpicBattleLogActions.OPEN.value, item=CrewDialogKeys.PERKS_RESET, parentScreen=CrewViewKeys.PERSONAL_FILE)
        self._uiEpicBattleLogger.initialize(CrewDialogKeys.PERKS_RESET)
        super(PerksResetDialog, self)._onLoading(*args, **kwargs)

    def _finalize(self):
        self._uiEpicBattleLogger.reset()
        self._uiEpicBattleLogger = None
        super(PerksResetDialog, self)._finalize()
        self._priceListContent = None
        return

    def _getEvents(self):
        return tuple() if self._isFreePerkReset else ((self._priceListContent.onPriceChange, self._onPriceChange),)

    def _onPriceChange(self, index=None):
        submitBtn = self.getButton(DialogButtons.SUBMIT)
        if submitBtn is not None:
            submitBtn.isDisabled = index is None
        return

    def _setResult(self, result):
        self._uiEpicBattleLogger.log(EpicBattleLogActions.CLICK.value, item=result, parentScreen=CrewDialogKeys.PERKS_RESET)
        if result == DialogButtons.SUBMIT:
            if not self._resetPerks():
                return
        super(PerksResetDialog, self)._setResult(result)

    def _resetPerks(self):
        if self._isFreePerkReset:
            self.__processReset(self._tankman, 0, None, True)
            return True
        elif self._priceListContent.isRecertification:
            self.__processReset(self._tankman, self._priceListContent.goldOptionKey, None, False)
            return True
        else:
            itemPrice, _, dropSkillKey = self._priceListContent.selectedPriceData
            price = self._itemsCache.items.shop.dropSkillsCost[dropSkillKey]
            purchaseMoneyState = getPurchaseMoneyState(itemPrice.price)
            if purchaseMoneyState is MoneyForPurchase.NOT_ENOUGH:
                showBuyGoldForCrew(itemPrice.price.gold)
                return False
            elif purchaseMoneyState is MoneyForPurchase.ENOUGH_WITH_EXCHANGE:
                purchaseGold = getPurchaseGoldForCredits(itemPrice.price)
                event_dispatcher.showExchangeCurrencyWindowModal(currencyValue=purchaseGold)
                return False
            self.__processReset(self._tankman, dropSkillKey, price, self._isFreePerkReset)
            return True

    @decorators.adisp_process('deleting')
    def __processReset(self, tankman, dropSkillKey, price, freeDrop):
        useRecertificationForm = price is None
        proc = TankmanDropSkills(tankman, dropSkillKey, useRecertificationForm)
        result = yield proc.request()
        if result.userMsg:
            if not useRecertificationForm:
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
            else:
                data = {'currencyType': '',
                 'count': 0}
                if not freeDrop:
                    data['currencyType'] = 'blanks'
                    data['count'] = 1
                    messageType = SYS_MESSAGE_TYPE.recertificationResetUsed
                    action = {'sentTime': time.time(),
                     'data': {'type': messageType.index(),
                              'data': data}}
                    MessengerEntry.g_instance.protos.BW.serviceChannel.onReceivePersonalSysMessage(action)
        return
