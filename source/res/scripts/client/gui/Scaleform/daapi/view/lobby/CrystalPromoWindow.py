# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/CrystalPromoWindow.py
from account_helpers.AccountSettings import AccountSettings, BOOSTERS, KNOWN_SELECTOR_BATTLES, SHOW_CRYSTAL_HEADER_BAND
from gui.Scaleform.daapi.view.meta.CrystalsPromoWindowMeta import CrystalsPromoWindowMeta
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS

class CrystalsPromoWindow(CrystalsPromoWindowMeta):

    def __init__(self, ctx=None):
        super(CrystalsPromoWindow, self).__init__()

    def onWindowClose(self):
        self.destroy()

    def _dispose(self):
        super(CrystalsPromoWindow, self)._dispose()

    def _populate(self):
        super(CrystalsPromoWindow, self)._populate()
        if AccountSettings.getSettings(SHOW_CRYSTAL_HEADER_BAND):
            AccountSettings.setSettings(SHOW_CRYSTAL_HEADER_BAND, False)
        self.as_setDataS({'windowTitle': MENU.CRYSTALS_PROMOWINDOW_TITLE,
         'headerTF': MENU.CRYSTALS_PROMOWINDOW_HEADER,
         'subTitle0': MENU.CRYSTALS_PROMOWINDOW_SUBTITLE0,
         'subDescr0': MENU.CRYSTALS_PROMOWINDOW_SUBDESCR0,
         'subTitle1': MENU.CRYSTALS_PROMOWINDOW_SUBTITLE1,
         'subDescr1': MENU.CRYSTALS_PROMOWINDOW_SUBDESCR1,
         'subTitle2': MENU.CRYSTALS_PROMOWINDOW_SUBTITLE2,
         'subDescr2': MENU.CRYSTALS_PROMOWINDOW_SUBDESCR2,
         'closeBtn': MENU.CRYSTALS_PROMOWINDOW_CLOSEBTN,
         'image0': RES_ICONS.MAPS_ICONS_BATTLETYPES_64X64_RANKED,
         'image1': RES_ICONS.MAPS_ICONS_LIBRARY_CRYSTAL_80X80,
         'image2': RES_ICONS.MAPS_ICONS_MODULES_LISTOVERLAYSMALL,
         'bg': RES_ICONS.MAPS_ICONS_WINDOWS_CRYSTALSPROMOBG})
