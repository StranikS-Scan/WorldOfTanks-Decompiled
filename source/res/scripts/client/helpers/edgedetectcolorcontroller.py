# Embedded file name: scripts/client/helpers/EdgeDetectColorController.py
import BigWorld, ResMgr, Math
from PlayerEvents import g_playerEvents
from Account import PlayerAccount
from account_helpers.settings_core.SettingsCore import g_settingsCore
g_instance = None

class EdgeDetectColorController:

    def __init__(self, dataSec):
        self.__colors = {'common': dict(),
         'colorBlind': dict()}
        self.__readColors(self.__colors['common'], 'common', dataSec)
        self.__readColors(self.__colors['colorBlind'], 'colorBlind', dataSec)
        g_settingsCore.onSettingsChanged += self.__changeColor
        g_playerEvents.onAccountShowGUI += self.__onAccountShowGUI

    def updateColors(self):
        """
        update color based on the current player account.
        :param place: '' for battle, 'hangar' when in hangar
        :return:
        """
        self.__changeColor({'isColorBlind': g_settingsCore.getSetting('isColorBlind')})

    def destroy(self):
        g_settingsCore.onSettingsChanged -= self.__changeColor
        g_playerEvents.onAccountShowGUI -= self.__onAccountShowGUI

    def __readColors(self, out, type, section):
        cName = '%s/' % type
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
