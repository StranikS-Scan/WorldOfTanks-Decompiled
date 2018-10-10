# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/EdgeDetectColorController.py
import BigWorld
import Math
from PlayerEvents import g_playerEvents
from Account import PlayerAccount
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
g_instance = None

class EdgeDetectColorController(object):
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, dataSec):
        self.__colors = {'common': dict(),
         'colorBlind': dict()}
        self.__readColors(self.__colors['common'], 'common', dataSec)
        self.__readColors(self.__colors['colorBlind'], 'colorBlind', dataSec)

    def updateColors(self):
        self.__changeColor({'isColorBlind': self.settingsCore.getSetting('isColorBlind')})

    def create(self):
        self.settingsCore.onSettingsChanged += self.__changeColor
        g_playerEvents.onAccountShowGUI += self.__onAccountShowGUI

    def destroy(self):
        self.settingsCore.onSettingsChanged -= self.__changeColor
        g_playerEvents.onAccountShowGUI -= self.__onAccountShowGUI

    def __readColors(self, out, cType, section):
        cName = '%s/' % cType
        out['self'] = section.readVector4(cName + 'self', Math.Vector4(0.2, 0.2, 0.2, 0.5))
        out['enemy'] = section.readVector4(cName + 'enemy', Math.Vector4(1, 0, 0, 0.5))
        out['friend'] = section.readVector4(cName + 'friend', Math.Vector4(0, 1, 0, 0.5))
        out['flag'] = section.readVector4(cName + 'flag', Math.Vector4(1, 1, 1, 1))
        out['hangar'] = section.readVector4(cName + 'hangar', Math.Vector4(1, 1, 0, 1))

    def __onAccountShowGUI(self, ctx):
        self.updateColors()

    def __changeColor(self, diff):
        if 'isColorBlind' not in diff:
            return
        cType = 'colorBlind' if diff['isColorBlind'] else 'common'
        isHangar = isinstance(BigWorld.player(), PlayerAccount)
        colors = self.__colors[cType]
        colorsSet = (colors['hangar'] if isHangar else colors['self'],
         colors['enemy'],
         colors['friend'],
         colors['flag'])
        BigWorld.wgSetEdgeDetectColors(colorsSet)
