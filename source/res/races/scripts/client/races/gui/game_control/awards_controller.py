# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/game_control/awards_controller.py
import typing
from chat_shared import SYS_MESSAGE_TYPE
from races.skeletons.progression_controller import IRacesProgressionController
from gui.game_control.AwardController import ServiceChannelHandler
from gui.impl.pub.notification_commands import WindowNotificationCommand
from helpers import dependency
from skeletons.gui.impl import INotificationWindowController
from skeletons.gui.system_messages import ISystemMessages
from races.gui.impl.lobby.rewards_views.races_rewards_view import RacesRewardsWindow
from races.gui.game_control.progression_controller import QUEST_STEP_REGEX, WELCOME_QUEST_REGEX
if typing.TYPE_CHECKING:
    from typing import Tuple, List
    from messenger.proto.bw.wrappers import ServiceChannelMessage
    from skeletons.gui.game_control import IAwardController

class RacesProgressionTokenQuestsHandler(ServiceChannelHandler):
    _notificationMgr = dependency.descriptor(INotificationWindowController)
    _systemMessages = dependency.descriptor(ISystemMessages)
    _racesProgression = dependency.descriptor(IRacesProgressionController)

    def __init__(self, awardCtrl):
        super(RacesProgressionTokenQuestsHandler, self).__init__(SYS_MESSAGE_TYPE.tokenQuests.index(), awardCtrl)

    def _showAward(self, ctx):
        _, message = ctx
        completedQuestsIDs = [ questID for questID in message.data.get('completedQuestIDs', set()) if QUEST_STEP_REGEX.match(questID) or WELCOME_QUEST_REGEX.match(questID) ]
        allQuests = self._racesProgression.getQuestsForAwardsScreen()
        progressionQuests = []
        for questID in completedQuestsIDs:
            progressionQuests.append(allQuests[questID])

        window = RacesRewardsWindow(quests=progressionQuests)
        self._notificationMgr.append(WindowNotificationCommand(window))

    def _needToShowAward(self, ctx):
        if not super(RacesProgressionTokenQuestsHandler, self)._needToShowAward(ctx):
            return False
        _, message = ctx
        isRacesQuest = self._racesProgression.isRacesProgressionQuest
        completedQuestIDs = message.data.get('completedQuestIDs', set())
        return any((isRacesQuest(questID) for questID in completedQuestIDs))


class RacesWelcomeQuestHandler(ServiceChannelHandler):
    _systemMessages = dependency.descriptor(ISystemMessages)
    _notificationMgr = dependency.descriptor(INotificationWindowController)
    _racesProgression = dependency.descriptor(IRacesProgressionController)

    def __init__(self, awardCtrl):
        super(RacesWelcomeQuestHandler, self).__init__(SYS_MESSAGE_TYPE.tokenQuests.index(), awardCtrl)

    def _showAward(self, ctx):
        _, message = ctx
        completedQuestsIDs = [ questID for questID in message.data.get('completedQuestIDs', set()) if WELCOME_QUEST_REGEX.match(questID) ]
        allQuests = self._racesProgression.getWelcomeQuestForAwardsScreen()
        for questID in completedQuestsIDs:
            progressionQuests = [allQuests[questID]]
            window = RacesRewardsWindow(quests=progressionQuests)
            self._notificationMgr.append(WindowNotificationCommand(window))

    def _needToShowAward(self, ctx):
        _, message = ctx
        if not super(RacesWelcomeQuestHandler, self)._needToShowAward(ctx):
            return False
        isRacesWelcomeQuest = self._racesProgression.isRacesWelcomeQuest
        completedQuestIDs = message.data.get('completedQuestIDs', set())
        return any((isRacesWelcomeQuest(questID) for questID in completedQuestIDs))


class RacesFirstWinQuestHandler(ServiceChannelHandler):
    _systemMessages = dependency.descriptor(ISystemMessages)
    _notificationMgr = dependency.descriptor(INotificationWindowController)
    _racesProgression = dependency.descriptor(IRacesProgressionController)

    def __init__(self, awardCtrl):
        super(RacesFirstWinQuestHandler, self).__init__(SYS_MESSAGE_TYPE.RacesBattleResults.index(), awardCtrl)

    def _showAward(self, ctx):
        allQuests = self._racesProgression.getFirstWinQuestForAwardsScreen()
        for key, _ in allQuests.iteritems():
            firstWinQuest = [allQuests[key]]
            window = RacesRewardsWindow(quests=firstWinQuest)
            self._notificationMgr.append(WindowNotificationCommand(window))

    def _needToShowAward(self, ctx):
        if not super(RacesFirstWinQuestHandler, self)._needToShowAward(ctx):
            return False
        _, message = ctx
        isRacesFirstWin = self._racesProgression.isRacesFirstWinQuest
        completedQuestIDs = message.data.get('completedQuestIDs', set())
        return any((isRacesFirstWin(questID) for questID in completedQuestIDs))
