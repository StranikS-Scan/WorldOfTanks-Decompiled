# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenter/events/quests.py
import typing
from operator import itemgetter
from gui.server_events.events_helpers import isWhiteTigerQuest
from gui.wt_event.wt_event_quests_packers import WtEventQuestUIDataPacker
from helpers import dependency
from skeletons.gui.game_control import IQuestsController
if typing.TYPE_CHECKING:
    from gui.battle_results.reusable import ReusableInfo
    from gui.impl.gen.view_models.views.lobby.postbattle.events.base_event_model import BaseEventModel

def getQuestsEvents(reusable, result, tooltipData):
    questController = dependency.instance(IQuestsController)
    events = []
    questIds = []
    questsProgress = sorted([ (quest, isComplete) for quest, _, _, _, isComplete in reusable.progress.getPlayerQuestProgress() ], key=itemgetter(1), reverse=True)
    for quest, isComplete in questsProgress:
        packer = WtEventQuestUIDataPacker(quest)
        events.append(packer.pack(tooltipData=tooltipData, isComplete=isComplete))
        questIds.append(quest.getID())

    for _, vehicle in reusable.personal.getVehicleItemsIterator():
        quests = [ q for q in questController.getQuestForVehicle(vehicle) if isWhiteTigerQuest(q.getGroupID()) and q.getID() not in questIds and not q.isCompleted() ]
        for quest in quests:
            packer = WtEventQuestUIDataPacker(quest)
            events.append(packer.pack(tooltipData=tooltipData))
            questIds.append(quest.getID())

    return events
