# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: server_side_replay/scripts/client/ServerSideReplayPersonality.py
from debug_utils import LOG_DEBUG
from server_side_replay.gui.Scaleform import registerLobbyHeaderTabs

def preInit():
    registerLobbyHeaderTabs()


def init():
    LOG_DEBUG('init', __name__)


def start():
    pass


def fini():
    pass
