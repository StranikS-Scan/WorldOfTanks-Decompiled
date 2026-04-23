# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/skeletons/gui/quests_controller.py
import typing
from skeletons.gui.game_control import IGameController
if typing.TYPE_CHECKING:
    from Event import Event
    from historical_battles.gui.server_events.battle_quests.quests_container import HBQuestsContainer

class IHBQuestsController(IGameController):
    onQuestsUpdated = None
    onDailyQuestUpdate = None

    def getQuestsContainer(self):
        raise NotImplementedError
