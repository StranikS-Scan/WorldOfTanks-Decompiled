# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/booster_buy_window.py
from gui import SystemMessages
from gui.Scaleform import MENU
from gui.Scaleform.daapi.view.meta.BoosterBuyWindowMeta import BoosterBuyWindowMeta
from gui.Scaleform.genConsts.SLOT_HIGHLIGHT_TYPES import SLOT_HIGHLIGHT_TYPES
from CurrentVehicle import g_currentVehicle
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.formatters import text_styles
from gui.shared.tooltips.formatters import packItemActionTooltipData
from gui.shared.utils.decorators import process
from gui.shared.utils import decorators
from gui.shared.gui_items.processors.module import ModuleBuyer
from gui.shared.gui_items.processors.vehicle import VehicleAutoBattleBoosterEquipProcessor
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class BoosterBuyWindow(BoosterBuyWindowMeta):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, ctx=None):
        super(BoosterBuyWindow, self).__init__()
        self.__item = self.itemsCache.items.getItemByCD(ctx['typeCompDescr'])
        self.__install = ctx['install']

    def onWindowClose(self):
        self.destroy()

    def buy(self, count):
        self.__buyItem(int(count))
        self.destroy()

    @decorators.process('loadStats')
    def setAutoRearm(self, autoRearm):
        vehicle = g_currentVehicle.item
        if vehicle is not None:
            yield VehicleAutoBattleBoosterEquipProcessor(vehicle, autoRearm).request()
        return

    def _populate(self):
        super(BoosterBuyWindow, self)._populate()
        if self.__item.isCrewBooster():
            isPerkReplace = not self.__item.isAffectedSkillLearnt(g_currentVehicle.item)
            desc = self.__item.getCrewBoosterAction(isPerkReplace)
            overlayType = SLOT_HIGHLIGHT_TYPES.BATTLE_BOOSTER_CREW_REPLACE if isPerkReplace else SLOT_HIGHLIGHT_TYPES.BATTLE_BOOSTER
        else:
            desc = self.__item.getOptDeviceBoosterDescription(g_currentVehicle.item)
            overlayType = SLOT_HIGHLIGHT_TYPES.BATTLE_BOOSTER
        self.as_setInitDataS({'windowTitle': MENU.BOOSTERBUYWINDOW_WINDOWTITLE,
         'nameText': text_styles.highTitle(self.__item.userName),
         'descText': text_styles.main(desc),
         'countLabelText': text_styles.main(MENU.BOOSTERBUYWINDOW_BUYCOUNT),
         'buyLabelText': text_styles.main(MENU.BOOSTERBUYWINDOW_TOTALPRICE),
         'totalPriceLabelText': text_styles.highlightText(MENU.BOOSTERBUYWINDOW_TOTALLABEL),
         'inHangarLabelText': text_styles.main(MENU.BOOSTERBUYWINDOW_INHANGARCOUNT),
         'boosterSlot': self.__getItemSlotData(self.__item, overlayType),
         'rearmCheckboxLabel': MENU.BOOSTERBUYWINDOW_REARMCHECKBOXLABEL,
         'rearmCheckboxTooltip': '',
         'submitBtnLabel': MENU.BOOSTERBUYWINDOW_BUYBUTTONLABEL,
         'cancelBtnLabel': MENU.BOOSTERBUYWINDOW_CANCELBUTTONLABEL})
        stats = self.itemsCache.items.stats
        itemPrice = self.__getItemPrice()
        currency = itemPrice.getCurrency(byWeight=True)
        vehicle = g_currentVehicle.item
        self.as_updateDataS({'actionPriceData': packItemActionTooltipData(self.__item, isBuying=True),
         'itemPrice': itemPrice.price.getSignValue(currency),
         'itemCount': self.__item.inventoryCount,
         'currency': currency,
         'currencyCount': stats.money.getSignValue(currency),
         'rearmCheckboxValue': vehicle.isAutoBattleBoosterEquip() if vehicle is not None else False})
        return

    @process('buyItem')
    def __buyItem(self, count):
        if self.__install and g_currentVehicle.isPresent():
            ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_AND_INSTALL_ITEM_VEHICLE_LAYOUT, g_currentVehicle.item, None, None, self.__item, count)
        else:
            currency = self.__getItemPrice().getCurrency(byWeight=True)
            result = yield ModuleBuyer(self.__item, count, currency).request()
            if result.userMsg:
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        return

    def __getItemPrice(self):
        return self.__item.getBuyPrice(preferred=False)

    @classmethod
    def __getItemSlotData(cls, item, overlayType):
        return {'overlayType': overlayType,
         'bgHighlightType': SLOT_HIGHLIGHT_TYPES.BATTLE_BOOSTER,
         'isBgVisible': False,
         'moduleType': item.getGUIEmblemID()}
