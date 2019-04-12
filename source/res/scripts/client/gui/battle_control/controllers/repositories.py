# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/repositories.py
from debug_utils import LOG_ERROR, LOG_DEBUG
from gui.battle_control.arena_info.interfaces import IArenaController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID, REUSABLE_BATTLE_CTRL_IDS
from gui.battle_control.battle_constants import getBattleCtrlName
from gui.battle_control.controllers import arena_border_ctrl
from gui.battle_control.controllers import arena_load_ctrl, battle_field_ctrl
from gui.battle_control.controllers import avatar_stats_ctrl
from gui.battle_control.controllers import bootcamp_ctrl
from gui.battle_control.controllers import chat_cmd_ctrl
from gui.battle_control.controllers import consumables
from gui.battle_control.controllers import debug_ctrl
from gui.battle_control.controllers import drr_scale_ctrl
from gui.battle_control.controllers import dyn_squad_functional
from gui.battle_control.controllers import feedback_adaptor
from gui.battle_control.controllers import game_messages_ctrl
from gui.battle_control.controllers import hit_direction_ctrl
from gui.battle_control.controllers import interfaces
from gui.battle_control.controllers import msgs_ctrl
from gui.battle_control.controllers import period_ctrl
from gui.battle_control.controllers import personal_efficiency_ctrl
from gui.battle_control.controllers import respawn_ctrl
from gui.battle_control.controllers import team_bases_ctrl
from gui.battle_control.controllers import team_health_bar_ctrl
from gui.battle_control.controllers import tmp_ignore_list_ctrl
from gui.battle_control.controllers import vehicle_state_ctrl
from gui.battle_control.controllers import view_points_ctrl
from gui.battle_control.controllers.quest_progress import quest_progress_ctrl
from skeletons.gui.battle_session import ISharedControllersLocator, IDynamicControllersLocator
from gui.battle_control.controllers import epic_respawn_ctrl
from gui.battle_control.controllers import progress_circle_ctrl
from gui.battle_control.controllers import epic_maps_ctrl
from gui.battle_control.controllers import epic_spectator_ctrl
from gui.battle_control.controllers import epic_missions_ctrl
from gui.battle_control.controllers import game_notification_ctrl
from gui.battle_control.controllers import epic_team_bases_ctrl

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
        return self.replayCtrl.isPlaying and not self.replayCtrl.isBattleSimulation if self.replayCtrl is not None else False

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
    def battleCacheCtrl(self):
        return self._repository.getController(BATTLE_CTRL_ID.TMP_IGNORE_LIST_CTRL)

    @property
    def viewPoints(self):
        return self._repository.getController(BATTLE_CTRL_ID.VIEW_POINTS)

    @property
    def questProgress(self):
        return self._repository.getController(BATTLE_CTRL_ID.QUEST_PROGRESS)


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
        repository.addController(ammo)
        repository.addController(consumables.createEquipmentCtrl(setup))
        repository.addController(consumables.createOptDevicesCtrl())
        state = vehicle_state_ctrl.createCtrl(setup)
        repository.addController(state)
        repository.addController(avatar_stats_ctrl.AvatarStatsController())
        feedback = feedback_adaptor.createFeedbackAdaptor(setup)
        messages = msgs_ctrl.createBattleMessagesCtrl(setup)
        repository.addController(feedback)
        repository.addController(messages)
        repository.addController(chat_cmd_ctrl.ChatCommandsController(setup, feedback, ammo))
        repository.addController(drr_scale_ctrl.DRRScaleController(messages))
        repository.addController(personal_efficiency_ctrl.createEfficiencyCtrl(setup, feedback, state))
        tmpIgnoreListCtrl = tmp_ignore_list_ctrl.createTmpIgnoreListCtrl(setup)
        if tmpIgnoreListCtrl is not None:
            repository.addController(tmpIgnoreListCtrl)
        repository.addArenaController(bootcamp_ctrl.BootcampController(), setup)
        repository.addArenaController(quest_progress_ctrl.createQuestProgressController(), setup)
        repository.addArenaController(view_points_ctrl.ViewPointsController(setup), setup)
        repository.addArenaController(arena_border_ctrl.ArenaBorderController(), setup)
        repository.addArenaViewController(arena_load_ctrl.createArenaLoadController(setup), setup)
        repository.addArenaViewController(period_ctrl.createPeriodCtrl(setup), setup)
        repository.addViewController(hit_direction_ctrl.createHitDirectionController(setup), setup)
        repository.addViewController(game_messages_ctrl.createGameMessagesController(setup), setup)
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
        return repository


class ClassicControllersRepository(_ControllersRepositoryByBonuses):
    __slots__ = ()

    @classmethod
    def create(cls, setup):
        repository = super(ClassicControllersRepository, cls).create(setup)
        repository.addArenaViewController(team_bases_ctrl.createTeamsBasesCtrl(setup), setup)
        repository.addArenaController(dyn_squad_functional.DynSquadFunctional(setup), setup)
        repository.addViewController(debug_ctrl.DebugController(), setup)
        repository.addArenaViewController(battle_field_ctrl.BattleFieldCtrl(), setup)
        return repository


class EpicControllersRepository(_ControllersRepository):
    __slots__ = ()

    @classmethod
    def create(cls, setup):
        repository = super(EpicControllersRepository, cls).create(setup)
        repository.addViewController(epic_respawn_ctrl.EpicRespawnsController(setup), setup)
        repository.addController(progress_circle_ctrl.ProgressTimerController(setup))
        repository.addViewController(epic_maps_ctrl.MapsController(setup), setup)
        repository.addViewController(debug_ctrl.DebugController(), setup)
        repository.addViewController(epic_spectator_ctrl.SpectatorViewController(setup), setup)
        repository.addArenaController(dyn_squad_functional.DynSquadFunctional(setup), setup)
        repository.addViewController(game_notification_ctrl.EpicGameNotificationsController(setup), setup)
        repository.addViewController(epic_missions_ctrl.EpicMissionsController(setup), setup)
        repository.addArenaViewController(epic_team_bases_ctrl.createEpicTeamsBasesCtrl(setup), setup)
        return repository
