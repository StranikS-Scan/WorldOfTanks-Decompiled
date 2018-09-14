# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/PromoPremiumIgrWindow.py
from account_helpers.AccountSettings import AccountSettings, IGR_PROMO
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.daapi.view.meta.PromoPremiumIgrWindowMeta import PromoPremiumIgrWindowMeta
from gui.Scaleform.framework import AppRef
from gui.Scaleform.managers.UtilsManager import ImageUrlProperties
from helpers import i18n
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.framework.managers.TextManager import TextType

class PromoPremiumIgrWindow(AbstractWindowView, View, PromoPremiumIgrWindowMeta, AppRef):

    def __init__(self, ctx = None):
        super(PromoPremiumIgrWindow, self).__init__()

    def _populate(self):
        super(PromoPremiumIgrWindow, self)._populate()
        self.__initData()

    def onWindowClose(self):
        self.destroy()

    def _dispose(self):
        AccountSettings.setFilter(IGR_PROMO, {'wasShown': True})
        super(PromoPremiumIgrWindow, self)._dispose()

    def __initData(self):
        ms = i18n.makeString
        getTxt = self.app.utilsManager.textManager.getText
        igrIcon = RES_ICONS.MAPS_ICONS_LIBRARY_PREMIUM_SMALL
        icon = self.app.utilsManager.getHtmlIconText(ImageUrlProperties(igrIcon, 34, 16, -4))
        self.as_setWindowTitleS(ms(MENU.PROMOPREMIUMIGRWINDOW_WINDOWTITLE))
        self.as_setTitleS(getTxt(TextType.HIGH_TITLE, ms(MENU.PROMOPREMIUMIGRWINDOW_TITLE)))
        self.as_setTextS(getTxt(TextType.STANDARD_TEXT, ms(MENU.PROMOPREMIUMIGRWINDOW_TEXT, iconIgr=icon)))
        self.as_setApplyButtonLabelS(ms(MENU.PROMOPREMIUMIGRWINDOW_APPLYBUTTONLABEL))
