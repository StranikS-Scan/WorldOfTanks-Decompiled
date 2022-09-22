# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenter/event.py
import typing
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.postbattle.widget_model import WidgetModel
from gui.server_events.event_items import WtQuest
from gui.shared.gui_items.loot_box import EventLootBoxes
from gui.shared.missions.packers.bonus import packBonusModelAndTooltipData, getDefaultBonusPackersMap, BonusUIPacker
from gui.wt_event.wt_event_bonuses_packers import WtLootboxTokenBonusPacker, WtTicketTokenBonusPacker
from helpers import dependency
from gui.server_events.bonuses import mergeBonuses
from skeletons.gui.game_control import IEventBattlesController, ILootBoxesController
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import TokensBonus
    from gui.battle_results.reusable import ReusableInfo
    from gui.impl.gen.view_models.views.lobby.postbattle.widgets_model import WidgetsModel

def _getEventBonusWidgetsMap():
    return {'battleToken': _WtWidgetTokenBonusPacker(),
     'ticket': _WtWidgetTicketTokenBonusPacker()}


def _getWtEventBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update(_getEventBonusWidgetsMap())
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
    questsProgress = reusable.progress.getPlayerQuestProgress()
    packer = _getWtEventBonusPacker()
    bonuses = []
    for e, _, _, _, isCompleted in questsProgress:
        if isCompleted:
            if isinstance(e, WtQuest):
                bonuses.extend([ bonus for bonus in e.getBonuses() if bonus.getName() in _getEventBonusWidgetsMap().keys() ])
            else:
                bonuses.extend(e.getBonuses())

    bonuses = mergeBonuses(bonuses)
    modelsArr = Array[WidgetModel]()
    packBonusModelAndTooltipData(bonuses, packer, modelsArr)
    sortMap = _sortMap()
    widgetsArr = model.getWidgets()
    for bonusModel in sorted(modelsArr, key=lambda b: sortMap.get(b.getName(), len(sortMap))):
        widgetsArr.addViewModel(bonusModel)

    modelsArr.clear()
