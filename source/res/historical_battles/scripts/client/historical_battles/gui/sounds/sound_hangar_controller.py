# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/sounds/sound_hangar_controller.py
import SoundGroups
import WWISE
from historical_battles.gui.sounds.sound_constants import HangarViewState, HBHangarEvent

class SoundHangarController(object):

    @staticmethod
    def onEnterEvent():
        SoundHangarController.__playEvent(HBHangarEvent.ENTER)

    @staticmethod
    def onEnterHangar():
        SoundHangarController.__onHangarViewChanged(HangarViewState.HANGAR)

    @staticmethod
    def onExitHangar():
        SoundHangarController.__playEvent(HBHangarEvent.EXIT)

    @staticmethod
    def onEnterProgressionView():
        SoundHangarController.__onHangarViewChanged(HangarViewState.PROGRESSION)

    @staticmethod
    def onEnterDivisionView():
        SoundHangarController.__onHangarViewChanged(HangarViewState.DIVISIONS)

    @staticmethod
    def onEnterOrdersView():
        SoundHangarController.__onHangarViewChanged(HangarViewState.ORDERS)

    @staticmethod
    def __onHangarViewChanged(state):
        WWISE.WW_setState(HangarViewState.GROUP, state)

    @staticmethod
    def __playEvent(event):
        SoundGroups.g_instance.playSound2D(event)
