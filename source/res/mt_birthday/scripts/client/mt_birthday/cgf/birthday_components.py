# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/cgf/birthday_components.py
import CGF
import functools
from helpers import dependency
from cgf_components.hover_component import SelectionComponent, IsHoveredComponent
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery
from cgf_script.component_meta_class import registerComponent, ComponentProperty, CGFMetaTypes
from constants import IS_CLIENT
from debug_utils import LOG_ERROR
from mt_birthday.skeletons.mt_birthday_controller import ITanksBirthdayController
from mt_birthday.birthday_constants import AnchorNames
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.lobby_context import ILobbyContext
_METHOD_BY_ANCHOR_NAME = None
if IS_CLIENT:
    from gui.shared.events import LobbySimpleEvent
    from gui.shared import g_eventBus
    from mt_birthday.gui.shared.event_dispatcher import showMainView, showGoldWagon
    _METHOD_BY_ANCHOR_NAME = {AnchorNames.POST_OFFICE: showMainView,
     AnchorNames.GOLD_WAGON: showGoldWagon}

@registerComponent
class BirthdayOutlineGoComponent(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Birthday Outline Game object'
    category = 'Birthday'
    objectName = ComponentProperty(type=CGFMetaTypes.STRING, editorName='object name', value=AnchorNames.POST_OFFICE)


class BirthdayClickManager(CGF.ComponentManager):

    @onAddedQuery(BirthdayOutlineGoComponent, SelectionComponent)
    def handleBirthdayClickAdded(self, outlineComponent, selectionComponent):
        selectionComponent.onClickAction += functools.partial(self.__onClickAction, outlineComponent)

    @onRemovedQuery(BirthdayOutlineGoComponent, SelectionComponent)
    def handleBirthdayClickRemoved(self, outlineComponent, selectionComponent):
        selectionComponent.onClickAction -= functools.partial(self.__onClickAction, outlineComponent)

    def __onClickAction(self, anchorObject):
        method = _METHOD_BY_ANCHOR_NAME.get(anchorObject.objectName)
        if not method:
            LOG_ERROR('{} is not defined, check METHOD_BY_ANCHOR_NAME'.format(anchorObject.objectName))
            return
        method()


class BirthdayTooltipManager(CGF.ComponentManager):
    __appLoader = dependency.descriptor(IAppLoader)
    __birthdayController = dependency.descriptor(ITanksBirthdayController)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    @onAddedQuery(IsHoveredComponent, BirthdayOutlineGoComponent)
    def onTooltipAdded(self, _, outlineComponent):
        selectionId = outlineComponent.objectName
        isEnabledGoldWagon = self.__lobbyContext.getServerSettings().ingameBrowserEventConfig.isEnabled
        if self.__birthdayController.isPaused() or selectionId == AnchorNames.GOLD_WAGON and not isEnabledGoldWagon:
            selectionId += 'OnPause'
        g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.ENTITY_TOOLTIP_SHOW, ctx={'selectionId': selectionId}))

    @onRemovedQuery(IsHoveredComponent, BirthdayOutlineGoComponent)
    def onTooltipRemoved(self, *_):
        g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.ENTITY_TOOLTIP_HIDE))


@registerComponent
class EasterEggsCollageComponent(object):
    editorTitle = 'Collage component'
    category = 'Birthday'
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    camera = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Camera', value=CGF.GameObject)

    @staticmethod
    def click():
        from mt_birthday.gui.shared.event_dispatcher import showCollageView
        showCollageView()


class EasterEggsManager(CGF.ComponentManager):

    @onAddedQuery(SelectionComponent, EasterEggsCollageComponent)
    def onListenerAdded(self, selectionCmp, easterEggsCollageCmp):
        selectionCmp.onClickAction += easterEggsCollageCmp.click

    @onRemovedQuery(SelectionComponent, EasterEggsCollageComponent)
    def onHoverRemoved(self, selectionCmp, easterEggsCollageCmp):
        selectionCmp.onClickAction -= easterEggsCollageCmp.click
