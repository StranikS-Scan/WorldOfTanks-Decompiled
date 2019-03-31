# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/EdgeDetectColorController.py
# Compiled at: 2011-07-13 22:06:15
import BigWorld, ResMgr, Math
from account_helpers.AccountSettings import AccountSettings
g_instance = None

class EdgeDetectColorController:

    def __init__(self, dataSec):
        self.__colors = {'common': dict(),
         'colorBlind': dict()}
        self.__readColors(self.__colors['common'], 'common', dataSec)
        self.__readColors(self.__colors['colorBlind'], 'colorBlind', dataSec)
        AccountSettings.onSettingsChanging += self.__changeColor

    def updateColors(self):
        self.__changeColor('isColorBlind')

    def destroy(self):
        AccountSettings.onSettingsChanging -= self.__changeColor

    def __readColors(self, out, type, section):
        cName = '%s/' % type
        out['self'] = section.readVector4(cName + 'self', Math.Vector4(0.2, 0.2, 0.2, 0.5))
        out['enemy'] = section.readVector4(cName + 'enemy', Math.Vector4(1, 0, 0, 0.5))
        out['friend'] = section.readVector4(cName + 'friend', Math.Vector4(0, 1, 0, 0.5))

    def __changeColor(self, args):
        if args != 'isColorBlind':
            return
        cType = 'colorBlind' if AccountSettings.getSettings('isColorBlind') is True else 'common'
        colors = self.__colors[cType]
        BigWorld.wgSetEdgeDetectColors((colors['self'], colors['enemy'], colors['friend']))
