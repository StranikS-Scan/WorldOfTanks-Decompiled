# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/vehicle_hub/sub_presenters/veh_skill_tree_sub_presenter.py
from __future__ import absolute_import
import logging
from Event import Event
from frameworks.state_machine import StateIdsObserver
from account_helpers import AccountSettings
from account_helpers.AccountSettings import VEH_SKILL_TREE_INTRO_SHOWN
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.veh_skill_tree_model import VehSkillTreeModel
from gui.impl.lobby.vehicle_hub import VehicleHubCtx, VehSkillTreeProgressionState, VehSkillTreePrestigeState, VehSkillTreeInitialState
from gui.impl.lobby.vehicle_hub.sub_presenters.sub_presenter_base import SubPresenterBase
from gui.impl.lobby.vehicle_hub.sub_presenters.veh_skill_tree.prestige_presenter import PrestigePresenter
from gui.impl.lobby.vehicle_hub.sub_presenters.veh_skill_tree.tree_presenter import TreePresenter
_logger = logging.getLogger(__name__)

class _VehicleSkillTreeStatesObserver(StateIdsObserver):

    def __init__(self):
        super(_VehicleSkillTreeStatesObserver, self).__init__([VehSkillTreeInitialState.STATE_ID, VehSkillTreeProgressionState.STATE_ID, VehSkillTreePrestigeState.STATE_ID])
        self.onNavigationChanged = Event()

    def onEnterState(self, state, event):
        if hasattr(state, 'SUB_TAB_NAME'):
            self.onNavigationChanged(state.SUB_TAB_NAME)


class VehSkillTreeSubPresenter(SubPresenterBase):

    def __init__(self, viewModel, parentView):
        super(VehSkillTreeSubPresenter, self).__init__(viewModel, parentView)
        self.__presenters = {}
        self.__activeTab = None
        self.__lsmObserver = _VehicleSkillTreeStatesObserver()
        return

    @property
    def viewModel(self):
        return super(VehSkillTreeSubPresenter, self).getViewModel()

    @property
    def currentPresenter(self):
        return self.__presenters[self.__activeTab] if self.__activeTab else None

    def createToolTipContent(self, event, contentID):
        if self.currentPresenter is not None:
            content = self.currentPresenter.createToolTipContent(event, contentID)
            if content is not None:
                return content
        return super(VehSkillTreeSubPresenter, self).createToolTipContent(event, contentID)

    def initialize(self, vhCtx, *args, **kwargs):
        self.__presenters = {VehSkillTreeModel.TREE: TreePresenter(self.viewModel.tree, self.parentView),
         VehSkillTreeModel.PRESTIGE: PrestigePresenter(self.viewModel.prestige, self.parentView)}
        lsm = getLobbyStateMachine()
        lsm.connect(self.__lsmObserver)
        self.__markIntroShowed()
        super(VehSkillTreeSubPresenter, self).initialize(vhCtx, *args, **kwargs)

    def finalize(self):
        lsm = getLobbyStateMachine()
        lsm.disconnect(self.__lsmObserver)
        if self.currentPresenter is not None:
            self.currentPresenter.finalize()
        super(VehSkillTreeSubPresenter, self).finalize()
        return

    def clear(self):
        for presenter in self.__presenters.values():
            presenter.clear()

        self.__lsmObserver = None
        self.__presenters = None
        self.__activeTab = None
        super(VehSkillTreeSubPresenter, self).clear()
        return

    def _getEvents(self):
        return ((self.__lsmObserver.onNavigationChanged, self.__onNavigationChanged),)

    def __onNavigationChanged(self, tabName):
        if tabName in self.__presenters:
            if self.currentPresenter and self.currentPresenter.isLoaded:
                self.currentPresenter.finalize()
            self.__activeTab = tabName
            self.viewModel.setLocationId(self.__activeTab)
            self.currentPresenter.initialize(self.vehicleHubCtx)
        else:
            _logger.error('Wrong presenter id %s.', tabName)

    @staticmethod
    def __markIntroShowed():
        from gui.shared.event_dispatcher import showVehSkillTreeIntro
        if not AccountSettings.getUIFlag(VEH_SKILL_TREE_INTRO_SHOWN):
            showVehSkillTreeIntro()
            AccountSettings.setUIFlag(VEH_SKILL_TREE_INTRO_SHOWN, True)
