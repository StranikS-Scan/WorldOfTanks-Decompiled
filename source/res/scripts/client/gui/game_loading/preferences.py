# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_loading/preferences.py
import typing
if typing.TYPE_CHECKING:
    from ResMgr import DataSection
SECTION_NAME = 'gameLoading'

class GameLoadingPreferences(object):
    __slots__ = ('_gameLoadingPrefs',)

    def __init__(self, preferences):
        super(GameLoadingPreferences, self).__init__()
        if not preferences.has_key(SECTION_NAME):
            preferences.write(SECTION_NAME, '')
        self._gameLoadingPrefs = preferences[SECTION_NAME]

    def getLoadingMax(self, slideID):
        loadingMax = self._gameLoadingPrefs[slideID]
        return loadingMax if loadingMax is None else loadingMax.asInt

    def setLoadingMax(self, slideID, value):
        self._gameLoadingPrefs.write(slideID, value)
