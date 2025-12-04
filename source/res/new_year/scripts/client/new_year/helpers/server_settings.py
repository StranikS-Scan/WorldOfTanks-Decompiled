# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/helpers/server_settings.py
from dependency_injection_container import replace_none_kwargs
from new_year_common.craft_cost import CraftCostConfig
from new_year_common.general_config import GeneralConfig
from new_year_common.machine_config import MachineConfig
from new_year_common.objects_config import ObjectsConfig
from new_year_common.setting_bonus import SettingBonusConfig
from new_year_common.toy_decay_cost import ToyDecayCostConfig
from new_year_common.settings import SettingBonusConsts, ToyDecayCostConsts, NYGeneralConsts, CraftCostConsts, MachineConsts, NyObjectsConsts
from skeletons.gui.lobby_context import ILobbyContext

@replace_none_kwargs(lobbyContext=ILobbyContext)
def getNewYearServerSettings(lobbyContext=None):
    return lobbyContext.getServerSettings().getNYConfig()


def __getNYSubConfig(lobbyContext, configName):
    return getNewYearServerSettings(lobbyContext=lobbyContext).get(configName, {})


@replace_none_kwargs(lobbyContext=ILobbyContext)
def getNewYearBonusConfig(lobbyContext=None):
    return SettingBonusConfig(__getNYSubConfig(lobbyContext, SettingBonusConsts.CONFIG_NAME))


@replace_none_kwargs(lobbyContext=ILobbyContext)
def getNewYearToyDecayCostConfig(lobbyContext=None):
    return ToyDecayCostConfig(__getNYSubConfig(lobbyContext, ToyDecayCostConsts.CONFIG_NAME))


@replace_none_kwargs(lobbyContext=ILobbyContext)
def getNewYearCraftCostConfig(lobbyContext=None):
    return CraftCostConfig(__getNYSubConfig(lobbyContext, CraftCostConsts.CONFIG_NAME))


@replace_none_kwargs(lobbyContext=ILobbyContext)
def getNewYearGeneralConfig(lobbyContext=None):
    return GeneralConfig(__getNYSubConfig(lobbyContext, NYGeneralConsts.CONFIG_NAME))


@replace_none_kwargs(lobbyContext=ILobbyContext)
def getNewYearMachineConfig(lobbyContext=None):
    return MachineConfig(__getNYSubConfig(lobbyContext, MachineConsts.CONFIG_NAME))


@replace_none_kwargs(lobbyContext=ILobbyContext)
def getNewYearObjectsConfig(lobbyContext=None):
    return ObjectsConfig(__getNYSubConfig(lobbyContext, NyObjectsConsts.CONFIG_NAME))
