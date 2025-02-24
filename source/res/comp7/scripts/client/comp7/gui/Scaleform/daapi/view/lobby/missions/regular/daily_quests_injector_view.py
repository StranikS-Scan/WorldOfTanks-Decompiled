# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/Scaleform/daapi/view/lobby/missions/regular/daily_quests_injector_view.py
from comp7.gui.impl.lobby.missions.daily_quests_view import Comp7DailyQuestsView
from gui.Scaleform.daapi.view.lobby.missions.regular.daily_quests_injector_view import DailyQuestsInjectorView

class Comp7DailyQuestsInjectorView(DailyQuestsInjectorView):

    def _makeInjectView(self):
        return Comp7DailyQuestsView()
