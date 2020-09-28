# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenter/events/common.py
import typing
from gui.battle_results.presenter.events.battle_pass import getBattlePassEvents
from gui.battle_results.presenter.events.quests import getQuestsEvents
from gui.battle_results.presenter.events.ranked import getRankedEvents
from gui.battle_results.presenter.events.research import getResearchEvents
if typing.TYPE_CHECKING:
    from gui.battle_results.reusable import ReusableInfo
    from gui.impl.gen.view_models.views.lobby.postbattle.events.events_stats_model import EventsStatsModel
    from gui.impl.gen.view_models.views.lobby.postbattle.events.base_event_model import BaseEventModel

def _getEventsDataProviders():
    return [getRankedEvents,
     getBattlePassEvents,
     getQuestsEvents,
     getResearchEvents]


def setEventsData(model, reusable, result, tooltipData=None):
    dataProviders = _getEventsDataProviders()
    for provider in dataProviders:
        dataItems = provider(reusable, result, tooltipData)
        if dataItems is None:
            continue
        for data in dataItems:
            model.getEvents().addViewModel(data)

    return
