# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/ranked/page.py
from gui.Scaleform.daapi.view.battle.classic.page import ClassicPage
from gui.Scaleform.daapi.view.battle.shared.hint_panel.plugins import RoleHelpPlugin
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES

class RankedPage(ClassicPage):

    def _populate(self):
        super(RankedPage, self)._populate()
        self.__tryInitRoleDescription()

    def __tryInitRoleDescription(self):
        if RoleHelpPlugin.isAvailableToShow():
            self.as_createRoleDescriptionS()
            self._blToggling.add(BATTLE_VIEW_ALIASES.ROLE_DESCRIPTION)
            if self._isBattleLoading:
                self._setComponentsVisibility(hidden={BATTLE_VIEW_ALIASES.ROLE_DESCRIPTION})
