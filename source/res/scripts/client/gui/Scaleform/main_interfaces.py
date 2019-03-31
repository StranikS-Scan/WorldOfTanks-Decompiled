# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/main_interfaces.py
# Compiled at: 2018-12-11 23:56:21
import constants
from debug_utils import LOG_ERROR
from gui.Scaleform.Barracks import Barracks
from gui.Scaleform.BattleLoading import BattleLoading
from gui.Scaleform.ConstructionDepartment import ConstructionDepartment
from gui.Scaleform.Inventory import Inventory
from gui.Scaleform.Hangar import Hangar
from gui.Scaleform.Login import Login
from gui.Scaleform.Prebattle import Prebattle
from gui.Scaleform.Profile import Profile
from gui.Scaleform.Shop import Shop
from gui.Scaleform.StartGameVideo import StartGameVideo
from gui.Scaleform.Training import Training
from gui.Scaleform.VehicleCustomization import VehicleCustomization
import exceptions
idict = {'login': Login,
 'hangar': Hangar,
 'inventory': Inventory,
 'shop': Shop,
 'profile': Profile,
 'prebattle': Prebattle,
 'construction_department': ConstructionDepartment,
 'battleloading': BattleLoading,
 'training': Training,
 'startgamevideo': StartGameVideo,
 'barracks': Barracks,
 'customization': VehicleCustomization}
if constants.HAS_DEV_RESOURCES:
    try:
        from gui.Scaleform.development.ManagementBattles import ManagementBattles
        idict.update({'development/management_battles': ManagementBattles})
    except exceptions.ImportError:
        LOG_ERROR('Package gui.Scaleform.development not found.')
