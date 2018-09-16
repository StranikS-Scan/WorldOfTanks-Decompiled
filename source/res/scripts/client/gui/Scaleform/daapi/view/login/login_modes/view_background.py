# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/login/login_modes/view_background.py
import random
import WWISE
import Windowing
import ResMgr
import ScaleformFileLoader
import Settings
from gui.Scaleform import SCALEFORM_SWF_PATH_V3, SCALEFORM_STARTUP_VIDEO_MASK, SCALEFORM_WALLPAPER_PATH
_BG_MODE_VIDEO, _BG_MODE_WALLPAPER = range(0, 2)
_LOGIN_VIDEO_FILE = SCALEFORM_STARTUP_VIDEO_MASK % '_login.usm'

class ViewBackground(object):

    def __init__(self, view):
        self.__isSoundMuted = False
        self.__bgMode = _BG_MODE_VIDEO
        self.__userPrefs = Settings.g_instance.userPrefs
        self.__view = view
        self.__lastImage = ''
        self.__show = True
        self.__switchButton = True
        self.__bufferTime = self.__userPrefs.readFloat(Settings.VIDEO_BUFFERING_TIME, 0.5)
        self.__images = self.__getWallpapersList()
        self.__isWindowAccessible = True
        self.__inSwitchToMode = None
        self.__delayedVideoStart = False
        return

    def showWallpaper(self, showSwitchButton):
        self.__view.as_showWallpaperS(self.__show, self.__randomImage(), showSwitchButton, self.__isSoundMuted)
        WWISE.WW_eventGlobal('loginscreen_ambient_start')
        if self.__isSoundMuted:
            WWISE.WW_eventGlobal('loginscreen_mute')

    def show(self):
        files = ['/'.join((SCALEFORM_SWF_PATH_V3, _LOGIN_VIDEO_FILE))]
        ScaleformFileLoader.enableStreaming(files)
        self.__isWindowAccessible = Windowing.isWindowAccessible()
        if not self.__isWindowAccessible:
            self.__delayedVideoStart = True
        else:
            self.__startBGMode()
        Windowing.addWindowAccessibilitynHandler(self.__onWindowAccessibilityChanged)

    def hide(self):
        ScaleformFileLoader.disableStreaming()
        self.__saveToPrefs()
        Windowing.removeWindowAccessibilityHandler(self.__onWindowAccessibilityChanged)

    def toggleMute(self, value):
        self.__isSoundMuted = value
        WWISE.WW_eventGlobal(('loginscreen_unmute', 'loginscreen_mute')[self.__isSoundMuted])

    def fadeSound(self):
        WWISE.WW_eventGlobal(('loginscreen_music_pause', 'loginscreen_ambient_stop')[self.__bgMode])
        self.__inSwitchToMode = _BG_MODE_VIDEO if self.__bgMode != _BG_MODE_VIDEO else _BG_MODE_WALLPAPER

    def switch(self):
        if self.__bgMode != _BG_MODE_VIDEO:
            self.__bgMode = _BG_MODE_VIDEO
            self.__view.as_showLoginVideoS(_LOGIN_VIDEO_FILE, self.__bufferTime, self.__isSoundMuted)
        else:
            self.__bgMode = _BG_MODE_WALLPAPER
            self.__view.as_showWallpaperS(self.__show, self.__randomImage(), self.__switchButton, self.__isSoundMuted)
        self.__inSwitchToMode = None
        WWISE.WW_eventGlobal(('loginscreen_music_resume', 'loginscreen_ambient_start')[self.__bgMode])
        if self.__isSoundMuted:
            WWISE.WW_eventGlobal('loginscreen_mute')
        self.__applyWindowAccessibility()
        return

    def startVideoSound(self):
        WWISE.WW_eventGlobal('loginscreen_music_start')
        if self.__isSoundMuted:
            WWISE.WW_eventGlobal('loginscreen_mute')
        self.__applyWindowAccessibility()

    def __onWindowAccessibilityChanged(self, isAccessible):
        if self.__isWindowAccessible == isAccessible:
            return
        self.__isWindowAccessible = isAccessible
        if isAccessible and self.__delayedVideoStart:
            self.__startBGMode()
        else:
            self.__applyWindowAccessibility()

    def __startBGMode(self):
        self.__loadFromPrefs()
        if self.__bgMode == _BG_MODE_VIDEO:
            self.__view.as_showLoginVideoS(_LOGIN_VIDEO_FILE, self.__bufferTime, self.__isSoundMuted)
        else:
            self.showWallpaper(self.__switchButton)

    def __applyWindowAccessibility(self):
        if self.__inSwitchToMode == _BG_MODE_VIDEO or not self.__inSwitchToMode and self.__bgMode == _BG_MODE_VIDEO:
            if self.__isWindowAccessible:
                self.__view.as_resumePlaybackS()
                WWISE.WW_eventGlobal('loginscreen_music_resume')
            else:
                self.__view.as_pausePlaybackS()
                WWISE.WW_eventGlobal('loginscreen_music_pause')

    def __loadFromPrefs(self):
        if self.__userPrefs.has_key(Settings.KEY_LOGINPAGE_PREFERENCES):
            ds = self.__userPrefs[Settings.KEY_LOGINPAGE_PREFERENCES]
            self.__isSoundMuted = ds.readBool('mute', False)
            self.__bgMode = ds.readInt('lastBgMode', _BG_MODE_VIDEO)
            self.__lastImage = ds.readString('lastLoginBgImage', '')
            self.__show = ds.readBool('showLoginWallpaper', True)

    def __saveToPrefs(self):
        if not self.__userPrefs.has_key(Settings.KEY_LOGINPAGE_PREFERENCES):
            self.__userPrefs.write(Settings.KEY_LOGINPAGE_PREFERENCES, '')
        ds = self.__userPrefs[Settings.KEY_LOGINPAGE_PREFERENCES]
        ds.writeBool('mute', self.__isSoundMuted)
        ds.writeInt('lastBgMode', self.__bgMode)
        ds.writeString('lastLoginBgImage', self.__lastImage)
        ds.writeBool('showLoginWallpaper', self.__show)

    def __randomImage(self):
        imagesPath = '../maps/login/%s.png'
        if self.__show and self.__images:
            if len(self.__images) == 1:
                newFile = self.__images[0]
            else:
                while True:
                    newFile = random.choice(self.__images)
                    if newFile != self.__lastImage:
                        break

            self.__lastImage = newFile
        else:
            newFile = '__login_bg'
        return imagesPath % newFile

    @staticmethod
    def __getWallpapersList():
        files = []
        ds = ResMgr.openSection(SCALEFORM_WALLPAPER_PATH)
        for filename in ds.keys():
            if filename[-4:] == '.png' and filename[0:2] != '__':
                files.append(filename[0:-4])

        ResMgr.purge(SCALEFORM_WALLPAPER_PATH, True)
        return files
