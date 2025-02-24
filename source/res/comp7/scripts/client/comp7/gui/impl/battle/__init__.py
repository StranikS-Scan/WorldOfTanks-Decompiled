# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/battle/__init__.py


def registerComp7Battle():
    from arena_component_system.assembler_helper import ARENA_BONUS_TYPE_CAP_COMPONENTS
    from AvatarInputHandler import _INITIAL_MODE_BY_BONUS_TYPE, _CTRL_MODE
    from AvatarInputHandler.MapCaseMode import _STRIKE_SELECTORS
    from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
    from comp7.avatar_input_handler.map_case_mode import Comp7ArenaBoundArtilleryStrikeSelector, Comp7ArenaBoundPlaneStrikeSelector, Comp7PoiArtilleryStrikeSelector
    from comp7.arena_components.comp7_equipment_component import Comp7EquipmentComponent
    from comp7.gui.battle_control.arena_info.arena_vos import Comp7Keys, TournamentComp7Keys
    from comp7.gui.battle_control.controllers.consumables import comp7_equipment_ctrl
    from comp7.gui.ingame_help.detailed_help_pages import Comp7PagesBuilder
    from comp7.helpers.tips import Comp7TipsCriteria
    from comp7_common.comp7_constants import ARENA_GUI_TYPE
    from constants import ARENA_BONUS_TYPE
    from gui.battle_control.arena_info.arena_vos import GAMEMODE_SPECIFIC_KEYS
    from gui.battle_control.controllers import callout_ctrl
    from gui.battle_control.controllers.consumables import extendEquipmentController
    from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
    from gui.shared.system_factory import registerBattleTipCriteria, registerIngameHelpPagesBuilder
    from items import artefacts
    registerBattleTipCriteria(ARENA_GUI_TYPE.COMP7, Comp7TipsCriteria)
    registerBattleTipCriteria(ARENA_GUI_TYPE.TOURNAMENT_COMP7, Comp7TipsCriteria)
    registerBattleTipCriteria(ARENA_GUI_TYPE.TRAINING_COMP7, Comp7TipsCriteria)
    registerIngameHelpPagesBuilder(Comp7PagesBuilder)
    extendEquipmentController({ARENA_BONUS_TYPE.COMP7: comp7_equipment_ctrl.Comp7EquipmentController,
     ARENA_BONUS_TYPE.TOURNAMENT_COMP7: comp7_equipment_ctrl.Comp7EquipmentController,
     ARENA_BONUS_TYPE.TRAINING_COMP7: comp7_equipment_ctrl.Comp7EquipmentController}, {ARENA_BONUS_TYPE.COMP7: comp7_equipment_ctrl.Comp7ReplayEquipmentController})
    GAMEMODE_SPECIFIC_KEYS.update({ARENA_GUI_TYPE.COMP7: Comp7Keys,
     ARENA_GUI_TYPE.TOURNAMENT_COMP7: TournamentComp7Keys,
     ARENA_GUI_TYPE.TRAINING_COMP7: Comp7Keys})
    ARENA_BONUS_TYPE_CAP_COMPONENTS.update({'comp7EquipmentComponent': (ARENA_BONUS_TYPE_CAPS.COMP7, Comp7EquipmentComponent)})
    _INITIAL_MODE_BY_BONUS_TYPE.update({ARENA_BONUS_TYPE.COMP7: _CTRL_MODE.VEHICLES_SELECTION,
     ARENA_BONUS_TYPE.TOURNAMENT_COMP7: _CTRL_MODE.VEHICLES_SELECTION,
     ARENA_BONUS_TYPE.TRAINING_COMP7: _CTRL_MODE.VEHICLES_SELECTION})
    _STRIKE_SELECTORS.update({artefacts.Comp7ReconEquipment: Comp7ArenaBoundPlaneStrikeSelector,
     artefacts.Comp7RedlineEquipment: Comp7ArenaBoundArtilleryStrikeSelector,
     artefacts.PoiArtilleryEquipment: Comp7PoiArtilleryStrikeSelector})
    callout_ctrl._CONSUMERS_LOCKS += (VIEW_ALIAS.COMP7_BATTLE_PAGE,)
