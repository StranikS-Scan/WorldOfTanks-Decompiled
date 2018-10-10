# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/game.py
import cPickle
import zlib
import sys
import asyncore
import functools
import locale
import services_config
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_DEBUG, LOG_ERROR, LOG_NOTE
import AreaDestructibles
import BigWorld
import constants
import CommandMapping
from helpers import dependency, log
import GUI
from gui import CLIENT_ENCODING, onRepeatKeyEvent, g_keyEventHandlers, g_mouseEventHandlers, InputHandler, GUI_SETTINGS
from gui.Scaleform.game_loading import GameLoading
from gui.shared import personality as gui_personality
from messenger import MessengerEntry
import MusicControllerWWISE
import TriggersManager
from helpers import RSSDownloader, OfflineMode, LightingGenerationMode
import Settings
from MemoryCriticalController import g_critMemHandler
import VOIP
import WebBrowser
import SoundGroups
from skeletons.connection_mgr import IConnectionManager
from bootcamp.Bootcamp import g_bootcamp
from skeletons.gameplay import IGameplayLogic
tutorialLoaderInit = lambda : None
tutorialLoaderFini = lambda : None
if constants.IS_TUTORIAL_ENABLED:
    if GUI_SETTINGS.isGuiEnabled():
        try:
            from tutorial.loader import init as tutorialLoaderInit
            from tutorial.loader import fini as tutorialLoaderFini
        except ImportError:
            LOG_ERROR('Module tutorial not found')

loadingScreenClass = GameLoading
__import__('__main__').GameLoading = loadingScreenClass
try:
    locale.setlocale(locale.LC_TIME, '')
except locale.Error:
    LOG_CURRENT_EXCEPTION()

class ServiceLocator(object):
    connectionMgr = dependency.descriptor(IConnectionManager)
    gameplay = dependency.descriptor(IGameplayLogic)


g_replayCtrl = None
g_onBeforeSendEvent = None

def autoFlushPythonLog():
    BigWorld.flushPythonLog()
    BigWorld.callback(5.0, autoFlushPythonLog)


def init(scriptConfig, engineConfig, userPreferences, loadingScreenGUI=None):
    global g_replayCtrl
    global g_onBeforeSendEvent
    try:
        log.config.setupFromXML()
        if constants.IS_DEVELOPMENT:
            autoFlushPythonLog()
            from development_features import initDevBonusTypes
            initDevBonusTypes()
        import Event
        g_onBeforeSendEvent = Event.Event()
        BigWorld.wg_initCustomSettings()
        Settings.g_instance = Settings.Settings(scriptConfig, engineConfig, userPreferences)
        CommandMapping.g_instance = CommandMapping.CommandMapping()
        from helpers import DecalMap
        DecalMap.g_instance = DecalMap.DecalMap(scriptConfig['decal'])
        from helpers import EdgeDetectColorController
        EdgeDetectColorController.g_instance = EdgeDetectColorController.EdgeDetectColorController(scriptConfig['silhouetteColors'])
        SoundGroups.g_instance = SoundGroups.SoundGroups()
        import BattleReplay
        g_replayCtrl = BattleReplay.g_replayCtrl = BattleReplay.BattleReplay()
        g_replayCtrl.registerWotReplayFileExtension()
        g_bootcamp.replayCallbackSubscribe()
        try:
            from Vibroeffects import VibroManager
            VibroManager.g_instance = VibroManager.VibroManager()
            VibroManager.g_instance.connect()
        except Exception:
            LOG_CURRENT_EXCEPTION()

        tutorialLoaderInit()
        BigWorld.callback(0.1, asyncore_call)
        import items
        items.init(True, None if not constants.IS_DEVELOPMENT else {})
        import win_points
        win_points.init()
        import rage
        rage.init()
        import ArenaType
        ArenaType.init()
        import dossiers2
        dossiers2.init()
        import personal_missions
        personal_missions.init()
        import motivation_quests
        motivation_quests.init()
        BigWorld.worldDrawEnabled(False)
        dependency.configure(services_config.getClientServicesConfig)
        gui_personality.init(loadingScreenGUI=loadingScreenGUI)
        EdgeDetectColorController.g_instance.create()
        g_replayCtrl.subscribe()
        MessengerEntry.g_instance.init()
        AreaDestructibles.init()
        MusicControllerWWISE.create()
        TriggersManager.init()
        RSSDownloader.init()
        items.clearXMLCache()
        SoundGroups.loadLightSoundsDB()
        import player_ranks
        player_ranks.init()
        import destructible_entities
        destructible_entities.init()
        try:
            from LightFx import LightManager
            LightManager.g_instance = LightManager.LightManager()
            import AuxiliaryFx
            AuxiliaryFx.g_instance = AuxiliaryFx.AuxiliaryFxManager()
        except Exception:
            LOG_CURRENT_EXCEPTION()

        from AvatarInputHandler.cameras import FovExtended
        FovExtended.instance().resetFov()
        BigWorld.pauseDRRAutoscaling(True)
    except Exception:
        LOG_CURRENT_EXCEPTION()
        BigWorld.quit()

    return


def start():
    LOG_DEBUG('start')
    if OfflineMode.onStartup():
        LOG_DEBUG('OfflineMode')
        return
    elif LightingGenerationMode.onStartup():
        LOG_DEBUG('LightingGenerationMode')
        return
    else:
        ServiceLocator.connectionMgr.onConnected += onConnected
        ServiceLocator.connectionMgr.onDisconnected += onDisconnected
        if len(sys.argv) > 2:
            if sys.argv[1] == 'scriptedTest':
                try:
                    scriptName = sys.argv[2]
                    if scriptName[-3:] == '.py':
                        scriptName = scriptName[:-3]
                    try:
                        __import__(scriptName)
                    except ImportError:
                        try:
                            __import__('tests.' + scriptName)
                        except ImportError:
                            __import__('Cat.' + scriptName)

                    ServiceLocator.gameplay.start()
                except Exception:
                    LOG_CURRENT_EXCEPTION()
                    BigWorld.wg_writeToStdOut('Failed to run scripted test, Python exception was thrown, see python.log')
                    BigWorld.quit()

            elif sys.argv[1] == 'offlineTest':
                try:
                    from Cat.Tasks.TestArena2 import TestArena2Object
                    LOG_DEBUG(sys.argv)
                    LOG_DEBUG('starting offline test: %s', sys.argv[2])
                    if len(sys.argv) > 3:
                        TestArena2Object.startOffline(sys.argv[2], sys.argv[3])
                    else:
                        TestArena2Object.startOffline(sys.argv[2])
                except Exception:
                    LOG_DEBUG('Game start FAILED with:')
                    LOG_CURRENT_EXCEPTION()

            elif sys.argv[1] == 'spinTest':
                try:
                    from Cat.Tasks.TestArena2 import TestArena2Object
                    LOG_DEBUG(sys.argv)
                    targetDirectory = sys.argv[4] if len(sys.argv) > 4 else 'SpinTestResult'
                    LOG_DEBUG('starting offline test: %s %s %s', sys.argv[2], sys.argv[3], targetDirectory)
                    TestArena2Object.startOffline(sys.argv[2], mapName=sys.argv[3], targetDirectory=targetDirectory)
                except Exception:
                    LOG_DEBUG('Game start FAILED with:')
                    LOG_CURRENT_EXCEPTION()

            elif sys.argv[1] == 'hangarOverride':
                try:
                    LOG_DEBUG(sys.argv)
                    from Tests.auto.HangarOverride import HangarOverride
                    HangarOverride.setHangar('spaces/' + sys.argv[2])
                    if len(sys.argv) > 3 and sys.argv[3] is not None:
                        LOG_DEBUG('Setting default client inactivity timeout: %s' % sys.argv[3])
                        constants.CLIENT_INACTIVITY_TIMEOUT = int(sys.argv[3])
                except Exception:
                    LOG_DEBUG('Game start FAILED with:')
                    LOG_CURRENT_EXCEPTION()

                ServiceLocator.gameplay.start()
                gui_personality.start()
            elif sys.argv[1] == 'replayTimeout':
                try:
                    g_replayCtrl.replayTimeout = float(sys.argv[2])
                except Exception:
                    LOG_DEBUG('Game start FAILED with:')
                    LOG_CURRENT_EXCEPTION()

                ServiceLocator.gameplay.start()
                gui_personality.start()
            elif sys.argv[1] == 'botInit' or sys.argv[1] == 'botExecute':
                ServiceLocator.gameplay.start()
                gui_personality.start()
                try:
                    LOG_DEBUG('BOTNET: Playing scenario "%s" with bot "%s"...' % (sys.argv[2], sys.argv[3]))
                    if sys.argv[1] == 'botInit':
                        scenarioPlayer().initBot(sys.argv[3], sys.argv[2])
                    elif sys.argv[1] == 'botExecute':
                        scenarioPlayer().execute(sys.argv[3], sys.argv[2])
                except Exception:
                    LOG_DEBUG('BOTNET: Failed to start the client with:')
                    LOG_CURRENT_EXCEPTION()

            else:
                ServiceLocator.gameplay.start()
                gui_personality.start()
        else:
            ServiceLocator.gameplay.start()
            gui_personality.start()
        try:
            import Vibroeffects
            Vibroeffects.VibroManager.g_instance.start()
        except Exception:
            LOG_CURRENT_EXCEPTION()

        try:
            from LightFx import LightManager
            if LightManager.g_instance is not None:
                LightManager.g_instance.start()
            from AuxiliaryFx import g_instance
            if g_instance is not None:
                g_instance.start()
        except Exception:
            LOG_CURRENT_EXCEPTION()

        WebBrowser.initExternalCache()
        return


def abort():
    BigWorld.callback(0.0, fini)


def fini():
    global g_replayCtrl
    global g_onBeforeSendEvent
    global g_scenario
    LOG_DEBUG('fini')
    if OfflineMode.enabled():
        return
    elif LightingGenerationMode.enabled():
        return
    else:
        BigWorld.wg_setScreenshotNotifyCallback(None)
        g_critMemHandler.restore()
        g_critMemHandler.destroy()
        if constants.IS_CAT_LOADED:
            import Cat
            Cat.fini()
        MusicControllerWWISE.destroy()
        if RSSDownloader.g_downloader is not None:
            RSSDownloader.g_downloader.destroy()
        ServiceLocator.connectionMgr.onConnected -= onConnected
        ServiceLocator.connectionMgr.onDisconnected -= onDisconnected
        MessengerEntry.g_instance.fini()
        from helpers import EdgeDetectColorController
        if EdgeDetectColorController.g_instance is not None:
            EdgeDetectColorController.g_instance.destroy()
            EdgeDetectColorController.g_instance = None
        BigWorld.resetEntityManager(False, False)
        BigWorld.clearAllSpaces()
        if TriggersManager.g_manager is not None:
            TriggersManager.g_manager.destroy()
            TriggersManager.g_manager = None
        if g_replayCtrl is not None:
            g_replayCtrl.unsubscribe()
        gui_personality.fini()
        tutorialLoaderFini()
        import Vibroeffects
        if Vibroeffects.VibroManager.g_instance is not None:
            Vibroeffects.VibroManager.g_instance.destroy()
            Vibroeffects.VibroManager.g_instance = None
        from LightFx import LightManager
        if LightManager.g_instance is not None:
            LightManager.g_instance.destroy()
            LightManager.g_instance = None
        import AuxiliaryFx
        if AuxiliaryFx.g_instance is not None:
            AuxiliaryFx.g_instance.destroy()
            AuxiliaryFx.g_instance = None
        from predefined_hosts import g_preDefinedHosts
        if g_preDefinedHosts is not None:
            g_preDefinedHosts.fini()
        dependency.clear()
        if g_replayCtrl is not None:
            g_replayCtrl.destroy()
            g_replayCtrl = None
        voipRespHandler = VOIP.getVOIPManager()
        if voipRespHandler is not None:
            voipRespHandler.destroy()
        SoundGroups.g_instance.destroy()
        Settings.g_instance.save()
        if g_scenario is not None:
            g_scenario.fini()
        g_onBeforeSendEvent = None
        WebBrowser.destroyExternalCache()
        return


def onChangeEnvironments(inside):
    pass


def onBeforeSend():
    if g_onBeforeSendEvent is not None:
        g_onBeforeSendEvent()
    return


def onRecreateDevice():
    gui_personality.onRecreateDevice()


def onStreamComplete(streamID, desc, data):
    try:
        origPacketLen, origCrc32 = cPickle.loads(desc)
    except Exception:
        origPacketLen, origCrc32 = (-1, -1)

    packetLen = len(data)
    crc32 = zlib.crc32(data)
    isCorrupted = origPacketLen != packetLen or origCrc32 != crc32
    desc = (isCorrupted,
     origPacketLen,
     packetLen,
     origCrc32,
     crc32)
    player = BigWorld.player()
    if player is None:
        LOG_ERROR('onStreamComplete: no player entity available for process stream (%d, %s) data' % (streamID, desc))
    else:
        player.onStreamComplete(streamID, desc, data)
    return


def onConnected():
    gui_personality.onConnected()
    VOIP.getVOIPManager().onConnected()


def onGeometryMapped(spaceID, path):
    SoundGroups.g_instance.unloadAll()
    LOG_NOTE('[SPACE] Loading space: ' + path)
    arenaName = path.split('/')[-1]
    SoundGroups.g_instance.preloadSoundGroups(arenaName)


def onDisconnected():
    gui_personality.onDisconnected()
    VOIP.getVOIPManager().logout()
    VOIP.getVOIPManager().onDisconnected()


def onCameraChange(oldCamera):
    pass


def handleCharEvent(char, key, mods):
    char = unicode(char.encode('iso8859'), CLIENT_ENCODING)
    return True if GUI.handleCharEvent(char, key, mods) else False


def handleAxisEvent(event):
    return False


def handleKeyEvent(event):
    if OfflineMode.handleKeyEvent(event):
        return True
    elif LightingGenerationMode.handleKeyEvent(event):
        return True
    else:
        isDown, key, mods, isRepeat = convertKeyEvent(event)
        if g_bootcamp.isRunning():
            g_bootcamp.handleKeyEvent(event)
        if WebBrowser.g_mgr.handleKeyEvent(event):
            return True
        if g_replayCtrl.isPlaying:
            if g_replayCtrl.handleKeyEvent(isDown, key, mods, isRepeat, event):
                return True
        if isRepeat:
            if onRepeatKeyEvent(event):
                return True
        if constants.IS_CAT_LOADED:
            import Cat
            if Cat.handleKeyEventBeforeGUI(isDown, key, mods, event):
                return True
        if not isRepeat:
            InputHandler.g_instance.handleKeyEvent(event)
            if GUI.handleKeyEvent(event):
                return True
        if constants.IS_CAT_LOADED:
            import Cat
            if Cat.handleKeyEventAfterGUI(isDown, key, mods, event):
                return True
        if not isRepeat:
            if MessengerEntry.g_instance.gui.handleKey(event):
                return True
        inputHandler = getattr(BigWorld.player(), 'inputHandler', None)
        if inputHandler is not None:
            if inputHandler.handleKeyEvent(event):
                return True
        for handler in g_keyEventHandlers:
            try:
                if handler(event):
                    return True
            except Exception:
                LOG_CURRENT_EXCEPTION()

        return False


def handleMouseEvent(event):
    if OfflineMode.handleMouseEvent(event):
        return True
    elif LightingGenerationMode.handleMouseEvent(event):
        return True
    else:
        dx, dy, dz, _ = convertMouseEvent(event)
        if constants.IS_CAT_LOADED:
            import Cat
            if Cat.handleMouseEvent(dx, dy, dz):
                return True
        if g_replayCtrl.isPlaying:
            if g_replayCtrl.handleMouseEvent(dx, dy, dz):
                return True
        if GUI.handleMouseEvent(event):
            return True
        inputHandler = getattr(BigWorld.player(), 'inputHandler', None)
        if inputHandler is not None:
            if inputHandler.handleMouseEvent(dx, dy, dz):
                return True
        for handler in g_mouseEventHandlers:
            try:
                if handler(event):
                    return True
            except Exception:
                LOG_CURRENT_EXCEPTION()

        return False


def handleInputLangChangeEvent():
    return False


def addChatMsg(*msg):
    print 'Message:', msg


_PYTHON_MACROS = {'p': 'BigWorld.player()',
 't': 'BigWorld.target()',
 'B': 'BigWorld',
 'v': 'BigWorld.entities[BigWorld.player().playerVehicleID]',
 'b': 'BigWorld.player().addBotToArena',
 'w': 'import Weather; Weather.weather().summon',
 'cam_pos': 'BigWorld.player().inputHandler._AvatarInputHandler__curCtrl.setCameraPosition',
 'gc': 'import gc; gc.set_debug(gc.DEBUG_LEAK | gc.DEBUG_STATS);gc.collect(2)',
 'gcd': 'import gc; gc.set_debug(gc.DEBUG_LEAK | gc.DEBUG_STATS);from debug_utils import dump_garbage; dump_garbage()',
 'gcd2': 'from debug_utils import dump_garbage_2; dump_garbage_2',
 'connect': 'ls=game.LanServers();ls.searchAndConnect',
 'create': 'BigWorld.player().createArena',
 'list': 'alr = game.ArenaListRequester',
 'start': 'BigWorld.player().startArena',
 'join': 'BigWorld.player().joinArena',
 'leave': 'BigWorld.player().leaveArena',
 'cv': 'import vehicles_check;vehicles_check.check',
 'cls': "print '\\n' * 100",
 'unlockAll': 'BigWorld.player().stats.unlockAll(lambda *args:None)',
 'hangar': 'from gui.ClientHangarSpace import g_clientHangarSpaceOverride; g_clientHangarSpaceOverride',
 'cvi': 'from CurrentVehicle import g_currentVehicle; cvi = g_currentVehicle.item; cvi',
 'wc': 'from gui.Scaleform.Waiting import Waiting; Waiting.close()',
 'clan': 'from gui.shared.ClanCache import g_clanCache; clan = g_clanCache',
 'camera': 'BigWorld.player().inputHandler.ctrl',
 'rankedCtrl': 'from helpers import dependency; from skeletons.gui.game_control import IRankedBattlesController;rc = dependency.instance(IRankedBattlesController)',
 'eventsCache': 'from helpers import dependency; from skeletons.gui.server_events import IEventsCache;ec = dependency.instance(IEventsCache)',
 'items': 'from helpers import dependency; from skeletons.gui.shared import IItemsCache;items = dependency.instance(IItemsCache).items'}

def expandMacros(line):
    import re
    patt = '\\$(' + functools.reduce(lambda x, y: x + '|' + y, _PYTHON_MACROS.iterkeys()) + ')(\\W|\\Z)'

    def repl(match):
        return _PYTHON_MACROS[match.group(1)] + match.group(2)

    return re.sub(patt, repl, line)


def wg_onChunkLoad(spaceID, chunkID, numDestructibles, isOutside):
    if not isOutside:
        return
    if spaceID != AreaDestructibles.g_destructiblesManager.getSpaceID():
        AreaDestructibles.g_destructiblesManager.startSpace(spaceID)
    AreaDestructibles.g_destructiblesManager.onChunkLoad(chunkID, numDestructibles)


def wg_onChunkLoose(spaceID, chunkID, isOutside):
    if not isOutside:
        return
    if spaceID == AreaDestructibles.g_destructiblesManager.getSpaceID():
        AreaDestructibles.g_destructiblesManager.onChunkLoose(chunkID)


def wg_playModuleDestructionAnimation(chunkID, destrIndex, moduleIndex, isShotDamage, isHavokSpawnedDestructibles):
    AreaDestructibles.g_destructiblesManager.onPlayModuleDestructionAnimation(chunkID, destrIndex, moduleIndex, isShotDamage, isHavokSpawnedDestructibles)


def convertKeyEvent(event):
    isDown = event.isKeyDown()
    key = event.key
    isRepeat = event.isRepeatedEvent()
    mods = 1 if event.isShiftDown() else (2 if event.isCtrlDown() else (4 if event.isAltDown() else 0))
    return (isDown,
     key,
     mods,
     isRepeat)


def convertMouseEvent(event):
    return (event.dx,
     event.dy,
     event.dz,
     event.cursorPosition)


def onMemoryCritical():
    g_critMemHandler()


def asyncore_call():
    try:
        asyncore.loop(count=1)
    except Exception:
        LOG_CURRENT_EXCEPTION()

    BigWorld.callback(0.1, asyncore_call)


g_scenario = None

def scenarioPlayer():
    global g_scenario
    if g_scenario is None:
        sys.path.append('scripts/bot')
        from client.ScenarioPlayer import g_scenarioPlayer
        g_scenario = g_scenarioPlayer
    return g_scenario
