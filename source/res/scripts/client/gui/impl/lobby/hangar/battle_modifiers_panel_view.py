# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/battle_modifiers_panel_view.py
from constants import QUEUE_TYPE, ARENA_BONUS_TYPE
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl import backport
from gui.impl.auxiliary.tooltips.simple_tooltip import createSimpleTooltip
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.hangar.battle_modifiers_panel_view_model import BattleModifiersPanelViewModel, Queue
from gui.impl.lobby.tooltips.battle_modifiers_domain_tooltip_view import BattleModifiersDomainTooltipView
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.prb_control.entities.listener import IGlobalListener
from helpers import dependency, int2roman
from skeletons.gui.game_control import IBattleModifiersController
from skeletons.gui.hangar import IBattleModifiersEntry
_TEXTS = R.strings.fortifications.battleModifiers

class BattleModifiersPanelView(ViewImpl, IGlobalListener, IBattleModifiersEntry):
    __battleModifiersController = dependency.descriptor(IBattleModifiersController)

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.lobby.hangar.BattleModifiersPanelView())
        settings.flags = flags
        settings.model = BattleModifiersPanelViewModel()
        super(BattleModifiersPanelView, self).__init__(settings)

    @classmethod
    def getIsActive(cls):
        modifiersDomain = cls.__battleModifiersController.getCurrentDomain()
        return modifiersDomain in IBattleModifiersController.ModifiersDomains.STRONGHOLD_DOMAINS

    @property
    def viewModel(self):
        return super(BattleModifiersPanelView, self).getViewModel()

    def createToolTip(self, event):
        if self.__battleModifiersController.battleModifiers:
            return super(BattleModifiersPanelView, self).createToolTip(event)
        bmQueues = self.__battleModifiersController.getBattleModifiersQueues()
        bmTextQueue = self.makeTextQueue(bmQueues)
        return createSimpleTooltip(self.getParentWindow(), event, header=backport.text(_TEXTS.title()), body=backport.text(_TEXTS.body(), battleModifiersQueue=bmTextQueue))

    def createToolTipContent(self, event, contentID):
        domain = self.__battleModifiersController.getCurrentDomain()
        return BattleModifiersDomainTooltipView(domain)

    def onPrbEntitySwitched(self):
        self.__fillModel()

    def onStrongholdDataChanged(self, header, isFirstBattle, reserve, reserveOrder):
        self.__fillModel()

    @staticmethod
    def makeTextQueue(bmQueues):
        textQueues = []
        for name, level in bmQueues:
            if level:
                textQueues.append(backport.text(R.strings.fortifications.battleModifiers.dyn(name)(), level=int2roman(int(level))))
            textQueues.append(backport.text(R.strings.fortifications.battleModifiers.dyn(name)()))

        return ', '.join(textQueues)

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
