# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/veh_post_progression/post_progression_intro.py
import typing
from account_helpers.settings_core.ServerSettingsManager import UI_STORAGE_KEYS
from gui.impl.gen import R
from gui.impl.lobby.common.info_view import getInfoWindowProc
if typing.TYPE_CHECKING:
    from gui.impl.lobby.common.info_view import IInfoWindowProcessor

def getPostProgressionIntroWindowProc():
    return getInfoWindowProc(R.views.lobby.veh_post_progression.PostProgressionIntro(), uiStorageKey=UI_STORAGE_KEYS.POST_PROGRESSION_INTRO_SHOWN)


def getPostProgressionInfoWindowProc():
    return getInfoWindowProc(R.views.lobby.veh_post_progression.PostProgressionInfo())
