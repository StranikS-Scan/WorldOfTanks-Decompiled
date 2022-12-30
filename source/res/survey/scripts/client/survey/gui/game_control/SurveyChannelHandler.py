# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: survey/scripts/client/survey/gui/game_control/SurveyChannelHandler.py
import logging
from chat_shared import SYS_MESSAGE_TYPE
from gui.game_control.AwardController import ServiceChannelHandler
from gui.shared.event_dispatcher import findAndLoadWindow
from survey.gui.impl.lobby.survey.survey_view import SurveyViewWindow
_logger = logging.getLogger(__name__)

class SurveyChannelHandler(ServiceChannelHandler):

    def __init__(self, awardCtrl):
        super(SurveyChannelHandler, self).__init__(SYS_MESSAGE_TYPE.showSurvey.index(), awardCtrl)

    def _showAward(self, ctx):
        _, message = ctx
        arenaUniqueID = message.data.get('arenaUniqueID', 0)
        timeout = message.data.get('timeout', 0)
        if arenaUniqueID == 0 or timeout == 0:
            _logger.warning('Some survey data is 0. timeout: %s ArenaID: %s', timeout, arenaUniqueID)
            return
        findAndLoadWindow(False, SurveyViewWindow, arenaUniqueID, timeout)
