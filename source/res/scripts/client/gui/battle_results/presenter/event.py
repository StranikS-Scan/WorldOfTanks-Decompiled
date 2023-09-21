# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenter/event.py
import typing
from constants import WT_TEAMS
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.postbattle.widget_model import WidgetModel
from gui.impl.lobby.wt_event.wt_quests_view import HUNTER_QUEST_CHAINS
from gui.server_events.event_items import WtQuest
from gui.server_events.events_constants import WT_BOSS_GROUP_ID
from gui.shared.gui_items.loot_box import EventLootBoxes
from gui.shared.missions.packers.bonus import packMissionsBonusModelAndTooltipData, BonusUIPacker
from gui.wt_event.wt_event_bonuses_packers import WtLootboxTokenBonusPacker, WtTicketTokenBonusPacker
from helpers import dependency
from gui.server_events.bonuses import mergeBonuses
from skeletons.gui.game_control import IEventBattlesController, ILootBoxesController, IQuestsController
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import TokensBonus
    from gui.battle_results.reusable import ReusableInfo
    from gui.impl.gen.view_models.views.lobby.postbattle.widgets_model import WidgetsModel

def _getEventBonusWidgetsMap():
    return {'battleToken': _WtWidgetTokenBonusPacker(),
     'ticket': _WtWidgetTicketTokenBonusPacker()}


def _getWtEventBonusPacker():
    mapping = _getEventBonusWidgetsMap()
    return BonusUIPacker(mapping)


class _WtWidgetTokenBonusPacker(WtLootboxTokenBonusPacker):
    __boxesCtrl = dependency.descriptor(ILootBoxesController)
    __gameEventCtrl = dependency.descriptor(IEventBattlesController)

    @classmethod
    def _getBonusModel(cls):
        return WidgetModel()

    @classmethod
    def _packToken(cls, token, model):
        super(_WtWidgetTokenBonusPacker, cls)._packToken(token, model)
        disabled = True
        if cls.__gameEventCtrl.isModeActive():
            lootBox = cls._itemsCache.items.tokens.getLootBoxByTokenID(token.id)
            if lootBox is not None:
                lootBoxesCount = cls.__boxesCtrl.getLootBoxesCountByType(lootBox.getType())
                disabled = lootBoxesCount == 0
        model = typing.cast(WidgetModel, model)
        model.setIsActionDisabled(disabled)
        return


class _WtWidgetTicketTokenBonusPacker(WtTicketTokenBonusPacker):
    __gameEventCtrl = dependency.descriptor(IEventBattlesController)

    @classmethod
    def _getBonusModel(cls):
        return WidgetModel()

    @classmethod
    def _packToken(cls, token, model):
        super(_WtWidgetTicketTokenBonusPacker, cls)._packToken(token, model)
        model = typing.cast(WidgetModel, model)
        model.setIsActionDisabled(not (cls.__gameEventCtrl.isModeActive() and cls.__gameEventCtrl.hasEnoughTickets()))


@dependency.replace_none_kwargs(gameEventCtrl=IEventBattlesController)
def _sortMap(gameEventCtrl=None):
    return {gameEventCtrl.getConfig().ticketToken: 1,
     EventLootBoxes.WT_HUNTER: 2,
     EventLootBoxes.WT_BOSS: 2}


def setWidgets(model, reusable, _):
    isBoss = reusable.getPersonalTeam() == WT_TEAMS.BOSS_TEAM
    if isBoss:
        quests = _getQuests([WT_BOSS_GROUP_ID])
    else:
        quests = _getQuests(HUNTER_QUEST_CHAINS)
    progressData = reusable.progress.getQuestsProgress()
    completedQuests = []
    for qID, quest in quests:
        if qID not in progressData:
            continue
        _, pPrev, pCur = progressData[qID]
        isCompleted = pCur.get('bonusCount', 0) - pPrev.get('bonusCount', 0) > 0
        if isCompleted:
            completedQuests.append(quest)

    packer = _getWtEventBonusPacker()
    bonuses = []
    for quest in completedQuests:
        if isinstance(quest, WtQuest):
            bonuses.extend([ bonus for bonus in quest.getBonuses() if bonus.getName() in packer.getPackers() ])

    bonuses = mergeBonuses(bonuses)
    modelsArr = Array[WidgetModel]()
    packMissionsBonusModelAndTooltipData(bonuses, packer, modelsArr)
    sortMap = _sortMap()
    widgetsArr = model.getWidgets()
    for bonusModel in sorted(modelsArr, key=lambda b: sortMap.get(b.getName(), len(sortMap))):
        widgetsArr.addViewModel(bonusModel)

    modelsArr.clear()


def _getQuests(groupIDs):
    questController = dependency.instance(IQuestsController)

    def filterFunc(quest):
        return quest.isEventBattlesQuest() and quest.getGroupID() in groupIDs

    quests = questController.eventsCache.getAllQuests(filterFunc).items()
    return quests
