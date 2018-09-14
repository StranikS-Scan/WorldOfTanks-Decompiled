# Embedded file name: scripts/client/gui/__init__.py
import nations
from collections import defaultdict
from constants import IS_DEVELOPMENT
from gui.GuiSettings import GuiSettings
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION
from helpers.html.templates import XMLCollection
g_guiResetters = set()
g_repeatKeyHandlers = set()
g_keyEventHandlers = set()
g_mouseEventHandlers = set()
g_tankActiveCamouflage = {'historical': {}}
GUI_SETTINGS = GuiSettings()
DEPTH_OF_Disconnect = 0.0
DEPTH_OF_Postmortem = 0.01
DEPTH_OF_BotsMenu = 0.05
DEPTH_OF_PhysicChart = 0.7
DEPTH_OF_Battle = 0.1
DEPTH_OF_Statistic = 0.1
DEPTH_OF_PlayerBonusesPanel = 0.2
DEPTH_OF_Minimap = 0.5
DEPTH_OF_Aim = 0.6
DEPTH_OF_Binoculars = 0.55
DEPTH_OF_GunMarker = 0.56
DEPTH_OF_VehicleMarker = 0.9
CLIENT_ENCODING = '1251'
TANKMEN_ROLES_ORDER_DICT = {'plain': ('commander', 'gunner', 'driver', 'radioman', 'loader'),
 'enum': ('commander', 'gunner1', 'gunner2', 'driver', 'radioman1', 'radioman2', 'loader1', 'loader2')}

def onRepeatKeyEvent(event):
    safeCopy = frozenset(g_repeatKeyHandlers)
    processed = False
    for handler in safeCopy:
        try:
            processed = handler(event)
            if processed:
                break
        except Exception:
            LOG_CURRENT_EXCEPTION()

    safeCopy = None
    return processed


NONE_NATION_NAME = 'none'
ALL_NATION_INDEX = -1
GUI_NATIONS = tuple((n for i, n in enumerate(nations.AVAILABLE_NAMES)))
try:
    new_order_list = [ x for x in GUI_SETTINGS.nations_order if x in nations.AVAILABLE_NAMES ]
    for i, n in enumerate(nations.AVAILABLE_NAMES):
        if n not in new_order_list:
            new_order_list.append(n)

    GUI_NATIONS = tuple(new_order_list)
except AttributeError:
    LOG_ERROR('Could not read nations order from XML. Default order.')

GUI_NATIONS_ORDER_INDEX = dict(((n, i) for i, n in enumerate(GUI_NATIONS)))
GUI_NATIONS_ORDER_INDEX[NONE_NATION_NAME] = nations.NONE_INDEX

def nationCompareByName(first, second):
    if second is None:
        return -1
    elif first is None:
        return 1
    else:
        return GUI_NATIONS_ORDER_INDEX[first] - GUI_NATIONS_ORDER_INDEX[second]


def nationCompareByIndex(first, second):

    def getNationName(idx):
        if idx != nations.NONE_INDEX:
            return nations.NAMES[idx]
        return NONE_NATION_NAME

    return nationCompareByName(getNationName(first), getNationName(second))


def getNationIndex(nationOrderIndex):
    if nationOrderIndex < len(GUI_NATIONS):
        return nations.INDICES.get(GUI_NATIONS[nationOrderIndex])
    else:
        return None


HTML_TEMPLATES_DIR_PATH = 'gui/{0:>s}.xml'
HTML_TEMPLATES_PATH_DELIMITER = ':'

class HtmlTemplatesCache(defaultdict):

    def __missing__(self, key):
        path = key.split(HTML_TEMPLATES_PATH_DELIMITER, 1)
        domain = HTML_TEMPLATES_DIR_PATH.format(path[0])
        ns = path[1] if len(path) > 1 else ''
        value = XMLCollection(domain, ns)
        value.load()
        self[key] = value
        return value


g_htmlTemplates = HtmlTemplatesCache()
if IS_DEVELOPMENT:

    def _reload_ht():
        for collection in g_htmlTemplates.itervalues():
            collection.load(clear=True)


def makeHtmlString(path, key, ctx = None, **kwargs):
    return g_htmlTemplates[path].format(key, ctx=ctx, **kwargs)
