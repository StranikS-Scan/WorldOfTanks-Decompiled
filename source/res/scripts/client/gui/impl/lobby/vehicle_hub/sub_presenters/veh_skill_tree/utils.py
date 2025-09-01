# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/vehicle_hub/sub_presenters/veh_skill_tree/utils.py
from __future__ import absolute_import
from collections import namedtuple
from typing import Dict, Optional, Tuple
from helpers import dependency
from items import vehicles
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.veh_skill_tree.node_model import Type, Status, NodeModel
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.veh_skill_tree.rewards_slot_model import RewardsSlotModel
from gui.impl.gen.view_models.views.lobby.veh_skill_tree.tooltips.prestige_reward_tooltip_model import RewardsSlotTooltipModel
from frameworks.wulf.view.array import fillStringsArray
from gui.shared.gui_items import GUI_ITEM_TYPE, getItemTypeID
from gui.server_events.bonuses import getNonQuestBonuses, CustomizationsBonus
from gui.shared.gui_items import Vehicle
from gui.shared.gui_items.Vehicle import getNationLessName
from gui.shared.missions.packers.bonus import CustomizationBonusUIPacker, BonusUIPacker
from gui.shared.missions.packers.bonus import getDefaultBonusPackersMap
from gui.veh_post_progression.models.progression_step import PostProgressionStepItem
from post_progression_common import VehicleState
from prestige_system.prestige_milestones_common import PrestigeLevelType, MilestonesType
from skeletons.gui.shared import IItemsCache
PrestigeBonusContext = namedtuple('PrestigeBonusContext', ['vehCD', 'level', 'state'])

class PrestigeCustomizationBonusUIPacker(CustomizationBonusUIPacker):
    __itemsCache = dependency.descriptor(IItemsCache)

    @classmethod
    def _getBonusModel(cls):
        return RewardsSlotModel()

    @classmethod
    def _packSingleBonus(cls, bonus, item, label):
        model = super(PrestigeCustomizationBonusUIPacker, cls)._packSingleBonus(bonus, item, label)
        ctx = bonus.getContext()
        customizations = bonus.getCustomizations()
        if not customizations:
            return model
        else:
            c11nItem = bonus.getC11nItem(customizations[0])
            itemTypeID = getItemTypeID(item.get('custType'))
            title, _ = cls.getTextInfoByItemTypeID(itemTypeID)
            if title is None:
                return model
            model.setTitle(c11nItem.userName)
            model.setSubtitle(title)
            model.setLevel(ctx.level)
            model.setState(ctx.state)
            model.setHasPreview(itemTypeID == GUI_ITEM_TYPE.STYLE)
            if c11nItem:
                if itemTypeID in (GUI_ITEM_TYPE.ATTACHMENT, GUI_ITEM_TYPE.STAT_TRACKER):
                    model.setRarity(c11nItem.rarity)
                    model.setName(str(bonus.getC11nItem(item).itemTypeName))
                    model.setIcon(str(bonus.getC11nItem(item).name))
                elif itemTypeID == GUI_ITEM_TYPE.STYLE:
                    model.setIcon('style_{}'.format(bonus.getC11nItem(item).id))
            return model

    @staticmethod
    def getTextInfoByItemTypeID(itemTypeID):
        rewardTypeTitle = R.strings.veh_skill_tree.vanity.rewardType.title
        rewardTypeDescription = R.strings.veh_skill_tree.vanity.rewardType.description
        if itemTypeID == GUI_ITEM_TYPE.STYLE:
            return (backport.text(rewardTypeTitle.style()), backport.text(rewardTypeDescription.style()))
        elif itemTypeID == GUI_ITEM_TYPE.STAT_TRACKER:
            return (backport.text(rewardTypeTitle.stattracker()), backport.text(rewardTypeDescription.stattracker()))
        else:
            return (backport.text(rewardTypeTitle.attachment()), backport.text(rewardTypeDescription.attachment())) if itemTypeID == GUI_ITEM_TYPE.ATTACHMENT else (None, None)


def getVehSkillTreeRewardViewBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'customizations': PrestigeCustomizationBonusUIPacker()})
    return BonusUIPacker(mapping)


class PrestigeCustomizationTooltipBonusUIPacker(CustomizationBonusUIPacker):

    @classmethod
    def _getBonusModel(cls):
        return RewardsSlotTooltipModel()

    @classmethod
    def _packSingleBonus(cls, bonus, item, label):
        model = super(PrestigeCustomizationTooltipBonusUIPacker, cls)._packSingleBonus(bonus, item, label)
        customizations = bonus.getCustomizations()
        if not customizations:
            return model
        else:
            c11nItem = bonus.getC11nItem(customizations[0])
            itemTypeID = getItemTypeID(item.get('custType'))
            title, description = PrestigeCustomizationBonusUIPacker.getTextInfoByItemTypeID(itemTypeID)
            if title is None or description is None:
                return model
            model.setTitle(c11nItem.userName)
            model.setSubtitle(title)
            model.setDescription(description)
            if c11nItem and itemTypeID == GUI_ITEM_TYPE.ATTACHMENT:
                model.setRarity(c11nItem.rarity)
            return model


def getVehSkillTreeRewardTooltipViewBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'customizations': PrestigeCustomizationTooltipBonusUIPacker()})
    return BonusUIPacker(mapping)


def getPrestigeBonus(milestones, ctx):
    reward = milestones.get(ctx.level)
    if not reward:
        return None
    else:
        bonusesConfig = reward.get('bonus', {})
        bonusesPrestige = []
        for bonusName, bonusValue in bonusesConfig.items():
            bonuses = getNonQuestBonuses(bonusName, bonusValue, ctx=ctx)
            if bonuses:
                bonusesPrestige.extend(bonuses)

        return bonusesPrestige[0] if bonusesPrestige else None


def fillNodeModel(nodeVM, step, nodeStatus, vehicle):
    x, y = step.getPosition()
    nodeVM.setId(constructNodeUiId(vehicle.intCD, step.stepID))
    nodeVM.setX(x)
    nodeVM.setY(y)
    nodeVM.setType(Type(step.getType()))
    nodeVM.setIconName(step.action.getImageName())
    nodeVM.setLocalizationName(step.action.getLocName())
    nodeVM.setPrice(step.getPrice().xp)
    nodeVM.setStatus(nodeStatus)
    nodeVM.setVehicleName(getNationLessName(vehicle.name))
    fillStringsArray(step.action.getCategories(), nodeVM.getCategories())


def getFullProgressionState(vehicle):
    progression = vehicle.postProgression
    state = VehicleState()
    for step in progression.iterOrderedSteps():
        state.addUnlock(step.stepID)

    return state


def getCheapestAvailablePerk(vehicle):
    cheapestPerk = None
    postProgression = vehicle.postProgression
    rootStepID = postProgression.getRawTree().rootStep
    visitedSteps = set()
    availableSteps = set()
    candidateSteps = [rootStepID]
    while candidateSteps:
        nextCandidateSteps = []
        for stepID in candidateSteps:
            step = postProgression.getStep(stepID)
            if step in visitedSteps:
                continue
            if not step.isReceived():
                availableSteps.add(step)
            else:
                nextCandidateSteps.extend(step.getNextStepIDs())
            visitedSteps.add(step)

        candidateSteps = nextCandidateSteps

    if availableSteps:
        cheapestPerk = min(availableSteps, key=lambda step: step.getPrice())
    return cheapestPerk


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getEliteExpirience(exclude=(), itemsCache=None):
    eliteVcls = itemsCache.items.stats.eliteVehicles
    vXPs = itemsCache.items.stats.vehiclesXPs
    return sum([ vXPs.get(eliteVCD, 0) for eliteVCD in eliteVcls if eliteVCD not in exclude and vehicles.g_list.isVehicleExistingByCD(eliteVCD) ])


def constructNodeUiId(uniqueId, nodeId):
    return int(str(uniqueId) + str(nodeId))


def deconstructNodeUiId(uniqueId, nodeUiId):
    return int(str(nodeUiId)[len(str(uniqueId)):])
