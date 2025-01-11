# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/game_control/awards_controller.py
from chat_shared import SYS_MESSAGE_TYPE
from gui.game_control.AwardController import PunishWindowHandler, MultiTypeServiceChannelHandler
from grinch.gui.grinch_gui_constants import SCH_CLIENT_MSG_TYPE
from helpers import dependency
from grinch_progression.gui.impl.lobby.views.quests_helper import isGrinchWeekendQuestID, isSpecialQuestQuest, isGrinchRandom
from skeletons.gui.system_messages import ISystemMessages

class GrinchPunishWindowHandler(PunishWindowHandler):

    @property
    def channelType(self):
        return SYS_MESSAGE_TYPE.grinchBattleResults.index()


def _getMessage(ctx):
    _, message = ctx
    return message


class GrinchRewardsHandler(MultiTypeServiceChannelHandler):
    _CLIENT_MSG_TYPE = SCH_CLIENT_MSG_TYPE.GRINCH_EVENT_PROGRESSION
    __systemMessages = dependency.descriptor(ISystemMessages)

    def __init__(self, awardCtrl):
        super(GrinchRewardsHandler, self).__init__((SYS_MESSAGE_TYPE.battleResults.index(), SYS_MESSAGE_TYPE.grinchBattleResults.index()), awardCtrl)

    def _showAward(self, ctx):
        self.__systemMessages.proto.serviceChannel.pushClientMessage(_getMessage(ctx), self._CLIENT_MSG_TYPE)

    def _needToShowAward(self, ctx):
        if not super(GrinchRewardsHandler, self)._needToShowAward(ctx):
            return False
        return bool([ qID for qID in _getMessage(ctx).data.get('completedQuestIDs', set()) if isGrinchWeekendQuestID(qID) or isSpecialQuestQuest(qID) or isGrinchRandom(qID) ])
