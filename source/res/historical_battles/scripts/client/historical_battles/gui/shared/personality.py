# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/shared/personality.py
import logging
from PlayerEvents import g_playerEvents
from helpers import dependency
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from skeletons.account_helpers.settings_core import ISettingsCache
from skeletons.gui.game_control import IBootcampController
from historical_battles.skeletons.gui.sound_controller import IHBSoundController
_logger = logging.getLogger(__name__)

class ServicesLocator(object):
    settingsCache = dependency.descriptor(ISettingsCache)
    gameEventController = dependency.descriptor(IGameEventController)
    bootcampController = dependency.descriptor(IBootcampController)
    soundController = dependency.descriptor(IHBSoundController)

    @classmethod
    def clear(cls):
        cls.gameEventController.clear()

    @classmethod
    def onDisconnected(cls):
        cls.clear()


def onAccountShowGUI(ctx):
    if not ServicesLocator.bootcampController.isInBootcamp():
        ServicesLocator.gameEventController.start()
        ServicesLocator.soundController.start()


def onAccountBecomeNonPlayer():
    if not ServicesLocator.bootcampController.isInBootcamp():
        ServicesLocator.gameEventController.stop()


def onAvatarBecomePlayer():
    if not ServicesLocator.bootcampController.isInBootcamp():
        ServicesLocator.gameEventController.stop()
    ServicesLocator.soundController.activateBattleSoundRemapping()


def onAvatarBecomeNonPlayer():
    ServicesLocator.soundController.deactivateBattleSoundRemapping()


def init():
    g_playerEvents.onAccountBecomeNonPlayer += onAccountBecomeNonPlayer
    g_playerEvents.onAvatarBecomePlayer += onAvatarBecomePlayer
    g_playerEvents.onAvatarBecomeNonPlayer += onAvatarBecomeNonPlayer
    g_playerEvents.onAccountShowGUI += onAccountShowGUI


def fini():
    g_playerEvents.onAccountBecomeNonPlayer -= onAccountBecomeNonPlayer
    g_playerEvents.onAvatarBecomePlayer -= onAvatarBecomePlayer
    g_playerEvents.onAvatarBecomeNonPlayer -= onAvatarBecomeNonPlayer
    g_playerEvents.onAccountShowGUI -= onAccountShowGUI
