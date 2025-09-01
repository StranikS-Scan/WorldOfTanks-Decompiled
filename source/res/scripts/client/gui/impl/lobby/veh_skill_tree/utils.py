# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/veh_skill_tree/utils.py
from collections import namedtuple
from typing import Dict, Optional
from helpers import dependency
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.veh_skill_tree.node_model import Type, Status, NodeModel
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.veh_skill_tree.rewards_slot_model import RewardsSlotModel
from frameworks.wulf.view.array import fillStringsArray
from gui.server_events.bonuses import getNonQuestBonuses, CustomizationsBonus
from gui.shared.gui_items import Vehicle
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
        c11nItem = bonus.getC11nItem(customizations[0])
        vehicle = cls.__itemsCache.items.getItemByCD(ctx.vehCD)
        bonusInfo = bonus.getList()[0]
        wrappedInfo = bonus.getWrappedBonus()[0]
        model.setTitle(bonusInfo['description'])
        model.setSubtitle(wrappedInfo['type'])
        model.setLevel(ctx.level)
        model.setState(ctx.state)
        model.setHasPreview(c11nItem.mayInstall(vehicle))
        return model


def getVehSkillTreeBonusPackersMap():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'customizations': PrestigeCustomizationBonusUIPacker()})
    return mapping


def getVehSkillTreeRewardViewBonusPacker():
    return BonusUIPacker(getVehSkillTreeBonusPackersMap())


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


def fillNodeModel(nodeVM, step, nodeStatus):
    x, y = step.getPosition()
    nodeVM.setId(step.stepID)
    nodeVM.setX(x)
    nodeVM.setY(y)
    nodeVM.setType(Type(step.getType()))
    nodeVM.setIconName(step.action.getImageName())
    nodeVM.setLocalizationName(step.action.getLocName())
    nodeVM.setPrice(step.getPrice().xp)
    nodeVM.setStatus(nodeStatus)
    fillStringsArray(step.action.getCategories(), nodeVM.getCategories())


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


def getFullProgressionState(vehicle):
    progression = vehicle.postProgression
    state = VehicleState()
    for step in progression.iterOrderedSteps():
        state.addUnlock(step.stepID)

    return state
