# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal_client_cgf/edge_detect_color/managers.py
import BigWorld
import CGF
from PlayerEvents import g_playerEvents
from helpers import dependency
from shared_utils import nextTick
from skeletons.account_helpers.settings_core import ISettingsCore
from cgf_script.managers_registrator import onAddedQuery
from portal_client_cgf.edge_detect_color.components import EdgeDetectFillColorComponent
from portal_common_cgf.portal_helpers import registerPortalManager
_FRIEND_EDGE_INDEX = 2

@registerPortalManager(CGF.DomainOption.DomainClient)
class EdgeDetectFillColorManager(CGF.ComponentManager):
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        super(EdgeDetectFillColorManager, self).__init__()
        self.settingsCore.onSettingsChanged += self.__onSettingsChanged
        g_playerEvents.onAccountShowGUI += self.__onAccountShowGUI

    def destroy(self):
        self.settingsCore.onSettingsChanged -= self.__onSettingsChanged
        g_playerEvents.onAccountShowGUI -= self.__onAccountShowGUI

    @onAddedQuery(CGF.GameObject, EdgeDetectFillColorComponent)
    def onComponentAdded(self, go, component):
        self.__applyTeammateColors()

    def __onSettingsChanged(self, diff):
        if 'isColorBlind' not in diff:
            return
        nextTick(self.__applyTeammateColors)()

    def __onAccountShowGUI(self, ctx):
        nextTick(self.__applyTeammateColors)()

    def __applyTeammateColors(self):
        query = CGF.Query(self.spaceID, (CGF.GameObject, EdgeDetectFillColorComponent))
        for _, component in query:
            BigWorld.setEdgeDetectEdgeColor(_FRIEND_EDGE_INDEX, component.fillColor)
            BigWorld.setEdgeDetectSolidColors(_FRIEND_EDGE_INDEX, component.solidOverlay, component.solidDestructible)
            BigWorld.setEdgeDetectPatternColors(_FRIEND_EDGE_INDEX, component.patternOverlayForeground, component.patternOverlay, component.patternDestructibleForeground, component.patternDestructible)
            return
