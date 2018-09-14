# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCBattleTopHint.py
from gui.Scaleform.daapi.view.meta.BCBattleTopHintMeta import BCBattleTopHintMeta
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from bootcamp.BootCampEvents import g_bootcampEvents
from constants import HINT_TYPE
HINT_VISIBILITY_COMPONENTS_MAP = {HINT_TYPE.HINTS_B3_CAPTURE: BATTLE_VIEW_ALIASES.TEAM_BASES_PANEL,
 HINT_TYPE.HINTS_B3_DETECTED: BATTLE_VIEW_ALIASES.SIXTH_SENSE}

class BCBattleTopHint(BCBattleTopHintMeta):

    def __init__(self):
        super(BCBattleTopHint, self).__init__()
        self.__hideCallback = None
        self.__id = None
        self.__message = None
        self.__completed = None
        self.__componentName = None
        return

    def showHint(self, settings):
        self.__hideCallback = settings['hideCallback']
        self.__id = settings['id']
        self.__message = settings['message']
        self.__completed = settings['completed']
        self.as_showHintS(self.__id, self.__message, self.__completed)
        for group, name in HINT_VISIBILITY_COMPONENTS_MAP.iteritems():
            if self.__id in group:
                self.__componentName = name
                g_bootcampEvents.onBattleComponentVisibility(self.__componentName, False)
                break

    def animFinish(self):
        if self.__hideCallback is not None:
            self.__hideCallback()
            self.__hideCallback = None
        return

    def complete(self):
        if self.__id is not None and self.__message is not None:
            self.as_showHintS(self.__id, self.__message, True)
        return

    def hideHint(self):
        self.as_hideHintS()
        if self.__componentName is not None:
            g_bootcampEvents.onBattleComponentVisibility(self.__componentName, True)
        return

    def closeHint(self):
        self.as_closeHintS()
        self.__hideCallback = None
        if self.__componentName is not None:
            g_bootcampEvents.onBattleComponentVisibility(self.__componentName, True)
        return
