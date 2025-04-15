# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/daily/daily_quests_model_helpers.py
import typing
from constants import DailyQuestsLevels
from gui.impl.gen.view_models.common.missions.event_model import EventStatus
from gui.shared.missions.packers.events import getEventUIDataPacker
from helpers import dependency
from skeletons.gui.game_control import IWotPlusController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
if typing.TYPE_CHECKING:
    from typing import Dict
    from gui.impl.gen.view_models.common.missions.daily_quest_model import DailyQuestModel
    from gui.server_events.event_items import DailyTokenQuest

@dependency.replace_none_kwargs(subscriptionController=IWotPlusController, lobbyContext=ILobbyContext, eventsCache=IEventsCache)
def addSubscriptionBonusesToQuest(questModel, subsQuestsByLevels, subscriptionController=None, lobbyContext=None, eventsCache=None):
    subscriptionEnabled = subscriptionController.isWotPlusEnabled()
    isEnableSubsQuest = lobbyContext.getServerSettings().isDailyQuestsExtraRewardsEnabled()
    if isEnableSubsQuest and subscriptionEnabled:
        quest = eventsCache.getQuestByID(questModel.getId())
        subsQuestLevel = DailyQuestsLevels.MAP_DAILY_QUESTS.get(quest.getLevel(), None)
        subsQuest = subsQuestsByLevels.get(subsQuestLevel, None)
        if subsQuest is not None:
            packer = getEventUIDataPacker(subsQuest)
            packer.pack(model=questModel)
            if quest.isCompleted() and not subsQuest.isCompleted():
                questModel.setStatus(EventStatus.UNDONESUBSCRIPTION)
    return
