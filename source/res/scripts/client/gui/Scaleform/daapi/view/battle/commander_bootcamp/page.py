# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/commander_bootcamp/page.py
from bootcamp.BootCampEvents import g_bootcampEvents
from gui.Scaleform.daapi.view.battle.commander import page as cpage
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES

class BCCommanderBattlePage(cpage.CommonCommanderBattlePage):

    def __init__(self):
        super(BCCommanderBattlePage, self).__init__(cpage.CommonRTSComponentsConfig() + cpage.BASE_COMMANDER_EXTENDED_CMPNTS)

    @property
    def topHint(self):
        return self.getComponent(BATTLE_VIEW_ALIASES.BOOTCAMP_BATTLE_TOP_HINT)

    def _populate(self):
        super(BCCommanderBattlePage, self)._populate()
        g_bootcampEvents.onBattleComponentVisibility += self.__onComponentVisibilityEvent

    def _dispose(self):
        g_bootcampEvents.onBattleComponentVisibility -= self.__onComponentVisibilityEvent
        super(BCCommanderBattlePage, self)._dispose()

    def __onComponentVisibilityEvent(self, name, isVisible):
        if isVisible:
            self._setComponentsVisibility(visible={name}, hidden=set())
        else:
            self._setComponentsVisibility(visible=set(), hidden={name})
        self.__setComponentEnabled(name, isVisible)

    def __setComponentEnabled(self, name, enable):
        if name == BATTLE_VIEW_ALIASES.SIXTH_SENSE:
            component = self.getComponent(BATTLE_VIEW_ALIASES.SIXTH_SENSE)
            if component is not None:
                component.enabled = enable
        return
