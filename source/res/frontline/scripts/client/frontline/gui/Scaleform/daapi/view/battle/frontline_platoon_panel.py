# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/Scaleform/daapi/view/battle/frontline_platoon_panel.py
from frontline.gui.Scaleform.daapi.view.meta.FrontlinePlatoonPanelMeta import FrontlinePlatoonPanelMeta
from helpers import i18n
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
_MAX_INVITES_DISPLAYED = 4

class FrontlinePlatoonPanel(FrontlinePlatoonPanelMeta):

    def _populate(self):
        super(FrontlinePlatoonPanel, self)._populate()
        self.as_setPlatoonTitleS(str(i18n.makeString(EPIC_BATTLE.SUPER_PLATOON_PANEL_TITLE)))
        self.as_setMaxDisplayedInviteMessagesS(_MAX_INVITES_DISPLAYED)

    def _handleNextMode(self, _):
        pass
