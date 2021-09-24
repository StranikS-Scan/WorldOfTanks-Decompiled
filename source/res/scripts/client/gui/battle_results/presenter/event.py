# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenter/event.py
import typing
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.postbattle.events.wt_event_quest_model import WtEventQuestModel
from gui.impl.gen.view_models.views.lobby.postbattle.widget_model import WidgetModel
from gui.shared.gui_items.loot_box import EventLootBoxes
from gui.shared.missions.packers.bonus import packBonusModelAndTooltipData, getDefaultBonusPackersMap, BonusUIPacker
from gui.wt_event.wt_event_bonuses_packers import WtLootboxTokenBonusPacker, WTEventGroupsBonusUIPacker, WtTicketTokenBonusPacker
from helpers import dependency
from gui.server_events.bonuses import mergeBonuses
from skeletons.gui.game_control import IGameEventController, ILootBoxesController
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import TokensBonus
    from gui.impl.lobby.wt_event.wt_event_constants import EventCollections
    from gui.server_events.bonuses import SimpleBonus
    from gui.battle_results.reusable import ReusableInfo
    from gui.impl.gen.view_models.views.lobby.postbattle.widgets_model import WidgetsModel

def _getWtEventBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'battleToken': _WtWidgetTokenBonusPacker(),
     'ticket': _WtWidgetTicketTokenBonusPacker(),
     'groups': _WTEventWidgetGroupsBonusUIPacker()})
    return BonusUIPacker(mapping)


class _WtWidgetTokenBonusPacker(WtLootboxTokenBonusPacker):
    __boxesCtrl = dependency.descriptor(ILootBoxesController)
    __gameEventCtrl = dependency.descriptor(IGameEventController)

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
    __gameEventCtrl = dependency.descriptor(IGameEventController)

    @classmethod
    def _getBonusModel(cls):
        return WidgetModel()

    @classmethod
    def _packToken(cls, token, model):
        super(_WtWidgetTicketTokenBonusPacker, cls)._packToken(token, model)
        model = typing.cast(WidgetModel, model)
        model.setIsActionDisabled(not (cls.__gameEventCtrl.isModeActive() and cls.__gameEventCtrl.hasEnoughTickets()))


class _WTEventWidgetGroupsBonusUIPacker(WTEventGroupsBonusUIPacker):
    __gameEventCtrl = dependency.descriptor(IGameEventController)

    @classmethod
    def _getBonusModel(cls):
        return WidgetModel()

    @classmethod
    def _packModel(cls, model, bonus, collectionType):
        super(_WTEventWidgetGroupsBonusUIPacker, cls)._packModel(model, bonus, collectionType)
        model.setIsActionDisabled(not cls.__gameEventCtrl.isModeActive())


@dependency.replace_none_kwargs(gameEventCtrl=IGameEventController)
def _sortMap(gameEventCtrl=None):
    return {WtEventQuestModel.HUNTER_COLLECTION_ITEM: 0,
     WtEventQuestModel.BOSS_COLLECTION_ITEM: 0,
     gameEventCtrl.getConfig().ticketToken: 1,
     EventLootBoxes.WT_HUNTER: 2,
     EventLootBoxes.WT_BOSS: 2}


def setWidgets(model, reusable, _):
    questsProgress = reusable.progress.getPlayerQuestProgress()
    packer = _getWtEventBonusPacker()
    bonuses = []
    for e, _, _, _, isCompleted in questsProgress:
        if isCompleted:
            bonuses.extend(e.getBonuses())

    bonuses = mergeBonuses(bonuses)
    modelsArr = Array[WidgetModel]()
    packBonusModelAndTooltipData(bonuses, packer, modelsArr)
    sortMap = _sortMap()
    widgetsArr = model.getWidgets()
    for bonusModel in sorted(modelsArr, key=lambda b: sortMap.get(b.getName(), len(sortMap))):
        widgetsArr.addViewModel(bonusModel)

    modelsArr.clear()
