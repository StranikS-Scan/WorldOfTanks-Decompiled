# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/messenger/formatters/service_channel.py
from adisp import adisp_async, adisp_process
from constants import SCENARIO_RESULT
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items import getItemTypeID
from helpers import time_utils, dependency
from messenger import g_settings
from messenger.formatters import TimeFormatter
from messenger.formatters.service_channel import BattleResultsFormatter, ServiceChannelFormatter
from messenger.formatters.service_channel_helpers import MessageData
from story_mode_common.story_mode_constants import FIRST_MISSION_ID
from story_mode.gui.shared.utils import getRewardList, getTasksCount
from story_mode.skeletons.story_mode_controller import IStoryModeController
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.game_control import IBattlePassController

class StoryModeResultsFormatter(BattleResultsFormatter):
    _storyModeCtrl = dependency.descriptor(IStoryModeController)
    _battleResultsService = dependency.descriptor(IBattleResultsService)
    _customizationService = dependency.descriptor(ICustomizationService)
    _battlePass = dependency.descriptor(IBattlePassController)

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isForceOnboarding = message.data.get('isForceOnboarding', False)
        if isForceOnboarding:
            callback([])
        else:
            messages = yield super(StoryModeResultsFormatter, self).format(message)
            callback(messages)

    def _prepareFormatData(self, message):
        missionId = message.data.get('missionId', FIRST_MISSION_ID)
        isOnboarding = self._storyModeCtrl.missions.isOnboarding(missionId)
        if isOnboarding:
            self._battleResultKeys = {SCENARIO_RESULT.LOSE: 'storyModeOnboardingBattleDefeatResult',
             SCENARIO_RESULT.PARTIAL: 'storyModeOnboardingBattleDefeatResult',
             SCENARIO_RESULT.WIN: 'storyModeOnboardingBattleVictoryResult'}
        else:
            self._battleResultKeys = {SCENARIO_RESULT.LOSE: 'storyModeRegularBattleDefeatResult',
             SCENARIO_RESULT.PARTIAL: 'storyModeRegularBattleDefeatResult',
             SCENARIO_RESULT.WIN: 'storyModeRegularBattleVictoryResult'}
        templateName, ctx = super(StoryModeResultsFormatter, self)._prepareFormatData(message)
        ctx['scenarioName'] = backport.text(R.strings.sm_battle.prebattle.mission.title.num(missionId)())
        if isOnboarding:
            return (templateName, ctx)
        ctx['missionsStr'] = ''
        ctx['xpStr'] = ''
        ctx['bpPointsStr'] = ''
        ctx['crystalStr'] = ''
        ctx['creditsStr'] = ''
        ctx['rewardStr'] = ''
        progressionInfo = message.data.get('progressionInfo', {})
        rewardList = getRewardList(progressionInfo, self._battlePass.isActive())
        completedTasksCount, tasksToCompleteCount = getTasksCount(progressionInfo)
        if tasksToCompleteCount:
            ctx['missionsStr'] = g_settings.htmlTemplates.format('missionCompleted', {'completedTasksCount': completedTasksCount,
             'tasksToCompleteCount': tasksToCompleteCount})
        freeXP = 0
        credits = 0
        bpPoints = 0
        crystal = 0
        customizations = []
        for reward in rewardList:
            credits += reward.get('credits', 0)
            freeXP += reward.get('freeXP', 0)
            bpPoints += sum((points for points in reward.get('battlePassPoints', {}).get('vehicles', {}).itervalues()))
            crystal += reward.get('crystal', 0)
            customizations += reward.get('customizations', [])

        if freeXP:
            ctx['xpStr'] = g_settings.htmlTemplates.format('xpEarned', {'freeXP': freeXP})
        if bpPoints:
            ctx['bpPointsStr'] = g_settings.htmlTemplates.format('bpPointsEarned', {'bpPoints': bpPoints})
        if crystal:
            ctx['crystalStr'] = g_settings.htmlTemplates.format('crystalEarned', {'crystal': crystal})
        if credits:
            ctx['creditsStr'] = g_settings.htmlTemplates.format('creditEarned', {'credits': credits})
        if customizations:
            customizationsList = []
            for customization in customizations:
                itemTypeID = getItemTypeID(customization['custType'])
                if itemTypeID:
                    style = self._customizationService.getItemByID(itemTypeID, customization['id'])
                    customizationsList.append(style.userName + ' (x' + str(customization['value']) + ')')

            ctx['rewardStr'] = g_settings.htmlTemplates.format('rewardEarned', {'reward': '<br/>'.join(customizationsList)})
        return (templateName, ctx)


class StoryModeAwardFormatter(ServiceChannelFormatter):
    __TEMPLATE = 'storyModeAwardMessage'

    def format(self, message, *args):
        medal = message.data.get('medalName')
        formatted = g_settings.msgTemplates.format(self.__TEMPLATE, {'at': TimeFormatter.getLongDatetimeFormat(time_utils.makeLocalServerTime(message.sentTime)),
         'medal_name': backport.text(R.strings.achievements.dyn(medal)())})
        return [MessageData(formatted, self._getGuiSettings(message, self.__TEMPLATE))]
