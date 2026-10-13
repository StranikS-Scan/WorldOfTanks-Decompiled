# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/hw_helpers/__init__.py
from __future__ import absolute_import
import typing
from gui.server_events.events_helpers import EventInfoModel
from halloween_common.halloween_constants import KEY_DAILY_QUEST_TPL
from gui.server_events.awards_formatters import AWARDS_SIZES
from halloween.gui.game_control.halloween_artefacts_controller import getBonusPriority
from halloween.gui.impl.gen.view_models.views.common.bonus_item_view_model import BonusItemViewModel
from halloween.gui.impl.gen.view_models.views.lobby.widgets.hangar_carousel_vehicle_view_model import VehicleStates
from halloween.gui.impl.gen.view_models.views.lobby.widgets.meta_view_model import ArtefactStates
from halloween.gui.impl.gen.view_models.views.lobby.vehicle_title_view_model import VehicleTypes, VehicleTitleViewModel
from halloween.gui.impl.lobby.hw_helpers.bonuses_formatters import getHWMetaAwardFormatter, getImgName, HalloweenBonusesAwardsComposer
from halloween.skeletons.halloween_artefacts_controller import IHalloweenArtefactsController
from halloween.skeletons.halloween_bestiary_controller import IHalloweenBestiaryController
from halloween.skeletons.halloween_controller import IHalloweenController
from helpers import dependency
from halloween_common.halloween_constants import HWStoryChoiceSettings
if typing.TYPE_CHECKING:
    from typing import Optional, Tuple, List, Dict, Any
    from frameworks.wulf import Array
    from gui.server_events.awards_formatters import PreformattedBonus
    from gui.server_events.bonuses import SimpleBonus
    from gui.server_events.event_items import Quest
    from halloween_common.configs.halloween_bestiary import EnemyModel
    from ids_generators import SequenceIDGenerator
PROMINENT_REWARD_TOOLTIP_ID = 'prominent_reward_tooltip'
INF_DISPLAY_BONUSES = 999

@dependency.replace_none_kwargs(hwCtrl=IHalloweenController)
def isDailyKeyQuestCompleted(intCD, hwCtrl=None):
    quest = hwCtrl.getHWQuestsCache().get(KEY_DAILY_QUEST_TPL.format(intCD=intCD))
    return quest.isCompleted() if quest else True


@dependency.replace_none_kwargs(hwCtrl=IHalloweenController)
def getDailyKeyQuestDescription(intCD, hwCtrl=None):
    quest = hwCtrl.getHWQuestsCache().get(KEY_DAILY_QUEST_TPL.format(intCD=intCD))
    return quest.getDescription() if quest else ''


@dependency.replace_none_kwargs(hwCtrl=IHalloweenController)
def isCustomizationHangarDisabled(hwCtrl=None):
    return hwCtrl.isEventPrb()


@dependency.replace_none_kwargs(ctrl=IHalloweenController)
def getVehicleState(vehicle, ctrl=None):
    state = VehicleStates.DEFAULT
    if not ctrl.hasAccessToVehicle(vehicle.intCD):
        state = VehicleStates.LOCKED
    elif vehicle.isInBattle:
        state = VehicleStates.INBATTLE
    elif vehicle.isInUnit:
        state = VehicleStates.INPLATOON
    elif vehicle.isAwaitingBattle:
        state = VehicleStates.INQUEUE
    return state


@dependency.replace_none_kwargs(ctrl=IHalloweenArtefactsController)
def getArtefactState(artefactID, ctrl=None):
    state = ArtefactStates.INPROGRESS
    if ctrl.isArtefactReceived(artefactID):
        state = ArtefactStates.RECEIVE
    elif ctrl.isArtefactOpened(artefactID):
        state = ArtefactStates.OPEN
    return state


def fillRewardsForTooltips(bonusRewards, bonusModels, maxBonuseInView, skipBonuses=None):
    formatter = HalloweenBonusesAwardsComposer(maxBonuseInView, getHWMetaAwardFormatter())
    sortedBonuses = sorted(bonusRewards, key=getBonusPriority)
    bonusRewards = formatter.getFormattedBonuses(sortedBonuses, AWARDS_SIZES.BIG)
    for bonus in bonusRewards:
        if skipBonuses is not None and bonus.bonusName in skipBonuses:
            continue
        reward = BonusItemViewModel()
        fillBaseBonusProperties(bonus, reward)
        bonusModels.addViewModel(reward)

    return


@dependency.replace_none_kwargs(ctrl=IHalloweenController)
def fillProminentBonus(resourceID, bonusRewards, bonusItemModel, ctrl=None):
    formatter = HalloweenBonusesAwardsComposer(INF_DISPLAY_BONUSES, getHWMetaAwardFormatter())
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
    bonusModel.setTooltipContentId(str(bonus.tooltip))
    bonusModel.setOverlayType(bonus.getOverlayType(AWARDS_SIZES.SMALL))


@dependency.replace_none_kwargs(ctrl=IHalloweenArtefactsController)
def fillGiftVehicleModel(vehGiftModel, ctrl=None):
    if ctrl is None:
        return
    else:
        vehicle = ctrl.getMainGiftVehicle()
        if vehicle is None:
            return
        vehGiftModel.setId(vehicle.intCD)
        vehGiftModel.setName(vehicle.userName)
        vehGiftModel.setLevel(vehicle.level)
        vehGiftModel.setNation(vehicle.nationName)
        vehGiftModel.setIsPremium(vehicle.isPremium)
        vehGiftModel.setRole(vehicle.role)
        vehGiftModel.setVehicleType(VehicleTypes(vehicle.type) if vehicle.type != '' else VehicleTypes.NONE)
        return


def getQuestSmallestFinishTimeLeft(quests):
    if quests:
        dailyResetTimeDelta = int(EventInfoModel.getDailyProgressResetTimeDelta())
        minTime = min([ (dailyResetTimeDelta if q.bonusCond.isDaily() else q.getFinishTimeLeft()) for q in quests ])
        return max(minTime, 0)


def fillRewardsCommon(bonusRewards, bonusModels, maxBonuseInView, idGen, rewardsHighlight=None, skipBonusNames=None):
    bonusCache = {}
    rewardsHighlight = rewardsHighlight or []
    skipBonusNames = skipBonusNames or []
    formatter = HalloweenBonusesAwardsComposer(maxBonuseInView, getHWMetaAwardFormatter())
    sortedBonuses = sorted(bonusRewards, key=getBonusPriority)
    formattedBonuses = formatter.getFormattedBonuses(sortedBonuses, AWARDS_SIZES.BIG)
    for bonus in formattedBonuses:
        if bonus.bonusName not in skipBonusNames:
            tooltipId = '{}'.format(next(idGen))
            bonusCache[tooltipId] = bonus
            reward = BonusItemViewModel()
            reward.setUserName(str(bonus.userName))
            reward.setName(bonus.bonusName)
            reward.setValue(str(bonus.label))
            reward.setLabel(str(bonus.label))
            reward.setIcon(getImgName(bonus.getImage(AWARDS_SIZES.BIG)))
            reward.setOverlayType(bonus.getOverlayType(AWARDS_SIZES.SMALL))
            reward.setTooltipId(tooltipId)
            reward.setTooltipContentId(str(bonus.tooltip))
            reward.setIsRewardShined(bonus.bonusName in rewardsHighlight)
            bonusModels.addViewModel(reward)

    return bonusCache


def fillRewards(artefact, bonusModels, maxBonuseInView, idGen, rewardsHighlight=None, skipBonusNames=None):
    return fillRewardsCommon(artefact.bonusRewards, bonusModels, maxBonuseInView, idGen, rewardsHighlight, skipBonusNames)


@dependency.replace_none_kwargs(hwArtefactCtrl=IHalloweenArtefactsController, hwBestiaryCtrl=IHalloweenBestiaryController)
def getEnemyByArtefactID(artefactID, hwArtefactCtrl=None, hwBestiaryCtrl=None):
    return hwBestiaryCtrl.getEnemyByToken(hwArtefactCtrl.getOpenedArtefactToken(artefactID))


def getEndingToken(choice):
    return HWStoryChoiceSettings.OPTION_1 if choice == 'option_1' else HWStoryChoiceSettings.OPTION_2
