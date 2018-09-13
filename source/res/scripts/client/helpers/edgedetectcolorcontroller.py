# Embedded file name: scripts/client/helpers/EdgeDetectColorController.py
import BigWorld, ResMgr, Math
from account_helpers.settings_core.SettingsCore import g_settingsCore
g_instance = None

class EdgeDetectColorController:

    def __init__(self, dataSec):
        self.__colors = {'common': dict(),
         'colorBlind': dict()}
        self.__readColors(self.__colors['common'], 'common', dataSec)
        self.__readColors(self.__colors['colorBlind'], 'colorBlind', dataSec)
        g_settingsCore.onSettingsChanged += self.__changeColor

    def updateColors(self):
        self.__changeColor({'isColorBlind': g_settingsCore.getSetting('isColorBlind')})

    def destroy(self):
        g_settingsCore.onSettingsChanged -= self.__changeColor

    def __readColors(self, out, type, section):
        cName = '%s/' % type
        out['self'] = section.readVector4(cName + 'self', Math.Vector4(0.2, 0.2, 0.2, 0.5))
        out['enemy'] = section.readVector4(cName + 'enemy', Math.Vector4(1, 0, 0, 0.5))
        out['friend'] = section.readVector4(cName + 'friend', Math.Vector4(0, 1, 0, 0.5))

    def __changeColor(self, diff):
        if 'isColorBlind' not in diff:
            return
        cType = 'colorBlind' if diff['isColorBlind'] else 'common'
        colors = self.__colors[cType]
        BigWorld.wgSetEdgeDetectColors((colors['self'], colors['enemy'], colors['friend']))
