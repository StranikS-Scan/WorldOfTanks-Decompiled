# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/battle_control/controllers/repositories.py
import teleport_spawn_ctrl
from gui.armor_flashlight.battle_controller import ArmorFlashlightBattleController
from gui.battle_control.controllers.appearance_cache_ctrls import default_appearance_cache_ctrl
from gui.battle_control.controllers import aiming_sounds_ctrl, callout_ctrl, team_bases_ctrl, debug_ctrl, perk_ctrl, default_maps_ctrl, arena_border_ctrl, arena_load_ctrl, avatar_stats_ctrl, drr_scale_ctrl, feedback_adaptor, game_messages_ctrl, hit_direction_ctrl, period_ctrl, personal_efficiency_ctrl, vehicle_state_ctrl, view_points_ctrl, spectator_ctrl, anonymizer_fakes_ctrl, game_restrictions_msgs_ctrl, deathzones_ctrl, prebattle_setups_ctrl, kill_cam_ctrl, battle_field_ctrl, ingame_help_ctrl
from gui.battle_control.controllers import map_zones_ctrl
from gui.battle_control.controllers.auto_shoot_guns.auto_shoot_ctrl import AutoShootControllerFactory
from gui.battle_control.controllers.quest_progress import quest_progress_ctrl
from gui.battle_control.controllers.repositories import SharedControllersRepository, ControllersRepositoryByBonuses
from gui.battle_control.controllers.spam_protection import battle_spam_ctrl
from gui.battle_control.controllers.battle_hints import controller as battle_hints_ctrl
from white_tiger.gui.battle_control.controllers import consumables
from white_tiger.gui.battle_control.controllers.sound_ctrls.wt_battle_sounds import WTBattleSoundController
from white_tiger.gui.battle_control.controllers import chat_cmd_ctrl

class WhiteTigerSharedControllerRepository(SharedControllersRepository):
    __slots__ = ()

    @classmethod
    def create(cls, setup):
        repository = cls()
        from gui.battle_control.controllers import crosshair_proxy
        repository.addController(crosshair_proxy.CrosshairDataProxy())
        ammo = consumables.createAmmoCtrl(setup)
        repository.addViewController(ammo, setup)
        repository.addController(consumables.createEquipmentCtrl(setup))
        repository.addController(consumables.createOptDevicesCtrl(setup))
        state = vehicle_state_ctrl.createCtrl(setup)
        repository.addController(state)
        repository.addController(avatar_stats_ctrl.AvatarStatsController())
        messages = cls.getMessagesController(setup)
        feedback = feedback_adaptor.createFeedbackAdaptor(setup)
        repository.addController(feedback)
        repository.addController(messages)
        repository.addController(chat_cmd_ctrl.WTChatCommandsController(setup, feedback, ammo))
        repository.addController(drr_scale_ctrl.DRRScaleController(messages))
        repository.addController(personal_efficiency_ctrl.createEfficiencyCtrl(setup, feedback, state))
        repository.addController(game_restrictions_msgs_ctrl.createGameRestrictionsMessagesController())
        repository.addController(kill_cam_ctrl.KillCameraController())
        repository.addArenaController(quest_progress_ctrl.createQuestProgressController(), setup)
        repository.addArenaController(view_points_ctrl.ViewPointsController(setup), setup)
        repository.addArenaController(arena_border_ctrl.ArenaBorderController(), setup)
        repository.addArenaController(anonymizer_fakes_ctrl.AnonymizerFakesController(setup), setup)
        repository.addArenaViewController(prebattle_setups_ctrl.PrebattleSetupsController(), setup)
        repository.addArenaViewController(arena_load_ctrl.createArenaLoadController(setup), setup)
        repository.addArenaViewController(period_ctrl.createPeriodCtrl(setup), setup)
        repository.addViewController(hit_direction_ctrl.createHitDirectionController(setup), setup)
        repository.addViewController(game_messages_ctrl.createGameMessagesController(setup), setup)
        repository.addViewController(callout_ctrl.createCalloutController(setup), setup)
        repository.addViewController(spectator_ctrl.SpectatorViewController(), setup)
        repository.addArenaController(cls.getAreaMarkersController(), setup)
        repository.addArenaController(deathzones_ctrl.DeathZonesController(), setup)
        repository.addController(AutoShootControllerFactory.createAutoShootController(setup))
        repository.addController(map_zones_ctrl.MapZonesController(setup))
        repository.addController(battle_spam_ctrl.BattleSpamController())
        repository.addController(aiming_sounds_ctrl.AimingSoundsCtrl())
        repository.addController(ingame_help_ctrl.IngameHelpController(setup))
        repository.addArenaController(ArmorFlashlightBattleController(), setup)
        return repository


class WhiteTigerControllerRepository(ControllersRepositoryByBonuses):
    __slots__ = ()

    @classmethod
    def create(cls, setup):
        repository = super(WhiteTigerControllerRepository, cls).create(setup)
        repository.addArenaViewController(team_bases_ctrl.createTeamsBasesCtrl(setup), setup)
        repository.addViewController(debug_ctrl.DebugController(), setup)
        repository.addViewController(perk_ctrl.PerksController(), setup)
        repository.addViewController(default_maps_ctrl.DefaultMapsController(setup), setup)
        repository.addArenaViewController(battle_field_ctrl.BattleFieldCtrl(), setup)
        repository.addArenaController(default_appearance_cache_ctrl.DefaultAppearanceCacheController(setup), setup)
        repository.addViewController(teleport_spawn_ctrl.TeleportSpawnController(), setup)
        repository.addViewController(battle_hints_ctrl.BattleHintsController(), setup)
        repository.addController(WTBattleSoundController())
        return repository
