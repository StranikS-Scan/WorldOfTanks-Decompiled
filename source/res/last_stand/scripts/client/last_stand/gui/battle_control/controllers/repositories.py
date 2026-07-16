# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/battle_control/controllers/repositories.py
from __future__ import absolute_import
import typing
from last_stand.skeletons.ls_controller import ILSController
from gui.battle_control.controllers import battle_field_ctrl, debug_ctrl, team_bases_ctrl, default_maps_ctrl, perk_ctrl, personal_death_zones_gui_ctrl
from gui.battle_control.controllers.battle_hints import controller as battle_hints_ctrl
from gui.battle_control.controllers.repositories import ControllersRepositoryByBonuses, SharedControllersRepository
from gui.battle_control.controllers.sound_ctrls.common import ShotsResultSoundController
from last_stand.gui.battle_control.controllers import appearance_cache_ctrl
from last_stand.gui.battle_control.controllers import battle_gui_controller
from last_stand.gui.battle_control.controllers import voip_ctrl
from last_stand.gui.battle_control.controllers.chat_cmd_ctrl import LSChatCommandsController
from helpers import dependency
if typing.TYPE_CHECKING:
    from gui.battle_control import BattleSessionSetup
    from gui.battle_control.controllers import _ControllersRepository

class LastStandSharedControllersRepository(SharedControllersRepository):

    @classmethod
    def getChatCommandsController(cls, setup, feedback, ammo):
        return LSChatCommandsController(setup, feedback, ammo)


class LastStandControllerRepository(ControllersRepositoryByBonuses):
    __slots__ = ()
    _lsCtrl = dependency.descriptor(ILSController)

    @classmethod
    def create(cls, setup):
        repository = super(LastStandControllerRepository, cls).create(setup)
        repository.addArenaViewController(team_bases_ctrl.createTeamsBasesCtrl(setup), setup)
        repository.addViewController(debug_ctrl.DebugController(), setup)
        repository.addViewController(default_maps_ctrl.DefaultMapsController(setup), setup)
        repository.addArenaViewController(battle_field_ctrl.BattleFieldCtrl(), setup)
        repository.addViewController(perk_ctrl.PerksController(), setup)
        repository.addViewController(battle_hints_ctrl.BattleHintsController(), setup)
        repository.addArenaController(appearance_cache_ctrl.LSAppearanceCacheController(setup), setup)
        repository.addArenaController(battle_gui_controller.LSBattleGUIController(), setup)
        settings = cls._lsCtrl.getModeSettings()
        isTeamChannelAvailable = settings.createVivoxTeamChannels if settings is not None else False
        repository.addArenaController(voip_ctrl.LSVOIPController(isTeamChannelAvailable), setup)
        repository.addController(personal_death_zones_gui_ctrl.PersonalDeathZonesGUIController())
        repository.addController(ShotsResultSoundController())
        return repository
