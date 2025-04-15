# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/gui/game_control/award_controller_handlers.py
import logging
from chat_shared import SYS_MESSAGE_TYPE
from gui.game_control.AwardController import ServiceChannelHandler
from resource_well.gui.shared.event_dispatcher import showResourceWellAwardWindow
_logger = logging.getLogger(__name__)

class ResourceWellRewardHandler(ServiceChannelHandler):

    def __init__(self, awardCtrl):
        super(ResourceWellRewardHandler, self).__init__(SYS_MESSAGE_TYPE.resourceWellReward.index(), awardCtrl)

    def _needToShowAward(self, ctx):
        if not super(ResourceWellRewardHandler, self)._needToShowAward(ctx):
            return False
        _, message = ctx
        if not message.data.get('rewardID', ''):
            _logger.error('RewardID is not found.')
            return False
        return True

    def _showAward(self, ctx):
        _, message = ctx
        showResourceWellAwardWindow(message.data['rewardID'], serialNumber=message.data.get('serialNumber', ''))
