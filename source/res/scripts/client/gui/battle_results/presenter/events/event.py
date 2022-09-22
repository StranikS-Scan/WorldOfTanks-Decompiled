# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenter/events/event.py
import typing
from gui.impl.gen.view_models.views.lobby.postbattle.events.wt_event_quest_model import WtEventQuestModel
from gui.server_events.event_items import WtQuest
from gui.server_events.events_helpers import EVENT_STATUS
from gui.wt_event.wt_event_helpers import isWtEventBattleQuest
from gui.wt_event.wt_event_quest_data_packer import WTEventBattleQuestUIDataPacker
from helpers import dependency
from skeletons.gui.game_control import IQuestsController
if typing.TYPE_CHECKING:
    from gui.battle_results.reusable import ReusableInfo
    from gui.impl.gen.view_models.views.lobby.postbattle.events.base_event_model import BaseEventModel

def getEvents(tooltipData, reusable, result):
    questController = dependency.instance(IQuestsController)
    questsProgress = reusable.progress.getPlayerQuestProgress()
    events = []
    curQuestIDs = []
    for e, pCur, _, _, isCompleted in questsProgress:
        event = WtQuest(e.getID(), e.getData(), pCur)
        packer = WTEventBattleQuestUIDataPacker(event)
        model = WtEventQuestModel()
        events.append(packer.pack(model))
        tooltipData[event.getID()] = packer.getTooltipData()
        curQuestIDs.append(event.getID())
        if isCompleted:
            model.setStatus(EVENT_STATUS.COMPLETED)

    for _, vehicle in reusable.personal.getVehicleItemsIterator():
        quests = [ q for q in questController.getQuestForVehicle(vehicle) if isWtEventBattleQuest(q.getID()) and q.getID() not in curQuestIDs and not q.isHidden() ]
        for quest in quests:
            packer = WTEventBattleQuestUIDataPacker(quest)
            model = WtEventQuestModel()
            events.append(packer.pack(model))
            tooltipData[quest.getID()] = packer.getTooltipData()
            if quest.isCompleted():
                model.setStatus(EVENT_STATUS.COMPLETED)

    return events
