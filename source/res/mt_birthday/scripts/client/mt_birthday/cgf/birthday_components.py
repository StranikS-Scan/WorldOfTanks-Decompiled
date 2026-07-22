# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/cgf/birthday_components.py
import CGF
from helpers import dependency
from gui.shared.utils.scheduled_notifications import AcyclicNotifier
from cgf_components.hover_component import SelectionComponent, IsHoveredComponent
from cgf_components.event_state_components import EventStateEnabledComponent
from cgf_components.marker_component import LobbyFlashMarker
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery
from cgf_script.component_meta_class import registerComponent, ComponentProperty, CGFMetaTypes
from constants import IS_CLIENT
from mt_birthday.skeletons.mt_birthday_controller import ITanksBirthdayController
from mt_birthday.birthday_constants import AnchorNames
from mt_birthday.gui.impl.gen.view_models.views.lobby.birthday.birthday_main_view_model import TabId
from skeletons.gui.app_loader import IAppLoader
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from helpers.gui_utils import getMouseScreenPosition
from helpers.cgf_utils import toggleCgfComponent
_METHOD_BY_ANCHOR_NAME = None
_TOOLTIP_SHOW_DELAY = 0.4
if IS_CLIENT:
    from mt_birthday.gui.shared.event_dispatcher import showMainView, showGoldWagon
    _METHOD_BY_ANCHOR_NAME = {AnchorNames.POST_OFFICE: showMainView,
     AnchorNames.GOLD_WAGON: showGoldWagon,
     AnchorNames.QUEST_GIVER: lambda : showMainView(TabId.QUESTS)}

@registerComponent
class BirthdayOutlineGoComponent(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Birthday Outline Game object'
    category = 'Birthday'
    objectName = ComponentProperty(type=CGFMetaTypes.STRING, editorName='object name', value=AnchorNames.POST_OFFICE)


class BirthdayEventManager(CGF.ComponentManager):
    __tankBirthdayController = dependency.descriptor(ITanksBirthdayController)

    def __init__(self, *args):
        super(BirthdayEventManager, self).__init__(*args)
        self.__initialFlashMarkers = {}

    def activate(self):
        self.__tankBirthdayController.onEventSettingsUpdated += self.__onBirthdaySettingsChange

    def deactivate(self):
        self.__tankBirthdayController.onEventSettingsUpdated -= self.__onBirthdaySettingsChange

    @onAddedQuery(BirthdayOutlineGoComponent)
    def onAdded(self, *args):
        self.__onBirthdaySettingsChange()

    def __onBirthdaySettingsChange(self):
        birthdayComponents = CGF.Query(self.spaceID, (CGF.GameObject, BirthdayOutlineGoComponent))
        hierarchyManager = CGF.HierarchyManager(self.spaceID)
        if not hierarchyManager:
            return
        else:
            for go, outlineComponent in birthdayComponents:
                if hierarchyManager.getChildrenIncludingInactive(go) is not None:
                    for child in hierarchyManager.getChildrenIncludingInactive(go):
                        flashMarkerComponent = child.findComponentByType(LobbyFlashMarker)
                        if flashMarkerComponent is not None and outlineComponent.objectName not in self.__initialFlashMarkers:
                            self.__initialFlashMarkers[outlineComponent.objectName] = {'icon': flashMarkerComponent.icon,
                             'textKey': flashMarkerComponent.textKey,
                             'iconPosition': flashMarkerComponent.iconPosition}
                        isGoldWagon = outlineComponent.objectName == AnchorNames.GOLD_WAGON
                        if isGoldWagon:
                            isComponentEnabled = self.__tankBirthdayController.isGoldWagonEnabled() and self.__tankBirthdayController.isEnabled()
                        else:
                            isComponentEnabled = self.__tankBirthdayController.isEnabled()
                        isComponentDisabled = self.__tankBirthdayController.isDisabled() or not isComponentEnabled
                        if isComponentEnabled:
                            toggleCgfComponent(child, LobbyFlashMarker, False)
                            initialFlashMarker = self.__initialFlashMarkers.get(outlineComponent.objectName, None)
                            if initialFlashMarker is not None:
                                child.createComponent(LobbyFlashMarker, '', initialFlashMarker['textKey'], initialFlashMarker['iconPosition'])
                            toggleCgfComponent(go, EventStateEnabledComponent, True)
                        else:
                            toggleCgfComponent(child, LobbyFlashMarker, False)
                            initialFlashMarker = self.__initialFlashMarkers.get(outlineComponent.objectName, None)
                            if initialFlashMarker is not None:
                                child.createComponent(LobbyFlashMarker, initialFlashMarker['icon'], initialFlashMarker['textKey'], initialFlashMarker['iconPosition'])
                            toggleCgfComponent(go, EventStateEnabledComponent, False)
                        if isComponentDisabled:
                            toggleCgfComponent(go, SelectionComponent, False)
                            toggleCgfComponent(child, LobbyFlashMarker, False)
                        toggleCgfComponent(go, SelectionComponent, True)

            return


class BirthdayClickManager(CGF.ComponentManager):

    @onAddedQuery(BirthdayOutlineGoComponent, SelectionComponent, EventStateEnabledComponent)
    def handleBirthdayClickAdded(self, outlineComponent, selectionComponent, _):
        method = _METHOD_BY_ANCHOR_NAME[outlineComponent.objectName]
        selectionComponent.onClickAction += method

    @onRemovedQuery(BirthdayOutlineGoComponent, SelectionComponent, EventStateEnabledComponent)
    def handleBirthdayClickRemoved(self, outlineComponent, selectionComponent, _):
        method = _METHOD_BY_ANCHOR_NAME[outlineComponent.objectName]
        selectionComponent.onClickAction -= method


class BirthdayTooltipManager(CGF.ComponentManager):
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self):
        super(BirthdayTooltipManager, self).__init__()
        self.__notifier = None
        return

    def __cancelNotifier(self):
        if self.__notifier is not None:
            self.__notifier.stopNotification()
            self.__notifier = None
        return

    @onAddedQuery(BirthdayOutlineGoComponent, IsHoveredComponent)
    def onTooltipAdded(self, outlineComponent, _):
        self.__cancelNotifier()

        def showTooltip():
            self.__cancelNotifier()
            self.__appLoader.getApp().getToolTipMgr().onCreateWulfTooltip(TOOLTIPS_CONSTANTS.BIRTHDAY_ENTRY_POINT, (outlineComponent.objectName,), *map(int, getMouseScreenPosition()))

        self.__notifier = AcyclicNotifier(lambda : _TOOLTIP_SHOW_DELAY, showTooltip)
        self.__notifier.startNotification()

    @onRemovedQuery(BirthdayOutlineGoComponent, IsHoveredComponent)
    def onTooltipRemoved(self, *_):
        self.__appLoader.getApp().getToolTipMgr().onHideTooltip(TOOLTIPS_CONSTANTS.BIRTHDAY_ENTRY_POINT)
        self.__cancelNotifier()
