# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/container_vews/personal_file/personal_file_view.py
import typing
import BigWorld
from frameworks.wulf import ViewSettings, ViewFlags
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.personal_case.personal_file_view_model import PersonalFileViewModel
from gui.impl.lobby.container_views.base.components import ContainerBase
from gui.impl.lobby.crew.container_vews.common.tankman_info_component import TankmanInfoComponent
from gui.impl.lobby.crew.container_vews.personal_file.components.post_progression_widget_component import PostProgressionWidgetComponent
from gui.impl.lobby.crew.container_vews.personal_file.components.skill_matrix_component import SkillMatrixComponent
from gui.impl.lobby.crew.container_vews.personal_file.context import PersonalFileViewContext
from gui.impl.lobby.crew.container_vews.personal_file.controller import PersonalFileInteractionController
from gui.impl.lobby.crew.personal_case import IPersonalTab
from gui.impl.lobby.crew.personal_case.base_personal_case_view import BasePersonalCaseView
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.shared import IItemsCache
from uilogging.crew.logging_constants import CrewViewKeys
if typing.TYPE_CHECKING:
    from typing import List, Type
    from gui.impl.lobby.container_views.base.controllers import InteractionController
    from gui.impl.lobby.container_views.base.components import ComponentBase

class PersonalFileView(ContainerBase, IPersonalTab, BasePersonalCaseView):
    __slots__ = ('__viewKey', '__isAnimationShowing', '__hasPendingRefresh')
    TITLE = backport.text(R.strings.crew.tankmanContainer.tab.personalFile())
    itemsCache = dependency.descriptor(IItemsCache)
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, layoutID=R.views.lobby.crew.personal_case.PersonalFileView(), **kwargs):
        self.__viewKey = CrewViewKeys.PERSONAL_FILE
        self.__isAnimationShowing = True
        self.__hasPendingRefresh = False
        settings = ViewSettings(layoutID, ViewFlags.LOBBY_TOP_SUB_VIEW, PersonalFileViewModel())
        super(PersonalFileView, self).__init__(settings, **kwargs)

    @property
    def viewModel(self):
        return super(PersonalFileView, self).getViewModel()

    @property
    def viewKey(self):
        return self.__viewKey

    def onChangeTankman(self, tankmanID):
        if tankmanID != self.context.tankman.invID:
            self.__clearAnimationData(self.context.skillAnimationsSkipped)
        if hasattr(self, 'interactionCtrl'):
            self.interactionCtrl.onChangeTankman(tankmanID)

    def onStopAnimations(self):
        if hasattr(self, 'interactionCtrl'):
            self.interactionCtrl.onStopAnimations()

    def setAnimationInProgress(self, isEnabled):
        self.getParentView().setAnimationInProgress(isEnabled)

    def hideContent(self):
        self.getParentView().toggleContentVisibility(False)

    def showContent(self):
        self.getParentView().toggleContentVisibility(True)

    def updateAnimationShowing(self, isShowing):
        self.__isAnimationShowing = isShowing
        if isShowing and self.__hasPendingRefresh:
            self.__hasPendingRefresh = False
            self.refresh()

    def refresh(self):
        if not self.__isAnimationShowing:
            self.__hasPendingRefresh = True
            return
        super(PersonalFileView, self).refresh()

    def _getComponents(self):
        return [TankmanInfoComponent(key='tankman_info', parent=self), SkillMatrixComponent(key='skill_matrix', parent=self), PostProgressionWidgetComponent(key='post_progression', parent=self)]

    def _getContext(self, *args, **kwargs):
        return PersonalFileViewContext(kwargs.get('tankmanID'))

    def _getInteractionControllerCls(self):
        return PersonalFileInteractionController

    def _fillViewModel(self, vm):
        vm.setTankmanId(self.context.tankmanID)
        vm.setSkillsEfficiency(self.context.tankman.currentVehicleSkillsEfficiency)
        vm.setIsTankmanInVehicle(self.context.tankman.vehicleDescr is not None)
        hasPostProgression = self.context.tankman.descriptor.isMaxSkillXp()
        vm.setHasPostProgression(hasPostProgression)
        if hasPostProgression:
            vm.setIsPostProgressionAnimated(BigWorld.player().crewAccountController.getTankmanVeteranAnimanion(self.context.tankman.invID))
        return

    def _finalize(self):
        try:
            try:
                self.__clearAnimationData()
            except AttributeError:
                pass

        finally:
            super(PersonalFileView, self)._finalize()

    def __clearAnimationData(self, skipped=False):
        if not skipped:
            BigWorld.player().crewAccountController.clearTankmanAnimanions(self.context.tankman.invID)
