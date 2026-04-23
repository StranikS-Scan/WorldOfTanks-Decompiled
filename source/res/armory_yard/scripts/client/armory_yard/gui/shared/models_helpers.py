# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/shared/models_helpers.py
import typing
from itertools import chain
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_quest_model import ArmoryYardQuestModel as QuestModel
from armory_yard.gui.shared.bonus_packers import getArmoryYardBonusPacker
from frameworks.wulf.view.array import fillIntsArray
from armory_yard.gui.shared.events_packers import ArmoryYardQuestUIDataPacker
from helpers import dependency
from nations import NAMES
from skeletons.gui.shared import IItemsCache
from armory_yard.skeletons.armory_yard_reroll_controller import IArmoryYardRerollController
if typing.TYPE_CHECKING:
    from typing import Iterable, Tuple, Dict, Set
    from armory_yard.gui.shared.armory_dynamic_quest import ArmoryDynamicQuest as ADQuest
    from gui.server_events.event_items import Quest
    from frameworks.wulf import Array

def _createArmoryQuestModel(quest, tooltipData, chapterID=0, hasBattleTokens=True, hideBattleTypes=None):
    vehicleClasses, vehicleLevels, vehicleNations = getRequiredVehicleDescrForQuest(quest)
    packer = ArmoryYardQuestUIDataPacker(quest, bonusPackerGetter=lambda : getArmoryYardBonusPacker(hasBattleTokens))
    questModel = packer.pack(model=QuestModel())
    questModel.setChapterId(chapterID)
    vehicleTypes = questModel.getVehicleTypes()
    vehicleTypes.clear()
    for vehicleClass in vehicleClasses:
        vehicleTypes.addString(vehicleClass)

    vehicleTypes.invalidate()
    vehicleNationsModel = questModel.getVehicleNations()
    vehicleNationsModel.clear()
    for vehicleNationID in vehicleNations:
        vehicleNationsModel.addString(NAMES[vehicleNationID])

    vehicleNationsModel.invalidate()
    battleTypes = questModel.getBattleTypes()
    battleTypes.clear()
    battleConditions = quest.preBattleCond.getConditions().find('bonusTypes')
    for battleType in battleConditions.getValue():
        if battleType not in hideBattleTypes:
            battleTypes.addNumber(battleType)

    battleTypes.invalidate()
    fillIntsArray(vehicleLevels, questModel.getLevels())
    questModel.setShowLevelsAsRange(isShowLevelsAsRange(vehicleLevels))
    tooltipData.update(packer.getTooltipData())
    return questModel


def updateArmoryConditionQuestsModel(questsModel, quests, tooltipData, chapterID=0, hasBattleTokens=True):
    questsCompleted = False
    tokenQuestID = ''
    hideBattleTypes = getHideBattleTypes()
    for quest in sorted(quests, key=lambda q: q.getSubCondID()):
        if set(quest.preBattleCond.getConditions().find('bonusTypes').getValue()).issubset(hideBattleTypes):
            continue
        if quest.isCompleted():
            questsCompleted = True
        vehicleClasses, vehicleLevels, vehicleNations = getRequiredVehicleDescrForQuest(quest)
        packer = ArmoryYardQuestUIDataPacker(quest, bonusPackerGetter=lambda : getArmoryYardBonusPacker(hasBattleTokens))
        questModel = packer.pack(model=QuestModel())
        questModel.setChapterId(chapterID)
        vehicleTypes = questModel.getVehicleTypes()
        vehicleTypes.clear()
        for vehicleClass in vehicleClasses:
            vehicleTypes.addString(vehicleClass)

        vehicleTypes.invalidate()
        vehicleNationsModel = questModel.getVehicleNations()
        vehicleNationsModel.clear()
        for vehicleNationID in vehicleNations:
            vehicleNationsModel.addString(NAMES[vehicleNationID])

        vehicleNationsModel.invalidate()
        battleTypes = questModel.getBattleTypes()
        battleTypes.clear()
        battleConditions = quest.preBattleCond.getConditions().find('bonusTypes')
        for battleType in battleConditions.getValue():
            if battleType not in hideBattleTypes:
                battleTypes.addNumber(battleType)

        battleTypes.invalidate()
        fillIntsArray(vehicleLevels, questModel.getLevels())
        questModel.setShowLevelsAsRange(isShowLevelsAsRange(vehicleLevels))
        tooltipData.update(packer.getTooltipData())
        tokenQuestID = quest.getTokenQuestID()
        questsModel.addViewModel(questModel)

    return (questsCompleted, tokenQuestID)


def updateArmoryBattleQuestsModel(questsModel, quests, tooltipData, chapterID=0, hasBattleTokens=True):
    questsCompleted = False
    hideBattleTypes = getHideBattleTypes()
    for quest in quests:
        if set(quest.preBattleCond.getConditions().find('bonusTypes').getValue()).issubset(hideBattleTypes):
            continue
        if quest.isCompleted():
            questsCompleted = True
        questModel = _createArmoryQuestModel(quest, tooltipData, chapterID, hasBattleTokens, hideBattleTypes)
        questsModel.addViewModel(questModel)

    return questsCompleted


def isShowLevelsAsRange(levels):
    if len(levels) < 2:
        return False
    for i, level in enumerate(levels[1:]):
        if level != levels[i] + 1:
            return False

    return True


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getRequiredVehicleDescrForQuest(quest, itemsCache=None):
    conditions = quest.vehicleReqs.getConditions().find('vehicleDescr')
    if conditions:
        vehicleTypes, vehicleNations, vehicleLevels, vehicleClasses, _ = conditions.parseFilters()
        levels = set()
        if vehicleTypes:
            for vehicleTypeCD in vehicleTypes:
                currentVehicle = itemsCache.items.getItemByCD(int(vehicleTypeCD))
                levels.add(currentVehicle.level)

        vehicleLevels = vehicleLevels or levels
        return (vehicleClasses or tuple(), sorted(vehicleLevels), vehicleNations or tuple())
    return (tuple(), set(), tuple())


@dependency.replace_none_kwargs(armoryYardReroll=IArmoryYardRerollController)
def getHideBattleTypes(armoryYardReroll=None):
    return armoryYardReroll.getHideBattleTypes()


def visitQuestInModel(questModel):
    isUpdated = False
    for item in chain(questModel.bonusCondition.getItems(), questModel.postBattleCondition.getItems()):
        if item.getEarned():
            isUpdated = True
            item.setEarned(0)

    if questModel.getEarned():
        isUpdated = True
        questModel.setEarned(0)
    return isUpdated
