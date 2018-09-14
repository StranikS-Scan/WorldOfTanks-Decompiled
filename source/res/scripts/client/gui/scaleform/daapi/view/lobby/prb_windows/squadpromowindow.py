# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/prb_windows/SquadPromoWindow.py
from gui.Scaleform.daapi.settings import BUTTON_LINKAGES
from helpers.i18n import makeString as _ms
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.daapi.view.meta.SquadPromoWindowMeta import SquadPromoWindowMeta
from gui.Scaleform.genConsts.TEXT_ALIGN import TEXT_ALIGN

class SquadPromoWindow(SquadPromoWindowMeta):
    _BTN_WIDTH = 120
    _CLOSE_BTN_ACTION = 'closeAction'

    def __init__(self, ctx = None):
        super(SquadPromoWindow, self).__init__()

    def onBtnClick(self, action):
        if action == self._CLOSE_BTN_ACTION:
            self.onWindowClose()

    def onWindowClose(self):
        self.destroy()

    def _populate(self):
        super(SquadPromoWindow, self)._populate()
        self.as_setImageS(RES_ICONS.MAPS_ICONS_WINDOWS_MINICLIENT_SQUAD_WINDOW_BACKGROUND, 0)
        self.as_setWindowTitleS(_ms('#menu:headerButtons/btnLabel/inSquad'))
        self.as_setTextS(_ms('#miniclient:squad_promo_window/header'), _ms('#miniclient:squad_promo_window/description'))
        self.as_setHyperlinkS(_ms('#miniclient:personal_quests_welcome_view/continue_download'))
        self.as_setButtonsS([{'label': _ms('#quests:QuestsPersonalWelcomeView/btnLabel'),
          'btnLinkage': BUTTON_LINKAGES.BUTTON_NORMAL,
          'action': self._CLOSE_BTN_ACTION,
          'isFocused': True,
          'tooltip': ''}], TEXT_ALIGN.RIGHT, self._BTN_WIDTH)

    def _dispose(self):
        super(SquadPromoWindow, self)._dispose()
