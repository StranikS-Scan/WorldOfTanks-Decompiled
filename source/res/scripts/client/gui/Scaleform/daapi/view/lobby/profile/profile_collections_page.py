# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/profile_collections_page.py
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.lobby.collection.collections_main_view import CollectionsMainView
from gui.shared.event_dispatcher import showCollectionsIntro

class ProfileCollectionsPage(InjectComponentAdaptor):

    def __init__(self, *args):
        super(ProfileCollectionsPage, self).__init__()

    def onSectionActivated(self):
        if self.__view is not None:
            self.__view.activate()
        return

    def onSectionDeactivated(self):
        if self.__view is not None:
            self.__view.deactivate()
        return

    def _makeInjectView(self):
        self.__view = CollectionsMainView()
        return self.__view

    def _createInjectView(self, *args):
        super(ProfileCollectionsPage, self)._createInjectView(*args)
        showCollectionsIntro()
