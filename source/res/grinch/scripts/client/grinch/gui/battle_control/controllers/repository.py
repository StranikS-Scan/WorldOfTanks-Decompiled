# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/battle_control/controllers/repository.py
import typing
from grinch.gui.battle_control.controllers.ingame_help_ctrl import GrinchIngameHelpController
from grinch.gui.battle_control.controllers.settings_contoller import OverrideSettingsController
from gui.battle_control.controllers import aiming_sounds_ctrl
from grinch.gui.battle_control.controllers import callout_ctrl
from gui.battle_control.controllers import arena_border_ctrl, arena_load_ctrl, avatar_stats_ctrl, chat_cmd_ctrl, consumables, drr_scale_ctrl, feedback_adaptor, game_messages_ctrl, hit_direction_ctrl, period_ctrl, personal_efficiency_ctrl, vehicle_state_ctrl, view_points_ctrl, spectator_ctrl, anonymizer_fakes_ctrl, game_restrictions_msgs_ctrl, deathzones_ctrl, prebattle_setups_ctrl, kill_cam_ctrl
from gui.battle_control.controllers import map_zones_ctrl
from gui.battle_control.controllers.auto_shoot_guns.auto_shoot_ctrl import AutoShootControllerFactory
from gui.battle_control.controllers.quest_progress import quest_progress_ctrl
from gui.battle_control.controllers.repositories import ClassicControllersRepository, SharedControllersRepository
from gui.battle_control.controllers.spam_protection import battle_spam_ctrl
if typing.TYPE_CHECKING:
    from gui.battle_control import BattleSessionSetup

class GrinchSharedControllerRepository(SharedControllersRepository):
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
        repository.addController(chat_cmd_ctrl.ChatCommandsController(setup, feedback, ammo))
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
        repository.addController(GrinchIngameHelpController(setup))
        return repository


class GrinchBattleControllerRepository(ClassicControllersRepository):
    __slots__ = ()

    @classmethod
    def create(cls, setup):
        repository = super(GrinchBattleControllerRepository, cls).create(setup)
        repository.addArenaController(OverrideSettingsController(), setup)
        return repository
