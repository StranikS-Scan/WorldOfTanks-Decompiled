# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light_progression/scripts/client/comp7_light_progression/gui/game_control/awards_controller.py
from comp7_light_progression.gui.gui_constants import SM_TYPE_COMP7_LIGHT_PROGRESSION, SCH_CLIENT_MSG_TYPE
from comp7_light_progression.gui.shared.event_dispatcher import showAwardsView
from chat_shared import SYS_MESSAGE_TYPE
from gui.game_control.AwardController import ServiceChannelHandler
from helpers import dependency
from skeletons.gui.system_messages import ISystemMessages

def _getMessage(ctx):
    _, message = ctx
    return message


class Comp7LightProgressionStageHandler(ServiceChannelHandler):
    __systemMessages = dependency.descriptor(ISystemMessages)
    _CLIENT_MSG_TYPE = SCH_CLIENT_MSG_TYPE.COMP7_LIGHT_PROGRESSION_NOTIFICATIONS

    def __init__(self, awardCtrl):
        super(Comp7LightProgressionStageHandler, self).__init__(SYS_MESSAGE_TYPE.__getattr__(SM_TYPE_COMP7_LIGHT_PROGRESSION).index(), awardCtrl)

    def _showAward(self, ctx):
        _, message = ctx
        stages = message.data.get('stages', set())
        for stage in stages:
            if stage.get('showAwardWindow', False):
                showAwardsView(stage)

        self._showMessages(ctx)

    def _showMessages(self, ctx):
        self.__systemMessages.proto.serviceChannel.pushClientMessage(_getMessage(ctx), self._CLIENT_MSG_TYPE)
