# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/EdgeDetectColorController.py
import BigWorld
import Math
from PlayerEvents import g_playerEvents
from Account import PlayerAccount
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IFestivityController
_DEFAULT_OVERLAY_COLOR = Math.Vector4(1, 1, 1, 1)
_OVERLAY_SOLID_KEYS = ('overlay', 'destructible')
_OVERLAY_PATTERN_KEYS = ('overlayForeground', 'overlay', 'destructibleForeground', 'destructible')
_OVERLAY_TARGET_INDEXES = {'enemy': 1,
 'friend': 2}
g_instance = None

class EdgeDetectColorController(object):
    settingsCore = dependency.descriptor(ISettingsCore)
    _festivityController = dependency.descriptor(IFestivityController)

    def __init__(self, dataSec):
        self.__colors = {'common': dict(),
         'colorBlind': dict()}
        self.__readColors(self.__colors, 'common', dataSec)
        self.__readColors(self.__colors, 'colorBlind', dataSec)

    def updateColors(self):
        self.__changeColor({'isColorBlind': self.settingsCore.getSetting('isColorBlind')})

    def create(self):
        self.settingsCore.onSettingsChanged += self.__changeColor
        g_playerEvents.onAccountShowGUI += self.__onAccountShowGUI
        self._festivityController.onStateChanged += self.__updateFestivityState

    def destroy(self):
        self.settingsCore.onSettingsChanged -= self.__changeColor
        g_playerEvents.onAccountShowGUI -= self.__onAccountShowGUI
        self._festivityController.onStateChanged -= self.__updateFestivityState

    def __readColors(self, colors, cType, section):
        cName = '{}/'.format(cType)
        out, common = colors[cType], colors['common']
        out['self'] = section.readVector4(cName + 'self', common.get('self', Math.Vector4(0.2, 0.2, 0.2, 0.5)))
        out['enemy'] = section.readVector4(cName + 'enemy', common.get('enemy', Math.Vector4(1, 0, 0, 0.5)))
        out['friend'] = section.readVector4(cName + 'friend', common.get('friend', Math.Vector4(0, 1, 0, 0.5)))
        out['flag'] = section.readVector4(cName + 'flag', common.get('flag', Math.Vector4(1, 1, 1, 1)))
        out['hangar'] = section.readVector4(cName + 'hangar', common.get('hangar', Math.Vector4(1, 1, 0, 1)))
        self.__readOverlayColors(out, common, cType, 'overlaySolidColors', _OVERLAY_SOLID_KEYS, section)
        self.__readOverlayColors(out, common, cType, 'overlayPatternColors', _OVERLAY_PATTERN_KEYS, section)

    def __readOverlayColors(self, out, common, cType, overlayType, keys, section):
        targets = ['enemy', 'friend']
        common, out[overlayType] = common.get(overlayType) or {}, {}
        for target in targets:
            commonTarget, out[overlayType][target] = common.get(target) or {}, {}
            targetPath = '/'.join([cType, overlayType, target]) + '/'
            for key in keys:
                color = section.readVector4(targetPath + key, commonTarget.get(key, _DEFAULT_OVERLAY_COLOR))
                out[overlayType][target][key] = color

            out[overlayType][target]['packed'] = [ out[overlayType][target][key] for key in keys ]

    def __onAccountShowGUI(self, ctx):
        self.updateColors()

    def __updateFestivityState(self):
        self.updateColors()

    def __changeColor(self, diff):
        if 'isColorBlind' not in diff:
            return
        isHangar = isinstance(BigWorld.player(), PlayerAccount)
        cType = 'colorBlind' if diff['isColorBlind'] else 'common'
        isFestivityHangar = isHangar and self._festivityController.isEnabled()
        colors = self.__colors[cType]
        colorsSet = (colors['hangar'] if isHangar else colors['self'],
         colors['enemy'],
         colors['friend'],
         self._festivityController.getHangarEdgeColor() if isFestivityHangar else colors['flag'])
        i = 0
        for c in colorsSet:
            BigWorld.wgSetEdgeDetectEdgeColor(i, c)
            i += 1

        for target, idx in _OVERLAY_TARGET_INDEXES.iteritems():
            BigWorld.wgSetEdgeDetectSolidColors(idx, *colors['overlaySolidColors'][target]['packed'])
            BigWorld.wgSetEdgeDetectPatternColors(idx, *colors['overlayPatternColors'][target]['packed'])
