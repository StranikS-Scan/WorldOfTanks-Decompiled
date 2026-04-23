# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/ls_helpers/__init__.py
from __future__ import absolute_import
import typing
from functools import wraps
from BWUtil import AsyncReturn
from last_stand_common.last_stand_constants import BOOSTER_FACTOR_NAMES, BOOSTER_FACTOR_OPERATIONS
from wg_async import wg_await, wg_async, forwardAsFuture
from gui.impl.backport import getNiceNumberFormat
from gui.server_events.awards_formatters import AWARDS_SIZES
from gui.server_events.events_helpers import EventInfoModel
from last_stand.gui.game_control.ls_artefacts_controller import getBonusPriority
from last_stand.gui.impl.gen.view_models.views.common.bonus_item_view_model import BonusItemViewModel
from last_stand.gui.impl.gen.view_models.views.lobby.widgets.meta_view_model import ArtefactStates
from last_stand.gui.impl.gen.view_models.views.lobby.widgets.reward_path_view_model import RewardPathViewModel
from last_stand.gui.impl.lobby.ls_helpers.bonuses_formatters import getLSMetaAwardFormatter, getImgName, LSBonusesAwardsComposer
from last_stand.skeletons.ls_artefacts_controller import ILSArtefactsController
from last_stand.skeletons.ls_controller import ILSController
from last_stand.skeletons.ls_quests_ui_cache import ILSQuestsUICache
from helpers import dependency, time_utils
from items.tankmen import MAX_SKILLS_EFFICIENCY
from gui.shared.gui_items.Vehicle import Vehicle
if typing.TYPE_CHECKING:
    from ids_generators import SequenceIDGenerator as IDGenerator
    from gui.server_events.awards_formatters import PreformattedBonus
    from gui.server_events.bonuses import SimpleBonus
    from gui.server_events.event_items import Quest
PROMINENT_REWARD_TOOLTIP_ID = 'prominent_reward_tooltip'
INF_DISPLAY_BONUSES = 999

@dependency.replace_none_kwargs(questsCache=ILSQuestsUICache)
def isQuestCompleted(questID, questsCache=None):
    quest = questsCache.getQuests().get(questID)
    return quest.isCompleted() if quest else False


@dependency.replace_none_kwargs(questsCache=ILSQuestsUICache)
def getQuestDescription(questID, questsCache=None):
    quest = questsCache.getQuests().get(questID)
    return quest.getDescription() if quest else ''


@dependency.replace_none_kwargs(lsCtrl=ILSController)
def isCustomizationHangarDisabled(lsCtrl=None):
    return lsCtrl.isEventPrb()


class UseHeaderNavigationImpossible(object):
    __slots__ = ('_hide', '_show', '_confirmationHelper')

    def __init__(self, confirmationHelper, show=True, hide=True):
        super(UseHeaderNavigationImpossible, self).__init__()
        self._hide = hide
        self._show = show
        self._confirmationHelper = confirmationHelper

    def __call__(self, func):

        @wraps(func)
        @wg_async
        def wrapper(*args, **kwargs):

            @wg_async
            def confirmation():
                raise AsyncReturn(False)

            if self._show:
                self._confirmationHelper.start(confirmation)
            yield wg_await(forwardAsFuture(func(*args, **kwargs)))
            if self._hide:
                self._confirmationHelper.stop()

        return wrapper


@dependency.replace_none_kwargs(ctrl=ILSArtefactsController)
def getArtefactState(artefactID, ctrl=None):
    state = ArtefactStates.INPROGRESS
    if ctrl.isArtefactReceived(artefactID):
        state = ArtefactStates.RECEIVE
    elif ctrl.isArtefactOpened(artefactID):
        state = ArtefactStates.OPEN
    return state


def fillRewards(bonusRewards, bonusModels, maxBonuseInView, idGen, skipBonuses=None):
    bonusCache = {}
    formatter = LSBonusesAwardsComposer(maxBonuseInView, getLSMetaAwardFormatter())
    sortedBonuses = sorted(bonusRewards, key=getBonusPriority)
    bonusRewards = formatter.getFormattedBonuses(sortedBonuses, AWARDS_SIZES.BIG)
    for bonus in bonusRewards:
        tooltipId = '{}'.format(idGen.next())
        bonusCache[tooltipId] = bonus
        if skipBonuses is not None and bonus.bonusName in skipBonuses:
            continue
        reward = BonusItemViewModel()
        fillBaseBonusProperties(bonus, reward)
        reward.setTooltipId(tooltipId)
        bonusModels.addViewModel(reward)

    return bonusCache


def fillRewardsForTooltips(bonusRewards, bonusModels, maxBonuseInView, skipBonuses=None):
    formatter = LSBonusesAwardsComposer(maxBonuseInView, getLSMetaAwardFormatter())
    sortedBonuses = sorted(bonusRewards, key=getBonusPriority)
    bonusRewards = formatter.getFormattedBonuses(sortedBonuses, AWARDS_SIZES.BIG)
    for bonus in bonusRewards:
        if skipBonuses is not None and bonus.bonusName in skipBonuses:
            continue
        reward = BonusItemViewModel()
        fillBaseBonusProperties(bonus, reward)
        bonusModels.addViewModel(reward)

    return


@dependency.replace_none_kwargs(ctrl=ILSController)
def fillProminentBonus(resourceID, bonusRewards, bonusItemModel, ctrl=None):
    formatter = LSBonusesAwardsComposer(INF_DISPLAY_BONUSES, getLSMetaAwardFormatter())
    sortedBonuses = sorted(bonusRewards, key=getBonusPriority)
    bonusRewards = formatter.getFormattedBonuses(sortedBonuses, AWARDS_SIZES.BIG)
    prominentBonusType = ctrl.getModeSettings().prominentBonus.get(resourceID, '')
    if not prominentBonusType:
        return None
    else:
        for bonus in bonusRewards:
            if prominentBonusType not in (bonus.bonusName, bonus.itemTypeName):
                continue
            fillBaseBonusProperties(bonus, bonusItemModel)
            bonusItemModel.setTooltipId(PROMINENT_REWARD_TOOLTIP_ID)
            return bonus

        return None


def fillBaseBonusProperties(bonus, bonusModel):
    bonusModel.setUserName(str(bonus.userName))
    bonusModel.setName(bonus.bonusName)
    bonusModel.setValue(str(bonus.label))
    bonusModel.setLabel(str(bonus.label))
    bonusModel.setIcon(getImgName(bonus.getImage(AWARDS_SIZES.BIG)))
    bonusModel.setOverlayType(bonus.getOverlayType(AWARDS_SIZES.SMALL))


def getQuestFinishTimeLeft(quest):
    if quest is None:
        return 0
    else:
        return int(EventInfoModel.getDailyProgressResetTimeDelta()) if quest.bonusCond.isDaily() else quest.getFinishTimeLeft()


@dependency.replace_none_kwargs(ctrl=ILSController)
def getBoosterFactorsParam(boosterName, ctrl=None):
    lsBoosters = ctrl.getModeSettings().lsBoostersConfig
    boosterFactors = next((booster for booster in lsBoosters if booster.get('name') == boosterName), None)
    result = {}
    for factor in boosterFactors.get('factors', []):
        if factor['operation'] == BOOSTER_FACTOR_OPERATIONS.ADD:
            result[factor['key'] + '_' + factor['operation']] = getNiceNumberFormat(abs(factor['value']))
        if factor['operation'] == BOOSTER_FACTOR_OPERATIONS.ADD_PERCENT:
            if factor['key'] not in BOOSTER_FACTOR_NAMES.RETENTION_FACTORS:
                result[factor['key'] + '_' + factor['operation']] = getNiceNumberFormat(abs(factor['value'] * 100))
            else:
                result[factor['key'] + '_' + factor['operation']] = getNiceNumberFormat(abs(1 + factor['value']) * 100)

    return result


@dependency.replace_none_kwargs(lsCtrl=ILSController, lsArtefactCtrl=ILSArtefactsController)
def fillRewardPathWidgetViewModel(model, lastUnopenedArtefactId=None, lsCtrl=None, lsArtefactCtrl=None):
    endDate = lsCtrl.getModeSettings().endDate
    now = time_utils.getCurrentLocalServerTimestamp()
    maxProgress = lsArtefactCtrl.getMaxArtefactsProgress()
    currentProgress = lsArtefactCtrl.getCurrentArtefactProgress()
    model.setTimeLeft(endDate - now)
    model.setCurrentProgress(min(currentProgress + 1, maxProgress))
    model.setIsCompleted(currentProgress >= maxProgress)
    model.setDataCollected(lsArtefactCtrl.getProgressPointsQuantity())
    if lastUnopenedArtefactId:
        model.setDataAmount(lsArtefactCtrl.getArtefactProgressPointsCost(lastUnopenedArtefactId))


def getLSVehicleStatus(vehicle):
    vState, vStateLvl = vehicle.getState()
    if vehicle.isRotationApplied():
        if vState in (Vehicle.VEHICLE_STATE.AMMO_NOT_FULL, Vehicle.VEHICLE_STATE.LOCKED):
            vState = Vehicle.VEHICLE_STATE.ROTATION_GROUP_UNLOCKED
    if not vehicle.activeInNationGroup:
        vState = Vehicle.VEHICLE_STATE.NOT_PRESENT
    return (Vehicle.VEHICLE_STATE.UNDAMAGED, Vehicle.VEHICLE_STATE_LEVEL.INFO) if vState in (Vehicle.VEHICLE_STATE.AMMO_NOT_FULL, Vehicle.VEHICLE_STATE.AMMO_NOT_FULL_EVENTS) else (vState, vStateLvl)
