# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/dialogs/perks_reset_dialog.py
import time
import typing
import SoundGroups
from chat_shared import SYS_MESSAGE_TYPE
from gui import SystemMessages
from gui.customization.shared import getPurchaseGoldForCredits, getPurchaseMoneyState, MoneyForPurchase
from gui.impl import backport
from gui.impl.auxiliary.tankman_operations import packSkills, packBaseTankman
from gui.impl.dialogs.dialog_template_button import CancelButton, ConfirmButton
from gui.impl.dialogs.sub_views.content.simple_text_content import SimpleTextContent
from gui.impl.dialogs.sub_views.title.simple_text_title import SimpleTextTitle
from gui.impl.dialogs.sub_views.top_right.money_balance import MoneyBalance
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders
from gui.impl.gen.view_models.views.dialogs.dialog_template_button_view_model import ButtonType
from gui.impl.gen.view_models.views.lobby.crew.dialogs.perks_reset_dialog_model import PerksResetDialogModel
from gui.impl.lobby.crew.crew_sounds import SOUNDS
from gui.impl.lobby.crew.dialogs.price_cards_content.perks_reset_price_list import PerksResetPriceList
from gui.impl.pub.dialog_window import DialogButtons
from gui.shared import event_dispatcher
from gui.shared.gui_items.Tankman import Tankman
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.gui_items.processors.tankman import TankmanDropSkills
from gui.shared.utils import decorators
from gui.shop import showBuyGoldForCrew
from helpers import dependency
from items.tankmen import TankmanDescr
from messenger import MessengerEntry
from skeletons.gui.shared import IItemsCache
from gui.impl.lobby.crew.crew_helpers.tankman_helpers import getPerksResetGracePeriod
from collections import namedtuple
from base_crew_dialog_template_view import BaseCrewDialogTemplateView
if typing.TYPE_CHECKING:
    pass
_LOC = R.strings.dialogs.perksReset

class PerksResetDialog(BaseCrewDialogTemplateView):
    __slots__ = ('_tankman', '_priceListContent', '_isFreePerkReset', '_lastSoundEvent', '_isFreeByGold')
    _itemsCache = dependency.descriptor(IItemsCache)
    VIEW_MODEL = PerksResetDialogModel

    def __init__(self, tankmanId):
        self._tankman = self._itemsCache.items.getTankman(tankmanId)
        self._isFreePerkReset = self._tankman.descriptor.isFreeDropSkills()
        super(PerksResetDialog, self).__init__(layoutID=None if self._isFreePerkReset else R.views.lobby.crew.dialogs.PerksResetDialog())
        self._isFreeByGold = getPerksResetGracePeriod() > 0 or not self._tankman.descriptor.firstSkillResetDisabled
        self._lastSoundEvent = None
        if not self._isFreePerkReset:
            self._priceListContent = PerksResetPriceList(tankmanId)
        return

    def _onLoading(self, *args, **kwargs):
        self.setBackgroundImagePath(R.images.gui.maps.icons.windows.background())
        if self._isFreePerkReset:
            self.setSubView(DefaultDialogPlaceHolders.CONTENT, SimpleTextContent(_LOC.free.description()))
            self.setSubView(DefaultDialogPlaceHolders.TITLE, SimpleTextTitle(str(backport.text(_LOC.title()))))
        else:
            self.setSubView(DefaultDialogPlaceHolders.TOP_RIGHT, MoneyBalance())
            self.setChildView(self._priceListContent.layoutID, self._priceListContent)
            self._initModel()
        isResetBtnDisabled = not (self._isFreeByGold or self._isFreePerkReset)
        self.addButton(ConfirmButton(_LOC.submit(), isDisabled=isResetBtnDisabled, buttonType=ButtonType.MAIN))
        self.addButton(CancelButton(_LOC.cancel()))
        if self._lastSoundEvent is None:
            self._lastSoundEvent = SOUNDS.CREW_RESET_PERK_SELECTION
            SoundGroups.g_instance.playSound2D(self._lastSoundEvent)
        super(PerksResetDialog, self)._onLoading(*args, **kwargs)
        return

    def _initModel(self):
        with self.viewModel.transaction() as vm:
            self._updateTankmenBefore()
            if not self._isFreePerkReset and self._isFreeByGold:
                _, (xpReuseFraction, _, _), _ = self._priceListContent.selectedPriceData
                self._updateTankmanAfter(xpReuseFraction)
            vm.setTitle(str(backport.text(_LOC.title())))
            vm.setResetGracePeriodLeft(getPerksResetGracePeriod())
            vm.setHasFreeFirstReset(not self._tankman.descriptor.firstSkillResetDisabled)

    def _finalize(self):
        super(PerksResetDialog, self)._finalize()
        self._priceListContent = None
        return

    def _getEvents(self):
        return tuple() if self._isFreePerkReset else ((self._priceListContent.onPriceChange, self._onPriceChange),)

    def _onPriceChange(self, index=None):
        submitBtn = self.getButton(DialogButtons.SUBMIT)
        if submitBtn is not None:
            isDisabled = index is None
            submitBtn.isDisabled = isDisabled
            if not isDisabled:
                priceNamed = namedtuple('priceNamed', ['xpReuseFraction', 'xpAmountLoss', 'skillsCountLoss'])
                _, priceData, _ = self._priceListContent.selectedPriceData
                price = priceNamed(*priceData)
                with self.viewModel.transaction():
                    self._updateTankmanAfter(price.xpReuseFraction)
                if price.xpAmountLoss:
                    if price.skillsCountLoss:
                        if self._lastSoundEvent != SOUNDS.CREW_RESET_PERK_HUGE_LOSS:
                            self._lastSoundEvent = soundEvent = SOUNDS.CREW_RESET_PERK_HUGE_LOSS
                        else:
                            soundEvent = SOUNDS.CREW_RESET_PERK_XP_LOSS
                    else:
                        self._lastSoundEvent = soundEvent = SOUNDS.CREW_RESET_PERK_XP_LOSS
                else:
                    self._lastSoundEvent = soundEvent = SOUNDS.CREW_RESET_PERK_NO_LOSS
                SoundGroups.g_instance.playSound2D(soundEvent)
        return

    def _setResult(self, result):
        if result == DialogButtons.SUBMIT:
            if not self._resetPerks():
                return
        super(PerksResetDialog, self)._setResult(result)

    def _resetPerks(self):
        if self._isFreePerkReset or self._isFreeByGold:
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
                event_dispatcher.showExchangeCurrencyWindowModal(gold=purchaseGold, backgroundImage=R.images.gui.maps.icons.windows.background())
                return False
            self.__processReset(self._tankman, dropSkillKey, price, self._isFreePerkReset)
            return True

    def _updateTankmenBefore(self):
        packBaseTankman(self.viewModel.tankmanBefore, self._tankman)
        packSkills(self.viewModel.tankmanBefore.skillList, self._tankman)

    def _updateTankmanAfter(self, xpReuseFraction):
        tmanDescr = TankmanDescr(self._tankman.strCD)
        tmanDescr.dropSkills(xpReuseFraction)
        tankman = Tankman(tmanDescr.makeCompactDescr(), vehicle=self._tankman.getVehicle(), vehicleSlotIdx=self._tankman.vehicleSlotIdx)
        tankman.setCombinedRoles(self._tankman.roles())
        packBaseTankman(self.viewModel.tankmanAfter, tankman)
        packSkills(self.viewModel.tankmanAfter.skillList, tankman)

    @decorators.adisp_process('deleting')
    def __processReset(self, tankman, dropSkillKey, price, freeDrop):
        useRecertificationForm = price is None
        proc = TankmanDropSkills(tankman, dropSkillKey, useRecertificationForm)
        result = yield proc.request()
        if result.userMsg:
            if not useRecertificationForm or freeDrop:
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
            else:
                action = {'sentTime': time.time(),
                 'data': {'type': SYS_MESSAGE_TYPE.recertificationResetUsed.index(),
                          'data': {'currencyType': 'blanks',
                                   'count': 1}}}
                MessengerEntry.g_instance.protos.BW.serviceChannel.onReceivePersonalSysMessage(action)
        return
