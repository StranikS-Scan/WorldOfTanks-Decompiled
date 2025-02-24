# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/missions/daily_quests_view.py
from gui.impl.lobby.missions.daily_quests_view import DailyQuestsView
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller

class Comp7DailyQuestsView(DailyQuestsView):
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def _getEvents(self):
        result = super(Comp7DailyQuestsView, self)._getEvents()
        result = list(result)
        result.append((self.__comp7Controller.onComp7ConfigChanged, self.__updateComp7Data))
        return result

    def _updateCommonData(self, *_):
        super(Comp7DailyQuestsView, self)._updateCommonData(*_)
        self.__updateComp7Data()

    def __updateComp7Data(self, *_):
        self.viewModel.setIsComp7Active(self.__comp7Controller.isEnabled())
