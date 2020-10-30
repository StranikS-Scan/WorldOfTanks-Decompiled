# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/event/event_crew_healing.py
import re
from CurrentVehicle import g_currentVehicle, g_currentPreviewVehicle
from account_helpers.AccountSettings import AccountSettings, EVENT_HEALING_SEEN, EVENT_COMMANDERS_READY_SEEN
from adisp import process
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getBuyGoldUrl
from gui.shared.event_dispatcher import showShop
from constants import HE19EnergyPurposes, EVENT_CLIENT_DATA
from gui import DialogsInterface
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.dialogs.ExchangeDialogMeta import ExchangeCreditsRechargeMeta
from gui.Scaleform.daapi.view.meta.EventManageCrewMeta import EventManageCrewMeta
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import moneyWithIcon
from gui.shared.money import Currency
from gui.shared.money import Money
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.shared import IItemsCache

class FakeCrewHealing(EventManageCrewMeta):
    gameEventController = dependency.descriptor(IGameEventController)
    itemsCache = dependency.descriptor(IItemsCache)
    _ENERGY_ITEM_PURPOSE = HE19EnergyPurposes.healing.name
    _SHOW_HEALING_ALL_DELAY = 3

    def __init__(self):
        super(FakeCrewHealing, self).__init__()
        self._vehCD = None
        self.__vehiclesTime = {}
        self.__needToRepair = False
        self._vehiclesController = self.gameEventController.getVehiclesController()
        self.__stats = self.itemsCache.items.stats
        return

    @property
    def currentAttempt(self):
        return self._vehiclesController.getCurrentAttempt(self._ENERGY_ITEM_PURPOSE)

    @property
    def shortage(self):
        currency, price = self._getEnergyPrice()
        shortage = self.__stats.money.getShortage(Money.makeFrom(currency, price))
        return shortage.get(currency)

    @process
    def onApply(self):
        currency, amount = self._getEnergyPrice()
        if self.shortage and not self._getEnergyFor():
            if currency == Currency.GOLD:
                showShop(getBuyGoldUrl())
                return
            meta = ExchangeCreditsRechargeMeta(backport.text(R.strings.event.hangar.crew_healing()), amount)
            isOk, _ = yield DialogsInterface.showDialog(meta)
            if not isOk:
                return
        data = self._getConfirmData()
        isOk = yield DialogsInterface.showEventMessageDialog(data)
        if not isOk:
            return
        if not data['storageAmount']:
            success = yield self._vehiclesController.buyEnergy(self._ENERGY_ITEM_PURPOSE, self._vehCD)
            if success and self._ENERGY_ITEM_PURPOSE == FakeCrewHealing._ENERGY_ITEM_PURPOSE:
                AccountSettings.setCounters(EVENT_COMMANDERS_READY_SEEN, True)
        else:
            self._vehiclesController.applyCommanderEnergy(self._ENERGY_ITEM_PURPOSE, self._vehCD)

    @process
    def showTraining(self):
        label = backport.text(R.strings.event.hangar.crew_healing.confirm_train.label())
        labelExecute = backport.text(R.strings.event.hangar.crew_healing.confirm_train.labelExecute())
        iconCommander = self.gameEventController.getVehicleSettings().getTankManIcon(self._vehCD)
        message = backport.text(R.strings.event.hangar.crew_healing.confirm_train.message())
        yield DialogsInterface.showEventMessageDialog({'messagePreset': 'EventInfoMessageUI',
         'label': label,
         'labelExecute': labelExecute,
         'iconPath': iconCommander,
         'message': message,
         'storageAmount': 0,
         'closeByEscape': False,
         'showCloseButton': False})
        AccountSettings.setCounters(EVENT_HEALING_SEEN, True)

    def handleTokensUpdate(self, tokens):
        for token in tokens:
            if re.search(self._ENERGY_ITEM_PURPOSE, token):
                self._update()
                break

    def onMoneyUpdate(self, *args):
        self._update()

    def onIngameEventsUpdate(self, *args):
        self._update()

    def _isApplyButtonEnabled(self):
        return (self._mayPurchaseWithExchange() or bool(self._getEnergyFor())) and not g_currentVehicle.isInBattle()

    def _isEnabled(self):
        return self._vehiclesController.isEnabled()

    def _hasUsedEnergy(self):
        return self._vehiclesController.hasEnergy(self._ENERGY_ITEM_PURPOSE, self._vehCD)

    def _getEnergyFor(self):
        return self._vehiclesController.getEnergyFor(self._ENERGY_ITEM_PURPOSE)

    def _getEnergyPrice(self):
        return self._vehiclesController.getEnergyPrice(self._ENERGY_ITEM_PURPOSE, self._vehCD)

    def _checkTimeAndEnergy(self):
        timeLeft = self.__vehiclesTime.get(self._vehCD)
        return True if timeLeft is None or timeLeft == self._vehiclesController.INVALID_TIME or self._vehiclesController.hasEnergy(FakeCrewHealing._ENERGY_ITEM_PURPOSE, self._vehCD) else False

    def _getConfirmData(self):
        currency, amount = self._getEnergyPrice()
        labelExecute = backport.text(R.strings.event.hangar.crew_healing.confirm_buy.labelExecute()) if self._getEnergyFor() else backport.text(R.strings.event.hangar.crew_healing.confirm_buy.labelBuy())
        data = {'messagePreset': 'EventConfirmMessageUI',
         'label': backport.text(R.strings.event.hangar.crew_healing.confirm_buy.label()),
         'message': backport.text(R.strings.event.hangar.crew_healing.confirm_buy.message()),
         'labelExecute': labelExecute,
         'iconPath': backport.image(R.images.gui.maps.icons.event.manageCrew.big.heal()),
         'costValue': amount if not self._getEnergyFor() else 0,
         'currency': currency,
         'storageAmount': self._getEnergyFor()}
        return data

    def _populate(self):
        super(FakeCrewHealing, self)._populate()
        g_currentVehicle.onChanged += self.__onVehicleSelected
        g_currentPreviewVehicle.onChanged += self.__onVehicleSelected
        self._vehiclesController.onTimeToRepairChanged += self.__onTimeToRepairChanged
        self.__onVehicleSelected()
        g_clientUpdateManager.addCallbacks({'stats.gold': self.onMoneyUpdate,
         'stats.credits': self.onMoneyUpdate,
         'tokens': self.handleTokensUpdate,
         'eventsData.' + str(EVENT_CLIENT_DATA.INGAME_EVENTS_REV): self.onIngameEventsUpdate})
        self._callback = CallbackDelayer()
        if self.__hasAllVehiclesInInventoryEnergy():
            self._showHealingAll()
        self.__vehiclesTime = self._vehiclesController.vehiclesTime
        self._updatePanel()

    def _dispose(self):
        g_currentVehicle.onChanged -= self.__onVehicleSelected
        g_currentPreviewVehicle.onChanged -= self.__onVehicleSelected
        self._vehiclesController.onTimeToRepairChanged -= self.__onTimeToRepairChanged
        g_clientUpdateManager.removeObjectCallbacks(self)
        self._callback.destroy()
        super(FakeCrewHealing, self)._dispose()

    def _showHealingAll(self):
        if self._isEnabled() and not AccountSettings.getCounters(EVENT_COMMANDERS_READY_SEEN) and self._ENERGY_ITEM_PURPOSE == FakeCrewHealing._ENERGY_ITEM_PURPOSE:
            AccountSettings.setCounters(EVENT_COMMANDERS_READY_SEEN, True)
            SystemMessages.pushMessage('', SystemMessages.SM_TYPE.EventHealingAll)

    def _update(self):
        self._updatePanel()
        if self.__needToRepair and not self._hasUsedEnergy() and not AccountSettings.getCounters(EVENT_HEALING_SEEN):
            self.showTraining()

    def _updatePanel(self):
        if not self._isEnabled():
            self.__needToRepair = False
            self.as_setVisibleS(False)
            return
        if self._checkTimeAndEnergy():
            if self.__needToRepair:
                self.__needToRepair = False
                self.as_setVisibleS(False)
                g_currentVehicle.refreshModel()
            return
        if not self._checkVehCanHaveEnergy():
            self.__needToRepair = False
            self.as_setVisibleS(False)
            return
        self.as_setDataS(self._getPannelMeta())
        if not self.__needToRepair:
            self.__needToRepair = True
            self.as_setVisibleS(True)

    def _checkVehCanHaveEnergy(self):
        if g_currentPreviewVehicle.isPresent() or not g_currentVehicle.isPresent():
            return False
        return False if not self._vehiclesController.isEventVehicleCanHaveEnergy(self._ENERGY_ITEM_PURPOSE, self._vehCD) else True

    def _getTooltipInfo(self, currency, alias):
        specialArgs = []
        if g_currentVehicle.isInBattle():
            specialAlias = TOOLTIPS_CONSTANTS.EVENT_COMMANDER_IN_BATTLE
            specialArgs = (self._vehCD,)
        elif bool(self.shortage) and not self._hasUsedEnergy():
            specialAlias = TOOLTIPS_CONSTANTS.NOT_ENOUGH_MONEY
            specialArgs = (self.shortage, currency)
        else:
            specialAlias = alias
        return (specialAlias, specialArgs)

    def _getPannelMeta(self):
        currency, amount = self._getEnergyPrice()
        specialAlias, specialArgs = self._getTooltipInfo(currency, TOOLTIPS_CONSTANTS.EVENT_TANK_REPAIR_INFO)
        inStorage = ''
        if self._getEnergyFor() > 0:
            inStorage = backport.text(R.strings.event.hangar.crew_booster.panel.inStorage(), value=self._getEnergyFor())
        data = {'description': backport.text(R.strings.event.hangar.crew_healing.panel.header()),
         'cost': moneyWithIcon(Money.makeFrom(currency, amount), currType=currency),
         'tooltip': '',
         'specialArgs': specialArgs,
         'specialAlias': specialAlias,
         'isSpecial': True,
         'buttonEnabled': self._isApplyButtonEnabled(),
         'buttonLabel': backport.text(R.strings.event.hangar.crew_healing.panel.buttonLabel()),
         'icon': backport.image(R.images.gui.maps.icons.event.manageCrew.small.heal()),
         'inStorage': inStorage,
         'isActivated': False,
         'bgFrame': 'healing'}
        return data

    def _mayPurchaseWithExchange(self):
        currency, amount = self._getEnergyPrice()
        if currency == Currency.GOLD:
            return True
        rechargePrice = Money.makeFrom(currency, amount)
        rate = self.itemsCache.items.shop.exchangeRate
        money = self.itemsCache.items.stats.money
        exchangedMoney = money.exchange(Currency.GOLD, Currency.CREDITS, rate, default=0)
        shortage = exchangedMoney.getShortage(rechargePrice)
        return False if shortage else True

    def __hasAllVehiclesInInventoryEnergy(self):
        vehiclesInInventory = self._vehiclesController.getAllVehiclesInInventory()
        if not vehiclesInInventory:
            return False
        return False if any((True for compDesc in vehiclesInInventory if not self._vehiclesController.hasEnergy(purpose=FakeCrewHealing._ENERGY_ITEM_PURPOSE, vehTypeCompDescr=compDesc))) else True

    def __onVehicleSelected(self):
        if g_currentPreviewVehicle.isPresent():
            self._vehCD = None
        elif g_currentVehicle.isPresent():
            self._vehCD = g_currentVehicle.item.intCD
        self._update()
        return

    def __onTimeToRepairChanged(self, vehiclesTime):
        self.__vehiclesTime = vehiclesTime
        self._update()
        if vehiclesTime:
            if AccountSettings.getCounters(EVENT_COMMANDERS_READY_SEEN):
                AccountSettings.setCounters(EVENT_COMMANDERS_READY_SEEN, False)
            for time in vehiclesTime.itervalues():
                if time == 0:
                    self._callback.delayCallback(self._SHOW_HEALING_ALL_DELAY, self._showHealingAll)
                    break
