# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/game_control/awards_controller.py
from chat_shared import SYS_MESSAGE_TYPE
from fun_random.gui.feature.util.fun_mixins import FunProgressionWatcher
from gui.game_control.AwardController import ServiceChannelHandler
from helpers import dependency
from messenger.m_constants import SCH_CLIENT_MSG_TYPE
from skeletons.gui.system_messages import ISystemMessages

def _getMessage(ctx):
    _, message = ctx
    return message


class FunProgressionQuestsHandler(ServiceChannelHandler, FunProgressionWatcher):
    __systemMessages = dependency.descriptor(ISystemMessages)
    _CLIENT_MSG_TYPE = SCH_CLIENT_MSG_TYPE.FUN_RANDOM_PROGRESSION

    def __init__(self, awardCtrl):
        super(FunProgressionQuestsHandler, self).__init__(SYS_MESSAGE_TYPE.battleResults.index(), awardCtrl)

    def _showAward(self, ctx):
        self.__systemMessages.proto.serviceChannel.pushClientMessage(_getMessage(ctx), self._CLIENT_MSG_TYPE)

    def _needToShowAward(self, ctx):
        if super(FunProgressionQuestsHandler, self)._needToShowAward(ctx):
            return bool([ qID for qID in _getMessage(ctx).data.get('completedQuestIDs', set()) if self._funRandomCtrl.progressions.isProgressionExecutor(qID) ])
        return False
