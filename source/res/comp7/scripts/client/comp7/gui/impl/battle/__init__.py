# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/battle/__init__.py


def registerComp7Battle():
    from arena_component_system.assembler_helper import ARENA_BONUS_TYPE_CAP_COMPONENTS
    from AvatarInputHandler import _INITIAL_MODE_BY_BONUS_TYPE, _CTRL_MODE
    from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
    from comp7.gui.battle_control.arena_info.arena_vos import Comp7Keys, TournamentComp7Keys
    from comp7.gui.ingame_help.detailed_help_pages import Comp7PagesBuilder
    from comp7.helpers.tips import Comp7TipsCriteria
    from comp7.arena_components.comp7_equipment_component import Comp7EquipmentComponent
    from comp7_core.gui.battle_control.controllers.consumables import comp7_equipment_ctrl
    from comp7_common.comp7_constants import ARENA_GUI_TYPE
    from constants import ARENA_BONUS_TYPE
    from gui.battle_control.controllers import callout_ctrl
    from gui.battle_control.controllers.consumables import extendEquipmentController
    from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
    from gui.shared.system_factory import registerBattleTipCriteria, registerIngameHelpPagesBuilder, registerGameModeArenaInfoKeys
    registerBattleTipCriteria(ARENA_GUI_TYPE.COMP7, Comp7TipsCriteria)
    registerBattleTipCriteria(ARENA_GUI_TYPE.TOURNAMENT_COMP7, Comp7TipsCriteria)
    registerBattleTipCriteria(ARENA_GUI_TYPE.TRAINING_COMP7, Comp7TipsCriteria)
    registerIngameHelpPagesBuilder(Comp7PagesBuilder)
    extendEquipmentController({ARENA_BONUS_TYPE.COMP7: comp7_equipment_ctrl.Comp7EquipmentController,
     ARENA_BONUS_TYPE.TOURNAMENT_COMP7: comp7_equipment_ctrl.Comp7EquipmentController,
     ARENA_BONUS_TYPE.TRAINING_COMP7: comp7_equipment_ctrl.Comp7EquipmentController}, {ARENA_BONUS_TYPE.COMP7: comp7_equipment_ctrl.Comp7ReplayEquipmentController,
     ARENA_BONUS_TYPE.TOURNAMENT_COMP7: comp7_equipment_ctrl.Comp7ReplayEquipmentController,
     ARENA_BONUS_TYPE.TRAINING_COMP7: comp7_equipment_ctrl.Comp7ReplayEquipmentController})
    registerGameModeArenaInfoKeys(ARENA_GUI_TYPE.COMP7, Comp7Keys)
    registerGameModeArenaInfoKeys(ARENA_GUI_TYPE.TOURNAMENT_COMP7, TournamentComp7Keys)
    registerGameModeArenaInfoKeys(ARENA_GUI_TYPE.TRAINING_COMP7, Comp7Keys)
    ARENA_BONUS_TYPE_CAP_COMPONENTS.update({'comp7EquipmentComponent': (ARENA_BONUS_TYPE_CAPS.COMP7, Comp7EquipmentComponent)})
    _INITIAL_MODE_BY_BONUS_TYPE.update({ARENA_BONUS_TYPE.COMP7: _CTRL_MODE.VEHICLES_SELECTION,
     ARENA_BONUS_TYPE.TOURNAMENT_COMP7: _CTRL_MODE.VEHICLES_SELECTION,
     ARENA_BONUS_TYPE.TRAINING_COMP7: _CTRL_MODE.VEHICLES_SELECTION})
    callout_ctrl._CONSUMERS_LOCKS += (VIEW_ALIAS.COMP7_BATTLE_PAGE,)
    _extendEquipmentProperties()
    _extendEquipmentSounds()


def _extendEquipmentProperties():
    from ApplicationPoint import _Comp7ReconApplicationPointEffect, _Comp7RedLineApplicationPointEffect, _EQUIPMENT_APPLICATION_POINTS
    from AvatarInputHandler.MapCaseMode import _STRIKE_SELECTORS
    from comp7_core.avatar_input_handler.map_case_mode import Comp7ArenaBoundArtilleryStrikeSelector, Comp7ArenaBoundPlaneStrikeSelector, Comp7PoiArtilleryStrikeSelector
    from comp7_core.gui.battle_control.controllers.consumables.comp7_equipment_items import _ROLE_SKILL_ITEM_CLASS_BY_NAME, _REPLAY_ROLE_SKILL_ITEM_CLASS_BY_NAME, _RoleSkillArtyVSItem, _RoleSkillReconVSItem, _ReplayRoleSkillArtyVSItem
    from comp7_common.items.comp7_artefacts import Comp7ReconEquipment, Comp7RedlineEquipment
    from items.artefacts import PoiArtilleryEquipment
    _ROLE_SKILL_ITEM_CLASS_BY_NAME.update({'comp7_recon': _RoleSkillReconVSItem,
     'comp7_redline': _RoleSkillArtyVSItem})
    _REPLAY_ROLE_SKILL_ITEM_CLASS_BY_NAME.update({'comp7_redline': _ReplayRoleSkillArtyVSItem})
    _EQUIPMENT_APPLICATION_POINTS.update({'comp7_recon': _Comp7ReconApplicationPointEffect,
     'comp7_redline': _Comp7RedLineApplicationPointEffect})
    _STRIKE_SELECTORS.update({Comp7ReconEquipment: Comp7ArenaBoundPlaneStrikeSelector,
     Comp7RedlineEquipment: Comp7ArenaBoundArtilleryStrikeSelector,
     PoiArtilleryEquipment: Comp7PoiArtilleryStrikeSelector})


def _extendEquipmentSounds():
    from comp7_core.gui.battle_control.controllers.sound_ctrls.comp7_battle_sounds import _EQUIPMENT_ACTIVATED_SOUNDS, _EQUIPMENT_DEACTIVATED_SOUNDS, _EQUIPMENT_PREPARING_START_SOUNDS, _EQUIPMENT_PREPARING_CANCEL_SOUNDS, _EQUIPMENT_PRE_DEACTIVATION_SOUNDS, _EQUIPMENT_ARTILLERY_NAMES, _PreDeactivationParams
    _EQUIPMENT_ACTIVATED_SOUNDS.update({'comp7_hunter': 'comp_7_ability_buff_common',
     'comp7_aoe_heal': 'comp_7_ability_aoe_heal_apply',
     'comp7_ally_support': 'comp_7_ability_buff_common',
     'comp7_concentration': 'comp_7_ability_buff_common',
     'comp7_fast_recharge': 'comp_7_ability_buff_common',
     'comp7_juggernaut': 'comp_7_ability_buff_common',
     'comp7_risky_attack': 'comp_7_ability_buff_common',
     'comp7_recon': 'comp_7_ability_uav',
     'comp7_berserk': 'comp_7_ability_buff_common',
     'comp7_sure_shot': 'comp_7_ability_buff_common',
     'comp7_sniper': 'comp_7_ability_bullseye',
     'comp7_aggressive_detection': 'comp_7_ability_wheel',
     'comp7_march': 'comp_7_ability_buff_common',
     'comp7_redline': 'comp_7_ability_arty_apply'})
    _EQUIPMENT_DEACTIVATED_SOUNDS.update({'comp7_aoe_heal': 'comp_7_ability_aoe_heal_stop',
     'comp7_hunter': 'comp_7_ability_buff_end',
     'comp7_ally_support': 'comp_7_ability_buff_end',
     'comp7_concentration': 'comp_7_ability_buff_end',
     'comp7_fast_recharge': 'comp_7_ability_buff_end',
     'comp7_juggernaut': 'comp_7_ability_buff_end',
     'comp7_risky_attack': 'comp_7_ability_buff_end',
     'comp7_berserk': 'comp_7_ability_buff_end',
     'comp7_sure_shot': 'comp_7_ability_buff_end',
     'comp7_sniper': 'comp_7_ability_buff_end',
     'comp7_aggressive_detection': 'comp_7_ability_buff_end',
     'comp7_march': 'comp_7_ability_buff_end'})
    _EQUIPMENT_PREPARING_START_SOUNDS.update({'comp7_redline': 'comp_7_ability_arty_aim'})
    _EQUIPMENT_PREPARING_CANCEL_SOUNDS.update({'comp7_redline': 'comp_7_ability_arty_cancel'})
    _EQUIPMENT_PRE_DEACTIVATION_SOUNDS.update({'comp7_aoe_inspire': _PreDeactivationParams('comp_7_ability_insp_stop', 3.0)})
    _EQUIPMENT_ARTILLERY_NAMES.append('comp7_redline')
