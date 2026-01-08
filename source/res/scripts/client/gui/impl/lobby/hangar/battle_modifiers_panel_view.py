# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/battle_modifiers_panel_view.py
from constants import QUEUE_TYPE, ARENA_BONUS_TYPE
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl import backport
from gui.impl.auxiliary.tooltips.simple_tooltip import createSimpleTooltip
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.hangar.battle_modifiers_panel_view_model import BattleModifiersPanelViewModel, Queue
from gui.impl.lobby.stronghold.stronghold_helpers import BATTLE_MODIFIERS_DOMAIN, getBattleModifiersByPrbEntity, getBattleModifiersQueues, BATTLE_MODIFIERS_DOMAIN_GM
from gui.impl.lobby.tooltips.battle_modifiers_domain_tooltip_view import BattleModifiersDomainTooltipView
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.prb_control.entities.listener import IGlobalListener
_TEXTS = R.strings.fortifications.battleModifiers

class BattleModifiersPanelView(ViewImpl, IGlobalListener):

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.lobby.hangar.BattleModifiersPanelView())
        settings.flags = flags
        settings.model = BattleModifiersPanelViewModel()
        super(BattleModifiersPanelView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BattleModifiersPanelView, self).getViewModel()

    def createToolTip(self, event):
        modifiers = getBattleModifiersByPrbEntity(self.prbEntity)
        return super(BattleModifiersPanelView, self).createToolTip(event) if modifiers else createSimpleTooltip(self.getParentWindow(), event, header=backport.text(_TEXTS.title()), body=backport.text(_TEXTS.body(), battleModifiersQueue=getBattleModifiersQueues()))

    def createToolTipContent(self, event, contentID):
        return BattleModifiersDomainTooltipView(BATTLE_MODIFIERS_DOMAIN_GM) if self.prbEntity.getQueueType() == QUEUE_TYPE.SPEC_BATTLE and self.prbEntity.getBonusType() == ARENA_BONUS_TYPE.GLOBAL_MAP else BattleModifiersDomainTooltipView(BATTLE_MODIFIERS_DOMAIN)

    def onPrbEntitySwitched(self):
        self.__fillModel()

    def onStrongholdDataChanged(self, header, isFirstBattle, reserve, reserveOrder):
        self.__fillModel()

    def _onLoading(self, *args, **kwargs):
        super(BattleModifiersPanelView, self)._onLoading(*args, **kwargs)
        self.startGlobalListening()
        self.__fillModel()

    def _finalize(self):
        self.stopGlobalListening()
        super(BattleModifiersPanelView, self)._finalize()

    @replaceNoneKwargsModel
    def __fillModel(self, model=None):
        queue = Queue.STRONGHOLD
        if self.prbEntity.getQueueType() == QUEUE_TYPE.SPEC_BATTLE and self.prbEntity.getBonusType() == ARENA_BONUS_TYPE.GLOBAL_MAP:
            queue = Queue.GLOBALMAP
        model.setQueue(queue)
