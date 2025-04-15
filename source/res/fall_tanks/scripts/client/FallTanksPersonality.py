# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/FallTanksPersonality.py
from gui.battle_results.reusable import ReusableInfoFactory
from gui.prb_control.prb_utils import initScaleformGuiTypes, initBattleCtrlIDs
from fall_tanks_common.fall_tanks_battle_mode import FallTanksBattleMode
from fall_tanks_constants import injectConsts
from fall_tanks.gui.battle_control import registerFallTanksBattle
from fall_tanks.gui import fall_tanks_gui_constants
from fall_tanks.gui.battle_results import registerFallTanksBattleResults
from fall_tanks.gui.fall_tanks_account_settings import addFallTanksAccountSettings
from fall_tanks.gui.fall_tanks_gui_constants import FALL_TANKS_EQUIPMENTS
from fall_tanks.gui.fun_random.sub_modes import registerFallTanksSubModes
from fall_tanks.gui.hangar_presets import registerHangarPresetConfig
from fall_tanks.gui.impl.lobby.fall_tanks_ammunition_panel import FallTanksAmmunitionPanelView
from fall_tanks.gui.impl.lobby.fall_tanks_ammunition_setup import FallTanksAmmunitionSetupView
from fall_tanks.gui.Scaleform import registerFallTanksScaleform
from fall_tanks.messenger.formatters import registerFallTanksFormatters

class ClientFallTanksBattleMode(FallTanksBattleMode):
    _CLIENT_BATTLE_PAGE = fall_tanks_gui_constants.VIEW_ALIAS.FALL_TANKS_BATTLE_PAGE

    @property
    def _client_ammunitionPanelViews(self):
        return [FallTanksAmmunitionPanelView]

    @property
    def _client_ammunitionSetupViews(self):
        return [FallTanksAmmunitionSetupView]

    @property
    def _client_arenaDescrClass(self):
        from fall_tanks.gui.battle_control.arena_info.arena_descrs import FallTanksArenaDescription
        return FallTanksArenaDescription

    @property
    def _client_arenaInfoKeys(self):
        from fall_tanks.gui.battle_control.arena_info.arena_vos import FallTanksKeys
        return FallTanksKeys

    @property
    def _client_attackReasonToCode(self):
        from fall_tanks_constants import ATTACK_REASON
        return {ATTACK_REASON.getIndex(ATTACK_REASON.FALL_TANKS_FINISH): 'DEATH_FROM_FALL_TANKS_FINISH',
         ATTACK_REASON.getIndex(ATTACK_REASON.FALL_TANKS_FALLING): 'DEATH_FROM_FALL_TANKS_FALLING',
         ATTACK_REASON.getIndex(ATTACK_REASON.FALL_TANKS_LEAVER): 'DEATH_FROM_FALL_TANKS_LEAVER'}

    @property
    def _client_battleControllersRepository(self):
        from fall_tanks.gui.battle_control.repository import FallTanksControllersRepository
        return FallTanksControllersRepository

    @property
    def _client_battleRequiredLibraries(self):
        return ['fall_tanks|fall_tanks_battle.swf']

    @property
    def _client_battleResultsReusables(self):
        from fall_tanks.gui.battle_results.reusable.fall_tanks_shared import FallTanksVehicleDetailedInfo, FallTanksVehicleSummarizeInfo
        return {ReusableInfoFactory.Keys.VEHICLE_DETAILED: FallTanksVehicleDetailedInfo,
         ReusableInfoFactory.Keys.VEHICLE_SUMMARIZED: FallTanksVehicleSummarizeInfo}

    @property
    def _client_controlModes(self):
        from fall_tanks.AvatarInpitHandler import FALL_TANKS_CTRLS_DESC_MAP
        return FALL_TANKS_CTRLS_DESC_MAP

    @property
    def _client_equipmentItems(self):
        from fall_tanks.gui.battle_control.controllers.equipment_items import FallTanksEquipmentItem, FallTanksReplyEquipmentItem
        return ((name, FallTanksEquipmentItem, FallTanksReplyEquipmentItem) for name in FALL_TANKS_EQUIPMENTS)

    @property
    def _client_sharedControllersRepository(self):
        from fall_tanks.gui.battle_control.repository import FallTanksSharedControllersRepository
        return FallTanksSharedControllersRepository


def preInit():
    injectConsts(__name__)
    initBattleCtrlIDs(fall_tanks_gui_constants, __name__)
    initScaleformGuiTypes(fall_tanks_gui_constants, __name__)
    battleMode = ClientFallTanksBattleMode(__name__)
    battleMode.registerGuiType()
    battleMode.registerControlModes()
    battleMode.registerClientArenaInfoKeys()
    battleMode.registerSharedControllersRepository()
    battleMode.registerBattleControllersRepository()
    battleMode.registerScaleformRequiredLibraries()
    battleMode.registerClientBattleResultReusabled()
    battleMode.registerClientEquipmentItems()
    battleMode.registerAmmunitionPanelViews()
    battleMode.registerAmmunitionSetupViews()
    battleMode.registerAttackReasonToCode()
    registerHangarPresetConfig()
    registerFallTanksScaleform()
    registerFallTanksFormatters()
    registerFallTanksSubModes()
    registerFallTanksBattle(__name__)
    registerFallTanksBattleResults()


def init():
    addFallTanksAccountSettings()


def start():
    pass


def fini():
    pass
