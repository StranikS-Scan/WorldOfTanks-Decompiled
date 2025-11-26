# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/views/presenters/battle_type_selector_presenter.py
from battle_royale.gui.constants import BattleRoyaleSubMode
from battle_royale.gui.impl.gen.view_models.views.lobby.views.battle_type_selector_view_model import BattleTypeSelectorViewModel, BattleType
from gui.impl.pub.view_component import ViewComponent
from gui.impl.gui_decorators import args2params
from gui.prb_control.entities.listener import IGlobalListener
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController
SubModeIdToBattleType = {BattleRoyaleSubMode.SOLO_MODE_ID: BattleType.SOLO,
 BattleRoyaleSubMode.SOLO_DYNAMIC_MODE_ID: BattleType.PLATOON,
 BattleRoyaleSubMode.SQUAD_MODE_ID: BattleType.TEAM}
BattleTypeToSubMode = {v:k for k, v in SubModeIdToBattleType.items()}

class BattleTypeSelectorPresenter(ViewComponent[BattleTypeSelectorViewModel], IGlobalListener):
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)

    def __init__(self):
        super(BattleTypeSelectorPresenter, self).__init__(model=BattleTypeSelectorViewModel)

    @property
    def viewModel(self):
        return super(BattleTypeSelectorPresenter, self).getViewModel()

    def onPrbEntitySwitched(self):
        self.__update()

    def _onLoading(self, *args, **kwargs):
        super(BattleTypeSelectorPresenter, self)._onLoading(args, kwargs)
        self.__onSubModeUpdated()
        self.__addListeners()

    def _finalize(self):
        self.__removeListeners()
        super(BattleTypeSelectorPresenter, self)._finalize()

    def __addListeners(self):
        self.viewModel.onSelectTab += self.__onSelectTab
        self.__battleRoyaleController.onSubModeUpdated += self.__onSubModeUpdated
        self.__battleRoyaleController.onPrimeTimeStatusUpdated += self.__update
        self.startGlobalListening()

    def __removeListeners(self):
        self.viewModel.onSelectTab -= self.__onSelectTab
        self.__battleRoyaleController.onSubModeUpdated -= self.__onSubModeUpdated
        self.__battleRoyaleController.onPrimeTimeStatusUpdated -= self.__update
        self.stopGlobalListening()

    @args2params(str)
    def __onSelectTab(self, tabId):
        subModeID = BattleTypeToSubMode.get(BattleType(tabId), BattleRoyaleSubMode.SOLO_MODE_ID)
        self.__battleRoyaleController.selectSubModeBattle(subModeID)

    def __update(self, *_):
        with self.viewModel.transaction() as model:
            subModeId = self.__battleRoyaleController.getCurrentSubModeID()
            model.setSelectedTab(SubModeIdToBattleType.get(subModeId, BattleType.SOLO))

    def __onSubModeUpdated(self, *args):
        self.__update()
