# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/messenger/formatters/service_channel.py
from adisp import adisp_async, adisp_process
from gui.impl import backport
from gui.impl.gen import R
from helpers import time_utils
from messenger import g_settings
from messenger.formatters import TimeFormatter
from messenger.formatters.service_channel import BattleResultsFormatter, ServiceChannelFormatter
from messenger.formatters.service_channel_helpers import MessageData
from story_mode_common.story_mode_constants import FIRST_MISSION_ID

class StoryModeResultsFormatter(BattleResultsFormatter):
    _battleResultKeys = {-1: 'storyModeBattleDefeatResult',
     0: 'storyModeBattleDefeatResult',
     1: 'storyModeBattleVictoryResult'}

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isForceOnboarding = message.data.get('isForceOnboarding', False)
        if isForceOnboarding:
            callback([])
        else:
            messages = yield super(StoryModeResultsFormatter, self).format(message)
            callback(messages)

    def _prepareFormatData(self, message, guiType=0):
        templateName, ctx = super(StoryModeResultsFormatter, self)._prepareFormatData(message)
        missionId = message.data.get('missionId', FIRST_MISSION_ID)
        ctx['scenarioName'] = backport.text(R.strings.sm_battle.prebattle.mission.title.num(missionId)())
        return (templateName, ctx)


class StoryModeAwardFormatter(ServiceChannelFormatter):
    __TEMPLATE = 'storyModeAwardMessage'

    def format(self, message, *args):
        medal = message.data['medal']
        formatted = g_settings.msgTemplates.format(self.__TEMPLATE, {'at': TimeFormatter.getLongDatetimeFormat(time_utils.makeLocalServerTime(message.sentTime)),
         'medal_name': backport.text(R.strings.achievements.dyn(medal)())})
        return [MessageData(formatted, self._getGuiSettings(message, self.__TEMPLATE))]
