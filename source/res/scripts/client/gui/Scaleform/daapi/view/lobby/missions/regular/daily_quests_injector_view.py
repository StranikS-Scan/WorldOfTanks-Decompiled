# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/regular/daily_quests_injector_view.py
from gui.Scaleform.daapi.view.meta.MissionsPremiumViewMeta import MissionsPremiumViewMeta
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.lobby.missions.daily_quests_view import DailyQuestsView

class DailyQuestsInjectorView(InjectComponentAdaptor, MissionsPremiumViewMeta):
    __slots__ = ()

    def setDefaultTab(self, tabIdx):
        if self._injectView is not None:
            self._injectView.setDefaultTab(tabIdx)
        return

    def markVisited(self):
        if self._injectView is not None:
            self._injectView.markVisited()
            self._injectView.resetInfoPageVisibility()
        return

    def setProxy(self, proxy):
        if self._injectView is not None:
            self._injectView.setProxy(proxy)
        return

    def _makeInjectView(self):
        return DailyQuestsView()
