# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/__init__.py
# Compiled at: 2019-03-11 20:15:32
import ResMgr, nations
from debug_utils import LOG_ERROR, LOG_DEBUG
DEPTH_OF_Disconnect = 0.0
DEPTH_OF_Postmortem = 0.01
DEPTH_OF_BotsMenu = 0.05
DEPTH_OF_Battle = 0.1
DEPTH_OF_Statistic = 0.1
DEPTH_OF_GameInfoPanel = 0.2
DEPTH_OF_PlayerBonusesPanel = 0.2
DEPTH_OF_Minimap = 0.5
DEPTH_OF_Aim = 0.6
DEPTH_OF_Binoculars = 0.55
DEPTH_OF_GunMarker = 0.56
DEPTH_OF_VehicleMarker = 0.9
CLIENT_ENCODING = '1251'
EULA_FILE_PATH = 'text/EULA.xml'
VERSION_FILE_PATH = '../version.xml'
TANKMEN_ROLES_ORDER_DICT = {'plain': ('commander', 'gunner', 'driver', 'radioman', 'loader'),
 'enum': ('commander', 'gunner1', 'gunner2', 'driver', 'radioman1', 'radioman2', 'loader1', 'loader2')}
NONE_NATION_NAME = 'none'
GUI_NATIONS = tuple((n for i, n in enumerate(nations.NAMES)))
GUI_CLEAR_LOGIN_VALUE = False
GUI_REMEMBER_PASS_VISIBLE = True
ds = ResMgr.openSection('text/settings.xml')
if ds is not None:
    new_order_list = list()
    for key, value in ds['nations_order'].items():
        try:
            nation = value.readString('')
            if nation not in nations.AVAILABLE_NAMES:
                LOG_ERROR('Unknown nation in nations order: %s', str(value.readString('')))
                continue
            new_order_list.append(nation)
        except:
            pass

    for i, n in enumerate(nations.AVAILABLE_NAMES):
        if n not in new_order_list:
            new_order_list.append(n)

    if new_order_list:
        GUI_NATIONS = tuple(new_order_list)
    GUI_CLEAR_LOGIN_VALUE = ds.readBool('clearLoginValue', GUI_CLEAR_LOGIN_VALUE)
    GUI_REMEMBER_PASS_VISIBLE = ds.readBool('rememberPassVisible', GUI_REMEMBER_PASS_VISIBLE)
else:
    LOG_ERROR('Could not read nations order from XML. Default order.')
GUI_NATIONS_ORDER_INDEX = dict(((n, i) for i, n in enumerate(GUI_NATIONS)))
GUI_NATIONS_ORDER_INDEX[NONE_NATION_NAME] = nations.NONE_INDEX

def nationCompareByName(first, second):
    if GUI_NATIONS_ORDER_INDEX[first] < GUI_NATIONS_ORDER_INDEX[second]:
        return -1
    if GUI_NATIONS_ORDER_INDEX[first] > GUI_NATIONS_ORDER_INDEX[second]:
        return 1


def nationCompareByIndex(first, second):

    def getNationName(idx):
        if idx != nations.NONE_INDEX:
            return nations.NAMES[idx]
        return NONE_NATION_NAME

    return nationCompareByName(getNationName(first), getNationName(second))
