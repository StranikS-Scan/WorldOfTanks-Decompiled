# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: event_platform/scripts/client/EventPlatformPersonality.py
from __future__ import absolute_import
from debug_utils import LOG_DEBUG
from constants_utils import addArenaBonusCapsFromExtension
from event_platform_common.event_platform_constants import ARENA_BONUS_TYPE_CAPS

def preInit():
    addArenaBonusCapsFromExtension(ARENA_BONUS_TYPE_CAPS, __name__)


def init():
    LOG_DEBUG('init', __name__)


def start():
    pass


def fini():
    pass
