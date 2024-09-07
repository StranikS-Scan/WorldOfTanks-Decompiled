# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/game_control/awards_controller.py
from armory_yard.gui.window_events import showArmoryYardRewardWindow
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_rewards_view_model import State
from armory_yard_constants import isArmoryYardStyleQuest
from chat_shared import SYS_MESSAGE_TYPE
from gui.game_control.AwardController import ServiceChannelHandler

class ArmoryYardStyleQuestsHandler(ServiceChannelHandler):

    def __init__(self, awardsCtrl):
        super(ArmoryYardStyleQuestsHandler, self).__init__(SYS_MESSAGE_TYPE.battleResults.index(), awardsCtrl)

    def _showAward(self, ctx):
        data = ctx[1].data
        armoryYardStyleQuests = self.eventsCache.getAllQuests(lambda q: isArmoryYardStyleQuest(q.getID()))
        for qID in data.get('completedQuestIDs', set()):
            if qID in armoryYardStyleQuests:
                rewards = data.get('detailedRewards', {}).get(qID)
                if 'customizations' in rewards:
                    showArmoryYardRewardWindow(rewards, State.STYLE)
