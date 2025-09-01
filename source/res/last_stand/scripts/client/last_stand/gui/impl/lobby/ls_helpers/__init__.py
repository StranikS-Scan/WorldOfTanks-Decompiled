# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/ls_helpers/__init__.py
import typing
from functools import wraps
from BWUtil import AsyncReturn
from wg_async import wg_await, wg_async, forwardAsFuture
from gui.server_events.awards_formatters import AWARDS_SIZES
from gui.server_events.events_helpers import EventInfoModel
from last_stand.gui.game_control.ls_artefacts_controller import compareBonusesByPriority
from last_stand.gui.impl.gen.view_models.views.common.bonus_item_view_model import BonusItemViewModel
from last_stand.gui.impl.gen.view_models.views.lobby.widgets.meta_view_model import ArtefactStates
from last_stand.gui.impl.lobby.ls_helpers.bonuses_formatters import getLSMetaAwardFormatter, getImgName, LSBonusesAwardsComposer
from last_stand.gui.impl.gen.view_models.views.lobby.widgets.hangar_carousel_view_model import VehicleStates
from last_stand.skeletons.ls_artefacts_controller import ILSArtefactsController
from last_stand.skeletons.ls_controller import ILSController
from helpers import dependency
from items.tankmen import MAX_SKILLS_EFFICIENCY
from skeletons.gui.server_events import IEventsCache
if typing.TYPE_CHECKING:
    from ids_generators import SequenceIDGenerator as IDGenerator
    from gui.shared.gui_items.Vehicle import Vehicle
    from gui.server_events.awards_formatters import PreformattedBonus
    from gui.server_events.bonuses import SimpleBonus
    from gui.server_events.event_items import Quest
PROMINENT_REWARD_TOOLTIP_ID = 'prominent_reward_tooltip'
INF_DISPLAY_BONUSES = 999

@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def isQuestCompleted(questID, eventsCache=None):
    quest = eventsCache.getAllQuests().get(questID)
    return quest.isCompleted() if quest else False


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def getQuestDescription(questID, eventsCache=None):
    quest = eventsCache.getAllQuests().get(questID)
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


def getVehicleState(vehicle):
    state = VehicleStates.DEFAULT.value
    if vehicle.isInBattle:
        return VehicleStates.INBATTLE.value
    elif vehicle.isInUnit:
        return VehicleStates.INPLATOON.value
    elif vehicle.rentalIsOver:
        if vehicle.isWotPlus:
            return VehicleStates.SUSPENDED.value
        return VehicleStates.RENTED.value
    elif vehicle.isBroken:
        return VehicleStates.REPAIR.value
    elif not vehicle.isCrewFull:
        return VehicleStates.CREWINCOMPLETE.value
    else:
        for _, tankman in vehicle.crew:
            if tankman is not None:
                if not tankman.canUseSkillsInCurrentVehicle or not tankman.isMaxRoleLevel:
                    state = VehicleStates.UNTRAINEDCREW.value
                    break
                if tankman.currentVehicleSkillsEfficiency < MAX_SKILLS_EFFICIENCY:
                    state = VehicleStates.LOWEFFICIENCY.value

        return state


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
    sortedBonuses = sorted(bonusRewards, cmp=compareBonusesByPriority)
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
    sortedBonuses = sorted(bonusRewards, cmp=compareBonusesByPriority)
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
    sortedBonuses = sorted(bonusRewards, cmp=compareBonusesByPriority)
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
