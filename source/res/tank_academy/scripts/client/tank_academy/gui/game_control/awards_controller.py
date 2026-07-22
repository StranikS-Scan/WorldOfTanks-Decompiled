# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tank_academy/scripts/client/tank_academy/gui/game_control/awards_controller.py
from chat_shared import SYS_MESSAGE_TYPE
from helpers import dependency
from gui.game_control.AwardController import MultiTypeServiceChannelHandler
from skeletons.gui.game_control import ITankAcademyController
from skeletons.gui.system_messages import ISystemMessages
from tank_academy.gui.gui_constants import SCH_CLIENT_MSG_TYPE
from tank_academy.gui.server_events.events_helpers import isTankAcademyQuestID

class TankAcademyQuestsHandler(MultiTypeServiceChannelHandler):
    __tankAcademyController = dependency.descriptor(ITankAcademyController)
    __systemMessages = dependency.descriptor(ISystemMessages)

    def __init__(self, awardCtrl):
        super(TankAcademyQuestsHandler, self).__init__((SYS_MESSAGE_TYPE.hangarQuests.index(), SYS_MESSAGE_TYPE.tokenQuests.index(), SYS_MESSAGE_TYPE.battleResults.index()), awardCtrl)

    def _showAward(self, ctx):
        _, message = ctx
        if message.type == SYS_MESSAGE_TYPE.battleResults.index():
            self.__systemMessages.proto.serviceChannel.pushClientMessage(message, SCH_CLIENT_MSG_TYPE.TANK_ACADEMY_BATTLE_AWARD)
        self.__tankAcademyController.showAwardView(message.data)

    def _needToShowAward(self, ctx):
        _, message = ctx
        if not super(TankAcademyQuestsHandler, self)._needToShowAward(ctx):
            return False
        self.__markPostBattleAutoShowSuppressed(message)
        return self.__hasTankAcademyCompletedQuest(message.data)

    def __markPostBattleAutoShowSuppressed(self, message):
        if message.type != SYS_MESSAGE_TYPE.battleResults.index():
            return False
        if self.__hasTankAcademyCompletedQuest(message.data) or message.data.get('isActionTokenAdded', False):
            arenaUniqueID = message.data.get('arenaUniqueID')
            if arenaUniqueID:
                self.__tankAcademyController.markPostBattleAutoShowSuppressed(arenaUniqueID)
                return True
        return False

    @staticmethod
    def __hasTankAcademyCompletedQuest(data):
        completedQuestIDs = data.get('completedQuestIDs', set())
        return any((isTankAcademyQuestID(qID) for qID in completedQuestIDs))
