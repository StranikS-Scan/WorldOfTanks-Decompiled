# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/helpers/ny_helpers.py
from dependency_injection_container import replace_none_kwargs
from gui.impl.lobby.loot_box.loot_box_sounds import PausedSoundManager
from skeletons.gui.shared import IItemsCache
from new_year.helpers.server_settings import getNewYearObjectsConfig
from new_year_common.items.components.ny_constants import TOKEN_VARIADIC_DISCOUNT_PREFIX
from gui.impl.gen import R

def _getVariadicID(vCD):
    return TOKEN_VARIADIC_DISCOUNT_PREFIX + ':' + str(vCD)


@replace_none_kwargs(itemsCache=IItemsCache)
def getCurrentObjectLevel(objectName, itemsCache=None):
    config = getNewYearObjectsConfig()
    currentLevel = itemsCache.items.tokens.getTokenCount(config.getObjectToken(objectName))
    return currentLevel


def showWebmVideoView(videoSource, parent=None, onVideoStarted=None, onVideoStopped=None, onVideoClosed=None, isAutoClose=False, canEscape=True, isUIVisible=False, uiShowDelay=-1):
    from gui.impl.lobby.video.video_view import VideoViewWindow
    window = VideoViewWindow(videoSource=videoSource, parent=parent, onVideoStarted=onVideoStarted, onVideoStopped=onVideoStopped, onVideoClosed=onVideoClosed, isAutoClose=isAutoClose, soundControl=PausedSoundManager(), canEscape=canEscape, isUIVisible=isUIVisible, uiShowDelay=uiShowDelay, viewId=R.views.lobby.video.VideoViewWebm())
    window.load()
    return window
