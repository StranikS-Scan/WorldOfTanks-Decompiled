# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/shared/utils.py
import typing
from frameworks.wulf import WindowLayer
from gui.Scaleform.framework.entities.DisposableEntity import EntityState
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.server_events.awards_formatters import AwardsPacker, AWARDS_SIZES
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from story_mode.gui.story_mode_gui_constants import VIEW_ALIAS
from story_mode.gui.shared.bonuses_formatters import StoryModeBonusesAwardsComposer, getImgPath
from story_mode.gui.shared.packers.bonus import getSMFormattersMap
from story_mode.gui.impl.gen.view_models.views.lobby.reward_model import RewardModel
from story_mode_common.configs.story_mode_missions import missionsSchema
from wg_async import wg_async, AsyncEvent, wg_await
if typing.TYPE_CHECKING:
    from gui.Scaleform.framework.application import AppEntry

@wg_async
def waitForLobby():
    appLoader = dependency.instance(IAppLoader)
    lobbyApp = appLoader.getDefLobbyApp()
    lobbyView = lobbyApp.containerManager.getContainer(WindowLayer.VIEW).getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.LOBBY})
    if lobbyView.getState() != EntityState.CREATED:
        asyncEvent = AsyncEvent()

        def onLobbyViewCreated(_):
            asyncEvent.set()

        lobbyView.onCreated += onLobbyViewCreated
        yield wg_await(asyncEvent.wait())
        lobbyView.onCreated -= onLobbyViewCreated


def getRewardList(progressInfo, isBattlePassActive, forBattleResults=False):
    missionSettings = missionsSchema.getModel()
    rewardsList = []
    if missionSettings is None:
        return rewardsList
    else:
        tasksToComplete = progressInfo.get('tasksToComplete', {})
        for missionId, tasksProgression in progressInfo.get('tasksProgression', {}).iteritems():
            mission = missionSettings.getMission(missionId)
            if mission is not None:
                rewardsList += mission.getTasksReward([ taskId for taskId in tasksProgression if tasksToComplete.get((missionId, taskId), True) ], isBattlePassActive)

        for missionId in progressInfo.get('missionsCompleted', []):
            mission = missionSettings.getMission(missionId)
            if mission is not None:
                rewardsList.append(mission.getMissionReward(forBattleResults))

        return rewardsList


def getTasksCount(progressInfo):
    tasksToComplete = progressInfo.get('tasksToComplete', {})
    tasksToCompleteCount = len(tasksToComplete)
    completedTasksCount = 0
    for missionID, tasks in progressInfo.get('tasksProgression', {}).iteritems():
        for taskID in tasks:
            if (missionID, taskID) in tasksToComplete:
                completedTasksCount += 1

    return (completedTasksCount, tasksToCompleteCount)


def formatAndFillRewards(rewards, rewardsModel, idGenerator, bonusCache, maxBonusesInView):
    rewardsModel.clear()
    formatter = StoryModeBonusesAwardsComposer(maxBonusesInView, AwardsPacker(getSMFormattersMap()))
    bonusRewards = formatter.getFormattedBonuses(rewards, AWARDS_SIZES.BIG)
    for bonus in bonusRewards:
        tooltipId = '{}'.format(idGenerator.next())
        bonusCache[tooltipId] = bonus
        rewardItem = RewardModel()
        rewardItem.setName(bonus.bonusName)
        rewardItem.setValue(str(bonus.label if bonus.label is not None else ''))
        rewardItem.setTooltipId(tooltipId)
        if isinstance(bonus.tooltip, int):
            rewardItem.setTooltipContentId(str(bonus.tooltip))
        iconModel = rewardItem.icon
        iconModel.setSmall(getImgPath(bonus.images.get('small')))
        iconModel.setBig(getImgPath(bonus.images.get('big')))
        rewardsModel.addViewModel(rewardItem)

    return
