# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/sounds/__init__.py
from __future__ import absolute_import
import SoundGroups

def play2DSound(eventName):
    SoundGroups.g_instance.playSafeSound2D(eventName)


def get2DSound(eventName):
    return SoundGroups.g_instance.getSound2D(eventName)
