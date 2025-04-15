# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/tab_content.py
from gui.Scaleform.daapi.view.meta.TabContentMeta import TabContentMeta
from gui.impl.battle.battle_page.tab_view import TabView
from gui.impl.gen import R

class TabContent(TabContentMeta):

    def _onPopulate(self):
        self._createInjectView()

    def _makeInjectView(self):
        self.__view = TabView(R.views.battle.battle_page.TabView())
        return self.__view

    def onTabChanged(self, tabAlias):
        self.__view.handleTabChange(tabAlias)
