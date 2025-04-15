# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale_progression/scripts/client/battle_royale_progression/gui/game_control/awards_controller.py
from battle_royale_progression.gui.shared.event_dispatcher import showAwardsView
from chat_shared import SYS_MESSAGE_TYPE
from gui.game_control.AwardController import ServiceChannelHandler
from helpers import dependency
from skeletons.gui.system_messages import ISystemMessages

def _getMessage(ctx):
    _, message = ctx
    return message


class BRProgressionStageHandler(ServiceChannelHandler):
    __systemMessages = dependency.descriptor(ISystemMessages)

    def __init__(self, awardCtrl):
        super(BRProgressionStageHandler, self).__init__(SYS_MESSAGE_TYPE.BRProgressionNotification.index(), awardCtrl)

    def _showAward(self, ctx):
        _, message = ctx
        stages = message.data.get('stages', set())
        for stage in stages:
            if stage.get('showAwardWindow', False):
                showAwardsView(stage)
