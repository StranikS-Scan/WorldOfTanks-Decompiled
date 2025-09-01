# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/game_control/award_controller.py
from comp7_light.gui.comp7_light_constants import SCH_CLIENT_MSG_TYPE
from comp7_light.gui.shared.event_dispatcher import showBattleQuestAwardsWindow
from chat_shared import SYS_MESSAGE_TYPE
from gui.game_control.AwardController import PunishWindowHandler, ServiceChannelHandler
from helpers import dependency
from skeletons.gui.system_messages import ISystemMessages

class Comp7LightProgressionStageHandler(ServiceChannelHandler):
    __systemMessages = dependency.descriptor(ISystemMessages)
    _CLIENT_MSG_TYPE = SCH_CLIENT_MSG_TYPE.COMP7_LIGHT_PROGRESSION_NOTIFICATIONS

    def __init__(self, awardCtrl):
        super(Comp7LightProgressionStageHandler, self).__init__(SYS_MESSAGE_TYPE.comp7LightProgressionNotification.index(), awardCtrl)

    def _showAward(self, ctx):
        _, message = ctx
        stages = message.data.get('stages', set())
        for stage in stages:
            if stage.get('showAwardWindow', False):
                showBattleQuestAwardsWindow(stage)

        self._showMessages(ctx)

    def _showMessages(self, ctx):
        self.__systemMessages.proto.serviceChannel.pushClientMessage(self._getMessage(ctx), self._CLIENT_MSG_TYPE)

    @staticmethod
    def _getMessage(ctx):
        _, message = ctx
        return message


class Comp7LightPunishWindowHandler(PunishWindowHandler):

    @property
    def channelType(self):
        return SYS_MESSAGE_TYPE.comp7LightBattleResults.index()
