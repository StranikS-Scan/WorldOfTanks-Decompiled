# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: versus_ai/scripts/client/VersusAIPersonality.py
from constants import PREBATTLE_TYPE, QUEUE_TYPE, ARENA_BONUS_TYPE, ARENA_GUI_TYPE, INVITATION_TYPE
from constants_utils import AbstractBattleMode
from gui.prb_control.prb_utils import initGuiTypes
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from UnitBase import UNIT_MGR_FLAGS, ROSTER_TYPE
from versus_ai.gui import versus_ai_gui_constants
from versus_ai.gui.versus_ai_gui_constants import PREBATTLE_ACTION_NAME, DEFAULT_QUEUE_TYPE_PRIORITY
from versus_ai.gui.Scaleform import registerVersusAIScaleform
from versus_ai.gui.prb_control import registerVersusAIStorage

class ClientVersusAIBattleMode(AbstractBattleMode):
    _PREBATTLE_TYPE = PREBATTLE_TYPE.VERSUS_AI
    _QUEUE_TYPE = QUEUE_TYPE.VERSUS_AI
    _ARENA_BONUS_TYPE = ARENA_BONUS_TYPE.VERSUS_AI
    _ARENA_GUI_TYPE = ARENA_GUI_TYPE.VERSUS_AI
    _UNIT_MGR_FLAGS = UNIT_MGR_FLAGS.VERSUS_AI
    _ROSTER_TYPE = ROSTER_TYPE.VERSUS_AI_ROSTER
    _INVITATION_TYPE = INVITATION_TYPE.VERSUS_AI
    _DEFAULT_QUEUE_TYPE_PRIORITY = DEFAULT_QUEUE_TYPE_PRIORITY
    _CLIENT_BATTLE_PAGE = VIEW_ALIAS.CLASSIC_BATTLE_PAGE
    _CLIENT_PRB_ACTION_NAME = PREBATTLE_ACTION_NAME.VERSUS_AI
    _CLIENT_PRB_ACTION_NAME_SQUAD = PREBATTLE_ACTION_NAME.VERSUS_AI_SQUAD

    @property
    def _ROSTER_CLASS(self):
        from unit_roster_config import VersusAIRoster
        return VersusAIRoster

    @property
    def _client_prbEntityClass(self):
        from versus_ai.gui.prb_control.entities.pre_queue.entity import VersusAIEntity
        return VersusAIEntity

    @property
    def _client_prbEntryPointClass(self):
        from versus_ai.gui.prb_control.entities.pre_queue.entity import VersusAIEntryPoint
        return VersusAIEntryPoint

    @property
    def _client_gameControllers(self):
        from versus_ai.skeletons.versus_ai_controller import IVersusAIController
        from versus_ai.gui.game_control.versus_ai_controller import VersusAIController
        return ((IVersusAIController, VersusAIController, False),)

    @property
    def _client_selectorColumn(self):
        from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_columns import ModeSelectorColumns
        return (ModeSelectorColumns.COLUMN_2, 30)

    @property
    def _client_selectorItemsCreator(self):
        from versus_ai.gui.Scaleform.daapi.view.lobby.header.battle_selector_items import addVersusAIBattleType
        return addVersusAIBattleType

    @property
    def _client_modeSelectorItemsClass(self):
        from versus_ai.gui.impl.lobby.mode_selector.versus_ai_mode_selector_item import VersusAIModeSelectorItem
        return VersusAIModeSelectorItem

    @property
    def _client_prbSquadEntityClass(self):
        from versus_ai.gui.prb_control.entities.squad.entity import VersusAISquadEntity
        return VersusAISquadEntity

    @property
    def _client_prbSquadEntryPointClass(self):
        from versus_ai.gui.prb_control.entities.squad.entity import VersusAISquadEntryPoint
        return VersusAISquadEntryPoint

    @property
    def _client_selectorSquadItemsCreator(self):
        from versus_ai.gui.Scaleform.daapi.view.lobby.header.battle_selector_items import addVersusAISquadType
        return addVersusAISquadType

    @property
    def _client_platoonViewClass(self):
        from versus_ai.gui.impl.lobby.versus_ai_platoon_members_view import VersusAIMembersView
        return VersusAIMembersView

    @property
    def _client_platoonLayouts(self):
        from gui.impl.gen import R
        from gui.impl.lobby.platoon.platoon_config import EPlatoonLayout, MembersWindow, PlatoonLayout
        return [(EPlatoonLayout.MEMBER, PlatoonLayout(R.views.lobby.platoon.MembersWindow(), MembersWindow))]

    @property
    def _client_providerBattleQueue(self):
        from versus_ai.gui.Scaleform.daapi.view.lobby.battle_queue import VersusAIQueueProvider
        return VersusAIQueueProvider

    @property
    def _client_arenaDescrClass(self):
        from versus_ai.gui.battle_control.arena_info.arena_descrs import VersusAIArenaDescription
        return VersusAIArenaDescription

    @property
    def _client_squadFinderClass(self):
        from gui.battle_control.arena_info.squad_finder import TeamScopeNumberingFinder
        return TeamScopeNumberingFinder

    @property
    def _client_tipsCriteriaClass(self):
        from versus_ai.helpers.versus_ai_tips import VersusAiTipsCriteria
        return VersusAiTipsCriteria


def preInit():
    initGuiTypes(versus_ai_gui_constants, __name__)
    battleMode = ClientVersusAIBattleMode(__name__)
    battleMode.registerClient()
    battleMode.registerClientSelector()
    battleMode.registerSquadTypes()
    battleMode.registerClientPlatoon()
    battleMode.registerClientSquadSelector()
    battleMode.registerGameControllers()
    battleMode.registerProviderBattleQueue()
    battleMode.registerDefaultQueueTypePriority()
    battleMode.registerBattleTipCriteria()
    registerVersusAIScaleform()
    registerVersusAIStorage()


def init():
    pass


def start():
    pass


def fini():
    pass
