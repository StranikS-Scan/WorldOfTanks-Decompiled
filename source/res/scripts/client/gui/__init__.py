# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/__init__.py
import logging
from collections import defaultdict
import nations
from constants import IS_DEVELOPMENT, HAS_DEV_RESOURCES
from gui import promo
from gui.GuiSettings import GuiSettings as _GuiSettings
from helpers.html.templates import XMLCollection
_logger = logging.getLogger(__name__)
g_guiResetters = set()
g_repeatKeyHandlers = set()
g_keyEventHandlers = set()
g_mouseEventHandlers = set()
g_tankActiveCamouflage = {'historical': {}}
GUI_SETTINGS = _GuiSettings()
DEPTH_OF_BotsMenu = 0.05
DEPTH_OF_Battle = 0.1
DEPTH_OF_Statistic = 0.1
DEPTH_OF_PlayerBonusesPanel = 0.2
DEPTH_OF_Aim = 0.6
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
            _logger.exception('onRepeatKeyEvent is invoked with exception')

    safeCopy = None
    return processed


NONE_NATION_NAME = 'none'
ALL_NATION_INDEX = -1
GUI_NATIONS = tuple(nations.AVAILABLE_NAMES)
try:
    new_order_list = [ x for x in GUI_SETTINGS.nations_order if x in nations.AVAILABLE_NAMES ]
    for i, n in enumerate(nations.AVAILABLE_NAMES):
        if n not in new_order_list:
            new_order_list.append(n)

    GUI_NATIONS = tuple(new_order_list)
except AttributeError:
    _logger.error('Could not read nations order from XML. Default order.')

GUI_NATIONS_ORDER_INDEX = {name:idx for idx, name in enumerate(GUI_NATIONS)}
GUI_NATIONS_ORDER_INDEX[NONE_NATION_NAME] = nations.NONE_INDEX
GUI_NATIONS_ORDER_INDEX_REVERSED = {name:idx for idx, name in enumerate(reversed(GUI_NATIONS))}
GUI_NATIONS_ORDER_INDICES = {nations.INDICES.get(name, nations.NONE_INDEX):idx for name, idx in GUI_NATIONS_ORDER_INDEX.iteritems()}

def nationCompareByName(first, second):
    if second is None:
        return -1
    else:
        return 1 if first is None else GUI_NATIONS_ORDER_INDEX[first] - GUI_NATIONS_ORDER_INDEX[second]


def nationCompareByIndex(first, second):

    def getNationName(idx):
        return nations.NAMES[idx] if idx != nations.NONE_INDEX else NONE_NATION_NAME

    return nationCompareByName(getNationName(first), getNationName(second))


def getNationIndex(nationOrderIndex):
    return nations.INDICES.get(GUI_NATIONS[nationOrderIndex]) if nationOrderIndex < len(GUI_NATIONS) else None


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


def makeHtmlString(path, key, ctx=None, **kwargs):
    return g_htmlTemplates[path].format(key, ctx=ctx, **kwargs)


class GUI_CTRL_MODE_FLAG(object):
    CURSOR_DETACHED = 0
    CURSOR_ATTACHED = 1
    CURSOR_VISIBLE = 2
    MOVING_DISABLED = 4
    AIMING_ENABLED = 8
    GUI_ENABLED = CURSOR_ATTACHED | CURSOR_VISIBLE


def getGuiServicesConfig(manager):
    from gui import app_loader
    from gui import battle_control
    from gui import battle_results
    from gui import wgcg
    from gui import customization
    from gui import event_boards
    from gui import game_control
    from gui import goodies
    from gui import login
    from gui import lobby_context
    from gui import server_events
    from gui import shared
    from gui import sounds
    from gui import Scaleform as _sf
    from gui import hangar_cameras
    from gui import impl
    from skeletons.gui.lobby_context import ILobbyContext
    manager.addConfig(app_loader.getAppLoaderConfig)
    manager.addConfig(shared.getSharedServices)
    manager.addConfig(game_control.getGameControllersConfig)
    manager.addConfig(impl.getGuiImplConfig)
    manager.addConfig(login.getLoginManagerConfig)
    manager.addConfig(server_events.getServerEventsConfig)
    manager.addConfig(_sf.getScaleformConfig)
    manager.addConfig(battle_control.getBattleSessionConfig)
    manager.addConfig(sounds.getSoundsConfig)
    manager.addConfig(wgcg.getWebServicesConfig)
    manager.addConfig(event_boards.getEventServicesConfig)
    manager.addConfig(goodies.getGoodiesCacheConfig)
    manager.addConfig(goodies.getDemountKitNoveltyConfig)
    manager.addConfig(battle_results.getBattleResultsServiceConfig)
    manager.addConfig(customization.getCustomizationServiceConfig)
    manager.addConfig(hangar_cameras.getHangarCamerasConfig)
    manager.addConfig(promo.getPromoConfig)
    manager.addInstance(ILobbyContext, lobby_context.LobbyContext(), finalizer='clear')
    manager.addConfig(server_events.getLinkedSetController)
    manager.addConfig(server_events.getGameEventController)
    if HAS_DEV_RESOURCES:
        try:
            from gui.development import getDevelopmentServicesConfig
        except ImportError:
            _logger.exception('Package development can not be imported')
            return

        getDevelopmentServicesConfig(manager)
