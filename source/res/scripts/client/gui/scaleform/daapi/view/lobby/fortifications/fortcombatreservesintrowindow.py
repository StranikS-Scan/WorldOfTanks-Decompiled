# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortCombatReservesIntroWindow.py
from helpers.i18n import makeString as _ms
from gui.Scaleform.daapi.view.meta.FortCombatReservesIntroMeta import FortCombatReservesIntroMeta
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS

class FortCombatReservesIntroWindow(FortCombatReservesIntroMeta):

    def _populate(self):
        super(FortCombatReservesIntroWindow, self)._populate()
        self.as_setDataS({'windowTitle': _ms(FORTIFICATIONS.FORTCOMBATRESERVESINTROWINDOW_WINDOWTITLE),
         'title': _ms(FORTIFICATIONS.FORTCOMBATRESERVESINTROWINDOW_TITLE),
         'description': _ms(FORTIFICATIONS.FORTCOMBATRESERVESINTROWINDOW_DESCRIPTION),
         'buttonLabel': _ms(FORTIFICATIONS.FORTNOTCOMMANDERFIRSTENTERWINDOW_APPLYBTNLABEL),
         'items': [{'imageSource': RES_ICONS.MAPS_ICONS_ORDERS_BIG_ARTILLERY,
                    'title': _ms(FORTIFICATIONS.FORTCOMBATRESERVESINTROWINDOW_ARTILLERY_TITLE),
                    'description': _ms(FORTIFICATIONS.FORTCOMBATRESERVESINTROWINDOW_ARTILLERY_DESCRIPTION)}, {'imageSource': RES_ICONS.MAPS_ICONS_ORDERS_BIG_BOMBER,
                    'title': _ms(FORTIFICATIONS.FORTCOMBATRESERVESINTROWINDOW_BOMBER_TITLE),
                    'description': _ms(FORTIFICATIONS.FORTCOMBATRESERVESINTROWINDOW_BOMBER_DESCRIPTION)}]})

    def onWindowClose(self):
        self.destroy()
