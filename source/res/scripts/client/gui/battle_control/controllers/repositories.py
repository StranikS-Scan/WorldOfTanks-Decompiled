# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/repositories.py
from typing import TYPE_CHECKING
from constants import ARENA_GUI_TYPE
from debug_utils import LOG_ERROR, LOG_DEBUG
from gui.battle_control.arena_info.interfaces import IArenaController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID, REUSABLE_BATTLE_CTRL_IDS, getBattleCtrlName
from gui.battle_control.controllers import arena_border_ctrl, arena_load_ctrl, battle_field_ctrl, avatar_stats_ctrl, bootcamp_ctrl, chat_cmd_ctrl, consumables, debug_ctrl, drr_scale_ctrl, dyn_squad_functional, feedback_adaptor, game_messages_ctrl, hit_direction_ctrl, interfaces, msgs_ctrl, period_ctrl, personal_efficiency_ctrl, respawn_ctrl, team_bases_ctrl, vehicle_state_ctrl, view_points_ctrl, epic_respawn_ctrl, progress_circle_ctrl, ingame_help_ctrl, epic_maps_ctrl, default_maps_ctrl, epic_spectator_ctrl, epic_missions_ctrl, game_notification_ctrl, epic_team_bases_ctrl, anonymizer_fakes_ctrl, game_restrictions_msgs_ctrl, callout_ctrl, deathzones_ctrl, dog_tags_ctrl, team_health_bar_ctrl, battle_notifier_ctrl, prebattle_setups_ctrl, perk_ctrl
from gui.battle_control.controllers import aiming_sounds_ctrl
from gui.battle_control.controllers import battle_hints_ctrl
from gui.battle_control.controllers import map_zones_ctrl
from gui.battle_control.controllers import points_of_interest_ctrl
from gui.battle_control.controllers.appearance_cache_ctrls.comp7_appearance_cache_ctrl import Comp7AppearanceCacheController
from gui.battle_control.controllers.appearance_cache_ctrls.default_appearance_cache_ctrl import DefaultAppearanceCacheController
from gui.battle_control.controllers.appearance_cache_ctrls.event_appearance_cache_ctrl import EventAppearanceCacheController
from gui.battle_control.controllers.appearance_cache_ctrls.maps_training_appearance_cache_ctrl import MapsTrainingAppearanceCacheController
from gui.battle_control.controllers.comp7_prebattle_setup_ctrl import Comp7PrebattleSetupController
from gui.battle_control.controllers.comp7_voip_ctrl import Comp7VOIPController
from gui.battle_control.controllers.quest_progress import quest_progress_ctrl
from gui.battle_control.controllers.sound_ctrls.comp7_battle_sounds import Comp7BattleSoundController
from gui.battle_control.controllers.sound_ctrls.stronghold_battle_sounds import StrongholdBattleSoundController
from gui.shared.system_factory import registerBattleControllerRepo
from skeletons.gui.battle_session import ISharedControllersLocator, IDynamicControllersLocator
if TYPE_CHECKING:
    from gui.battle_control.controllers.consumables.equipment_ctrl import EquipmentsController

class BattleSessionSetup(object):
    __slots__ = ('avatar', 'replayCtrl', 'gasAttackMgr', 'sessionProvider')

    def __init__(self, avatar=None, replayCtrl=None, gasAttackMgr=None, sessionProvider=None):
        super(BattleSessionSetup, self).__init__()
        self.avatar = avatar
        self.replayCtrl = replayCtrl
        self.gasAttackMgr = gasAttackMgr
        self.sessionProvider = sessionProvider

    @property
    def isReplayPlaying(self):
        return self.replayCtrl.isPlaying if self.replayCtrl is not None else False

    @property
    def isReplayRecording(self):
        return self.replayCtrl.isRecording if self.replayCtrl is not None else False

    @property
    def battleCtx(self):
        return self.sessionProvider.getCtx()

    @property
    def arenaDP(self):
        return self.sessionProvider.getArenaDP()

    @property
    def arenaVisitor(self):
        return self.sessionProvider.arenaVisitor

    @property
    def arenaEntity(self):
        return self.avatar.arena

    def registerArenaCtrl(self, controller):
        return self.sessionProvider.addArenaCtrl(controller)

    def registerViewComponentsCtrl(self, controller):
        return self.sessionProvider.registerViewComponentsCtrl(controller)

    def clear(self):
        self.avatar = None
        self.replayCtrl = None
        self.gasAttackMgr = None
        self.sessionProvider = None
        return


class _ControllersLocator(object):
    __slots__ = ('_repository',)

    def __init__(self, repository=None):
        super(_ControllersLocator, self).__init__()
        if repository is not None:
            self._repository = repository
        else:
            self._repository = _EmptyRepository()
        return

    def destroy(self):
        self._repository.destroy()


class SharedControllersLocator(_ControllersLocator, ISharedControllersLocator):
    __slots__ = ()

    @property
    def ammo(self):
        return self._repository.getController(BATTLE_CTRL_ID.AMMO)

    @property
    def equipments(self):
        return self._repository.getController(BATTLE_CTRL_ID.EQUIPMENTS)

    @property
    def optionalDevices(self):
        return self._repository.getController(BATTLE_CTRL_ID.OPTIONAL_DEVICES)

    @property
    def prebattleSetups(self):
        return self._repository.getController(BATTLE_CTRL_ID.PREBATTLE_SETUPS_CTRL)

    @property
    def vehicleState(self):
        return self._repository.getController(BATTLE_CTRL_ID.OBSERVED_VEHICLE_STATE)

    @property
    def hitDirection(self):
        return self._repository.getController(BATTLE_CTRL_ID.HIT_DIRECTION)

    @property
    def arenaLoad(self):
        return self._repository.getController(BATTLE_CTRL_ID.ARENA_LOAD_PROGRESS)

    @property
    def arenaPeriod(self):
        return self._repository.getController(BATTLE_CTRL_ID.ARENA_PERIOD)

    @property
    def feedback(self):
        return self._repository.getController(BATTLE_CTRL_ID.FEEDBACK)

    @property
    def chatCommands(self):
        return self._repository.getController(BATTLE_CTRL_ID.CHAT_COMMANDS)

    @property
    def messages(self):
        return self._repository.getController(BATTLE_CTRL_ID.MESSAGES)

    @property
    def drrScale(self):
        return self._repository.getController(BATTLE_CTRL_ID.DRR_SCALE)

    @property
    def privateStats(self):
        return self._repository.getController(BATTLE_CTRL_ID.AVATAR_PRIVATE_STATS)

    @property
    def crosshair(self):
        return self._repository.getController(BATTLE_CTRL_ID.CROSSHAIR)

    @property
    def personalEfficiencyCtrl(self):
        return self._repository.getController(BATTLE_CTRL_ID.PERSONAL_EFFICIENCY)

    @property
    def anonymizerFakesCtrl(self):
        return self._repository.getController(BATTLE_CTRL_ID.ANONYMIZER_FAKES)

    @property
    def viewPoints(self):
        return self._repository.getController(BATTLE_CTRL_ID.VIEW_POINTS)

    @property
    def questProgress(self):
        return self._repository.getController(BATTLE_CTRL_ID.QUEST_PROGRESS)

    @property
    def calloutCtrl(self):
        return self._repository.getController(BATTLE_CTRL_ID.CALLOUT)

    @property
    def areaMarker(self):
        return self._repository.getController(BATTLE_CTRL_ID.AREA_MARKER)

    @property
    def arenaBorder(self):
        return self._repository.getController(BATTLE_CTRL_ID.ARENA_BORDER)

    @property
    def deathzones(self):
        return self._repository.getController(BATTLE_CTRL_ID.DEATHZONES)

    @property
    def ingameHelp(self):
        return self._repository.getController(BATTLE_CTRL_ID.INGAME_HELP_CTRL)

    @property
    def mapZones(self):
        return self._repository.getController(BATTLE_CTRL_ID.MAP_ZONES_CONTROLLER)

    @property
    def aimingSounds(self):
        return self._repository.getController(BATTLE_CTRL_ID.AIMING_SOUNDS_CTRL)


class DynamicControllersLocator(_ControllersLocator, IDynamicControllersLocator):
    __slots__ = ()

    @property
    def debug(self):
        return self._repository.getController(BATTLE_CTRL_ID.DEBUG)

    @property
    def teamBases(self):
        return self._repository.getController(BATTLE_CTRL_ID.TEAM_BASES)

    @property
    def progressTimer(self):
        return self._repository.getController(BATTLE_CTRL_ID.PROGRESS_TIMER)

    @property
    def maps(self):
        return self._repository.getController(BATTLE_CTRL_ID.MAPS)

    @property
    def spectator(self):
        return self._repository.getController(BATTLE_CTRL_ID.SPECTATOR)

    @property
    def missions(self):
        return self._repository.getController(BATTLE_CTRL_ID.EPIC_MISSIONS)

    @property
    def respawn(self):
        return self._repository.getController(BATTLE_CTRL_ID.RESPAWN)

    @property
    def dynSquads(self):
        return self._repository.getController(BATTLE_CTRL_ID.DYN_SQUADS)

    @property
    def battleField(self):
        return self._repository.getController(BATTLE_CTRL_ID.BATTLE_FIELD_CTRL)

    @property
    def repair(self):
        return self._repository.getController(BATTLE_CTRL_ID.REPAIR)

    @property
    def playerGameModeData(self):
        return self._repository.getController(BATTLE_CTRL_ID.PLAYER_GAME_MODE_DATA)

    @property
    def teamHealthBar(self):
        return self._repository.getController(BATTLE_CTRL_ID.TEAM_HEALTH_BAR)

    @property
    def gameNotifications(self):
        return self._repository.getController(BATTLE_CTRL_ID.GAME_NOTIFICATIONS)

    @property
    def progression(self):
        return self._repository.getController(BATTLE_CTRL_ID.PROGRESSION_CTRL)

    @property
    def radar(self):
        return self._repository.getController(BATTLE_CTRL_ID.RADAR_CTRL)

    @property
    def spawn(self):
        return self._repository.getController(BATTLE_CTRL_ID.SPAWN_CTRL)

    @property
    def deathScreen(self):
        return self._repository.getController(BATTLE_CTRL_ID.DEATH_SCREEN_CTRL)

    @property
    def vehicleCount(self):
        return self._repository.getController(BATTLE_CTRL_ID.VEHICLES_COUNT_CTRL)

    @property
    def perks(self):
        return self._repository.getController(BATTLE_CTRL_ID.PERKS)

    @property
    def battleHints(self):
        return self._repository.getController(BATTLE_CTRL_ID.BATTLE_HINTS)

    @property
    def dogTags(self):
        return self._repository.getController(BATTLE_CTRL_ID.DOG_TAGS)

    @property
    def battleNotifier(self):
        return self._repository.getController(BATTLE_CTRL_ID.BATTLE_NOTIFIER)

    @property
    def soundPlayers(self):
        return self._repository.getController(BATTLE_CTRL_ID.SOUND_PLAYERS_CTRL)

    @property
    def appearanceCache(self):
        return self._repository.getController(BATTLE_CTRL_ID.APPEARANCE_CACHE_CTRL)

    @property
    def pointsOfInterest(self):
        return self._repository.getController(BATTLE_CTRL_ID.POINTS_OF_INTEREST_CTRL)

    @property
    def comp7PrebattleSetup(self):
        return self._repository.getController(BATTLE_CTRL_ID.COMP7_PREBATTLE_SETUP_CTRL)

    @property
    def comp7VOIPController(self):
        return self._repository.getController(BATTLE_CTRL_ID.COMP7_VOIP_CTRL)

    @property
    def overrideSettingsController(self):
        return self._repository.getController(BATTLE_CTRL_ID.OVERRIDE_SETTINGS)


class _EmptyRepository(interfaces.IBattleControllersRepository):
    __slots__ = ()

    @classmethod
    def create(cls, setup):
        return cls()

    def destroy(self):
        pass

    def getController(self, ctrlID):
        return None

    def addController(self, ctrl):
        pass


class _ControllersRepository(interfaces.IBattleControllersRepository):
    __slots__ = ('_ctrls',)

    def __init__(self):
        super(_ControllersRepository, self).__init__()
        self._ctrls = {}

    @classmethod
    def create(cls, setup):
        return cls()

    def destroy(self):
        while self._ctrls:
            _, ctrl = self._ctrls.popitem()
            ctrl.stopControl()
            LOG_DEBUG('GUI Controller is stopped', getBattleCtrlName(ctrl.getControllerID()))

    def getController(self, ctrlID):
        return self._ctrls[ctrlID] if ctrlID in self._ctrls else None

    def addController(self, ctrl):
        ctrlID = ctrl.getControllerID()
        if ctrlID in REUSABLE_BATTLE_CTRL_IDS:
            LOG_ERROR('Controller can not be added to repository, controllerID is not unique', ctrlID)
            return
        if ctrlID in self._ctrls:
            LOG_ERROR('Controller with given ID already exists', ctrlID)
            return
        self._ctrls[ctrlID] = ctrl
        if not isinstance(ctrl, IArenaController):
            ctrl.startControl()
        LOG_DEBUG('GUI Controller is started', getBattleCtrlName(ctrlID))

    def addArenaController(self, ctrl, setup):
        if setup.registerArenaCtrl(ctrl):
            self.addController(ctrl)

    def addViewController(self, ctrl, setup):
        if setup.registerViewComponentsCtrl(ctrl):
            self.addController(ctrl)

    def addArenaViewController(self, ctrl, setup):
        if setup.registerArenaCtrl(ctrl) and setup.registerViewComponentsCtrl(ctrl):
            self.addController(ctrl)


class SharedControllersRepository(_ControllersRepository):
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
        messages = msgs_ctrl.createBattleMessagesCtrl(setup)
        feedback = feedback_adaptor.createFeedbackAdaptor(setup)
        repository.addController(feedback)
        repository.addController(messages)
        repository.addController(chat_cmd_ctrl.ChatCommandsController(setup, feedback, ammo))
        repository.addController(drr_scale_ctrl.DRRScaleController(messages))
        repository.addController(personal_efficiency_ctrl.createEfficiencyCtrl(setup, feedback, state))
        repository.addController(game_restrictions_msgs_ctrl.createGameRestrictionsMessagesController())
        repository.addArenaController(bootcamp_ctrl.BootcampController(), setup)
        repository.addArenaController(quest_progress_ctrl.createQuestProgressController(), setup)
        repository.addArenaController(view_points_ctrl.ViewPointsController(setup), setup)
        guiVisitor = setup.arenaVisitor.gui
        if guiVisitor.isBattleRoyale():
            repository.addArenaController(arena_border_ctrl.BattleRoyaleBorderCtrl(), setup)
        else:
            repository.addArenaController(arena_border_ctrl.ArenaBorderController(), setup)
        repository.addArenaController(anonymizer_fakes_ctrl.AnonymizerFakesController(setup), setup)
        repository.addArenaViewController(prebattle_setups_ctrl.PrebattleSetupsController(), setup)
        repository.addArenaViewController(arena_load_ctrl.createArenaLoadController(setup), setup)
        repository.addArenaViewController(period_ctrl.createPeriodCtrl(setup), setup)
        repository.addViewController(hit_direction_ctrl.createHitDirectionController(setup), setup)
        repository.addViewController(game_messages_ctrl.createGameMessagesController(setup), setup)
        repository.addViewController(callout_ctrl.createCalloutController(setup), setup)
        from gui.battle_control.controllers import area_marker_ctrl
        repository.addArenaController(area_marker_ctrl.AreaMarkersController(), setup)
        repository.addArenaController(deathzones_ctrl.DeathZonesController(), setup)
        repository.addController(ingame_help_ctrl.IngameHelpController(setup))
        repository.addController(map_zones_ctrl.MapZonesController(setup))
        repository.addController(aiming_sounds_ctrl.AimingSoundsCtrl())
        return repository


class _ControllersRepositoryByBonuses(_ControllersRepository):
    __slots__ = ()

    @classmethod
    def create(cls, setup):
        repository = super(_ControllersRepositoryByBonuses, cls).create(setup)
        arenaVisitor = setup.arenaVisitor
        if arenaVisitor.hasRespawns():
            repository.addViewController(respawn_ctrl.RespawnsController(setup), setup)
        if arenaVisitor.hasHealthBar():
            repository.addViewController(team_health_bar_ctrl.TeamHealthBarController(setup), setup)
        if arenaVisitor.hasDogTag():
            repository.addController(dog_tags_ctrl.DogTagsController(setup))
        if arenaVisitor.hasDynSquads():
            repository.addArenaController(dyn_squad_functional.DynSquadFunctional(setup), setup)
        if arenaVisitor.hasBattleNotifier():
            repository.addViewController(battle_notifier_ctrl.BattleNotifierController(setup), setup)
        if arenaVisitor.hasPointsOfInterest():
            repository.addController(points_of_interest_ctrl.PointsOfInterestController(setup))
        return repository


class ClassicControllersRepository(_ControllersRepositoryByBonuses):
    __slots__ = ()

    @classmethod
    def create(cls, setup):
        repository = super(ClassicControllersRepository, cls).create(setup)
        repository.addArenaViewController(team_bases_ctrl.createTeamsBasesCtrl(setup), setup)
        repository.addViewController(debug_ctrl.DebugController(), setup)
        repository.addViewController(perk_ctrl.PerksController(), setup)
        repository.addViewController(default_maps_ctrl.DefaultMapsController(setup), setup)
        repository.addArenaViewController(battle_field_ctrl.BattleFieldCtrl(), setup)
        repository.addArenaController(cls._getAppearanceCacheController(setup), setup)
        return repository

    @staticmethod
    def _getAppearanceCacheController(setup):
        return DefaultAppearanceCacheController(setup)


class EpicControllersRepository(_ControllersRepository):
    __slots__ = ()

    @classmethod
    def create(cls, setup):
        repository = super(EpicControllersRepository, cls).create(setup)
        repository.addViewController(epic_respawn_ctrl.EpicRespawnsController(setup), setup)
        repository.addController(progress_circle_ctrl.ProgressTimerController(setup))
        repository.addViewController(epic_maps_ctrl.EpicMapsController(setup), setup)
        repository.addViewController(debug_ctrl.DebugController(), setup)
        repository.addViewController(epic_spectator_ctrl.SpectatorViewController(setup), setup)
        repository.addViewController(perk_ctrl.PerksController(), setup)
        repository.addArenaController(dyn_squad_functional.DynSquadFunctional(setup), setup)
        repository.addViewController(game_notification_ctrl.EpicGameNotificationsController(setup), setup)
        repository.addViewController(epic_missions_ctrl.EpicMissionsController(setup), setup)
        repository.addArenaViewController(battle_field_ctrl.BattleFieldCtrl(), setup)
        repository.addArenaViewController(epic_team_bases_ctrl.createEpicTeamsBasesCtrl(setup), setup)
        repository.addArenaController(DefaultAppearanceCacheController(setup), setup)
        repository.addViewController(battle_hints_ctrl.createBattleHintsController(), setup)
        return repository


class EventControllerRepository(_ControllersRepositoryByBonuses):
    __slots__ = ()

    @classmethod
    def create(cls, setup):
        repository = super(EventControllerRepository, cls).create(setup)
        repository.addArenaViewController(team_bases_ctrl.createTeamsBasesCtrl(setup), setup)
        repository.addViewController(debug_ctrl.DebugController(), setup)
        repository.addViewController(default_maps_ctrl.DefaultMapsController(setup), setup)
        repository.addArenaViewController(battle_field_ctrl.BattleFieldCtrl(), setup)
        repository.addViewController(perk_ctrl.PerksController(), setup)
        repository.addViewController(battle_hints_ctrl.createBattleHintsController(), setup)
        repository.addArenaController(EventAppearanceCacheController(setup), setup)
        return repository


class MapsTrainingControllerRepository(_ControllersRepositoryByBonuses):
    __slots__ = ()

    @classmethod
    def create(cls, setup):
        from gui.Scaleform.daapi.view.battle.maps_training import battle_hints_mt
        repository = super(MapsTrainingControllerRepository, cls).create(setup)
        repository.addArenaViewController(team_bases_ctrl.createTeamsBasesCtrl(setup), setup)
        repository.addArenaController(dyn_squad_functional.DynSquadFunctional(setup), setup)
        repository.addViewController(debug_ctrl.DebugController(), setup)
        repository.addViewController(default_maps_ctrl.DefaultMapsController(setup), setup)
        repository.addViewController(game_messages_ctrl.createGameMessagesController(setup), setup)
        repository.addArenaViewController(battle_field_ctrl.BattleFieldCtrl(), setup)
        repository.addViewController(battle_hints_mt.createBattleHintsController(), setup)
        repository.addArenaController(MapsTrainingAppearanceCacheController(setup), setup)
        return repository


class StrongholdControllerRepository(ClassicControllersRepository):
    __slots__ = ()

    @classmethod
    def create(cls, setup):
        repository = super(StrongholdControllerRepository, cls).create(setup)
        repository.addController(StrongholdBattleSoundController())
        return repository


class Comp7ControllerRepository(ClassicControllersRepository):
    __slots__ = ()

    @classmethod
    def create(cls, setup):
        repository = super(Comp7ControllerRepository, cls).create(setup)
        repository.addArenaViewController(Comp7PrebattleSetupController(), setup)
        repository.addArenaController(Comp7VOIPController(), setup)
        repository.addController(Comp7BattleSoundController())
        return repository

    @staticmethod
    def _getAppearanceCacheController(setup):
        return Comp7AppearanceCacheController(setup)


for guiType in ARENA_GUI_TYPE.EPIC_RANGE:
    registerBattleControllerRepo(guiType, EpicControllersRepository)

for guiType in ARENA_GUI_TYPE.STRONGHOLD_RANGE:
    registerBattleControllerRepo(guiType, StrongholdControllerRepository)

registerBattleControllerRepo(ARENA_GUI_TYPE.EVENT_BATTLES, EventControllerRepository)
registerBattleControllerRepo(ARENA_GUI_TYPE.MAPS_TRAINING, MapsTrainingControllerRepository)
registerBattleControllerRepo(ARENA_GUI_TYPE.COMP7, Comp7ControllerRepository)
