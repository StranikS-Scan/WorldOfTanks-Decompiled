# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/CrystalPromoWindow.py
from gui.Scaleform.daapi.view.lobby.store.browser.ingameshop_helpers import getBonsUrl, isIngameShopEnabled
from gui.Scaleform.daapi.view.meta.CrystalsPromoWindowMeta import CrystalsPromoWindowMeta
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared.event_dispatcher import showWebShop, showOldShop

class CrystalsPromoWindow(CrystalsPromoWindowMeta):

    def __init__(self, ctx=None):
        super(CrystalsPromoWindow, self).__init__()

    def onWindowClose(self):
        self.destroy()

    def _populate(self):
        super(CrystalsPromoWindow, self)._populate()
        self.as_setDataS({'windowTitle': MENU.CRYSTALS_PROMOWINDOW_TITLE,
         'headerTF': MENU.CRYSTALS_PROMOWINDOW_HEADER,
         'subTitle0': MENU.CRYSTALS_PROMOWINDOW_SUBTITLE0,
         'subDescr0': MENU.CRYSTALS_PROMOWINDOW_SUBDESCR0,
         'subTitle1': MENU.CRYSTALS_PROMOWINDOW_SUBTITLE1,
         'subDescr1': MENU.CRYSTALS_PROMOWINDOW_SUBDESCR1,
         'subTitle2': MENU.CRYSTALS_PROMOWINDOW_SUBTITLE2,
         'subDescr2': MENU.CRYSTALS_PROMOWINDOW_SUBDESCR2,
         'closeBtn': MENU.CRYSTALS_PROMOWINDOW_CLOSEBTN,
         'openShopBtnLabel': MENU.CRYSTALS_PROMOWINDOW_OPENSHOPBTNLABEL,
         'image0': RES_ICONS.MAPS_ICONS_BATTLETYPES_64X64_RANKED_EPICRANDOM,
         'image1': RES_ICONS.MAPS_ICONS_LIBRARY_CRYSTAL_80X80,
         'image2': RES_ICONS.MAPS_ICONS_MODULES_LISTOVERLAYSMALL,
         'bg': RES_ICONS.MAPS_ICONS_WINDOWS_CRYSTALSPROMOBG,
         'showOpenShopBtn': isIngameShopEnabled()})

    def onOpenShop(self):
        if isIngameShopEnabled():
            showWebShop(getBonsUrl())
        else:
            showOldShop(ctx={'tabId': STORE_CONSTANTS.SHOP,
             'component': STORE_CONSTANTS.BATTLE_BOOSTER})
        self.destroy()
