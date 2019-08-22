# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/battle_royale/battle_royale_event_info.py
from frameworks.wulf import ViewFlags
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.impl.gen.view_models.views.battle_royale.event_info_view_model import EventInfoViewModel
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.Scaleform.genConsts.BATTLEROYALE_CONSTS import BATTLEROYALE_CONSTS
from gui.Scaleform.genConsts.BATTLEROYALE_ALIASES import BATTLEROYALE_ALIASES
from gui.shared import event_dispatcher

class EventInfoComponent(InjectComponentAdaptor):

    def _makeInjectView(self):
        return EventInfoView()


class EventInfoView(ViewImpl):

    def __init__(self, *args, **kwargs):
        super(EventInfoView, self).__init__(R.views.lobby.battleRoyale.event_info.EventInfo(), ViewFlags.COMPONENT, EventInfoViewModel, *args, **kwargs)

    @property
    def viewModel(self):
        return super(EventInfoView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(EventInfoView, self)._initialize()
        self.viewModel.onInfoVideoClicked += self.__onInfoVideoClicked

    def _finalize(self):
        self.viewModel.onInfoVideoClicked -= self.__onInfoVideoClicked
        super(EventInfoView, self)._finalize()

    def __onInfoVideoClicked(self):
        event_dispatcher.showBattleRoyaleIntroVideo(returnAlias=BATTLEROYALE_ALIASES.BATTLE_ROYALE_MAIN_PAGE_ALIAS, selectedItemID=BATTLEROYALE_CONSTS.BATTLE_ROYALE_INFO_ID)
