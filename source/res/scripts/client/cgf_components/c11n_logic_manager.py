# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/c11n_logic_manager.py
import BigWorld
import CGF
from cgf_script.component_meta_class import registerComponent
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery
from helpers import dependency
from skeletons.gui.game_control import IPlatoonController, IHeroTankController

@registerComponent
class OnC11nAppearComponent(object):
    domain = CGF.DomainOption.DomainClient
    editorTitle = 'On Customization appear'
    category = 'C11n'


@registerComponent
class OnC11nHideComponent(object):
    domain = CGF.DomainOption.DomainClient
    editorTitle = 'On Customization hide'
    category = 'C11n'


class C11nLogicManager(CGF.ComponentManager):
    __heroTankCtrl = dependency.descriptor(IHeroTankController)
    __platoonController = dependency.descriptor(IPlatoonController)

    def __init__(self):
        super(C11nLogicManager, self).__init__()
        self.__c11nAppearRoots = []
        self.__c11nHideRoots = []

    def destroy(self):
        self.clear()

    def deactivate(self):
        self.clear()

    def clear(self):
        self.__c11nAppearRoots = []
        self.__c11nHideRoots = []

    @onAddedQuery(CGF.GameObject, OnC11nAppearComponent)
    def onAddedAppearDetail(self, gameObject, _):
        self.__c11nAppearRoots.append(gameObject)

    @onRemovedQuery(CGF.GameObject, OnC11nAppearComponent)
    def onRemovedAppearDetail(self, gameObject, _):
        if gameObject in self.__c11nAppearRoots:
            self.__c11nAppearRoots.remove(gameObject)

    @onAddedQuery(CGF.GameObject, OnC11nHideComponent)
    def onAddedDisappearDetail(self, gameObject, _):
        self.__c11nHideRoots.append(gameObject)

    @onRemovedQuery(CGF.GameObject, OnC11nHideComponent)
    def onRemovedHideDetail(self, gameObject, _):
        if gameObject in self.__c11nHideRoots:
            self.__c11nHideRoots.remove(gameObject)

    def __hideOtherTanks(self):
        self.__platoonController.onPlatoonTankVisualizationBlocked(True)
        self.__heroTankCtrl.setHidden(True)

    def __showOtherTanks(self):
        self.__platoonController.onPlatoonTankVisualizationBlocked(False)
        self.__heroTankCtrl.setHidden(False)

    def onC11nEnter(self):
        hManager = CGF.HierarchyManager(self.spaceID)
        for appearRoot in self.__c11nAppearRoots:
            children = hManager.getChildrenIncludingInactive(appearRoot)
            if not children:
                continue
            for child in children:
                child.activate()

        for hideRoot in self.__c11nHideRoots:
            children = hManager.getChildrenIncludingInactive(hideRoot)
            if not children:
                continue
            for child in children:
                child.deactivate()

        BigWorld.callback(0.0, self.__hideOtherTanks)

    def onC11nExit(self):
        hManager = CGF.HierarchyManager(self.spaceID)
        for appearRoot in self.__c11nAppearRoots:
            children = hManager.getChildrenIncludingInactive(appearRoot)
            if not children:
                continue
            for child in children:
                child.deactivate()

        for hideRoot in self.__c11nHideRoots:
            children = hManager.getChildrenIncludingInactive(hideRoot)
            if not children:
                continue
            for child in children:
                child.activate()

        self.__showOtherTanks()
