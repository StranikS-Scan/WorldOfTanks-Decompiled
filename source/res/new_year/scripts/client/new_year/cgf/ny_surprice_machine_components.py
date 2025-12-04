# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/cgf/ny_surprice_machine_components.py
import CGF
from cgf_script.component_meta_class import registerComponent, ComponentProperty, CGFMetaTypes
from new_year.skeletons.new_year import INewYearSurpriseMachine, INewYearCurrencyController
from new_year.gui.impl.gen.view_models.common.ny_currency_type_model import NyCurrencyType
from new_year.ny_constants import NyBtnTypes, NySurpriseMachineStates, ViewAliases
from cgf_components.hover_component import SelectionComponent, IsHoveredComponent
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery
from skeletons.gui.impl import INewYearNavigation
from GenericComponents import AnimatorComponent
from Sound import Sound2DComponent
from helpers import dependency

@registerComponent
class NyInteractiveGroup(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'NY Interactive Group'
    category = 'New Year'
    kind = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Kind', value=NySurpriseMachineStates.MACHINE, annotations={'comboBox': {NySurpriseMachineStates.MACHINE: NySurpriseMachineStates.MACHINE,
                  NySurpriseMachineStates.BUTTONS: NySurpriseMachineStates.BUTTONS}})


@registerComponent
class NyMachineActivationComponent(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'NY Machine Activator'
    category = 'New Year'
    highlightSound = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Highlight Sound', value=Sound2DComponent)
    wooshSound = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Woosh Sound', value=Sound2DComponent)
    __nyMachineController = dependency.descriptor(INewYearSurpriseMachine)

    def clickAction(self):
        self.__nyMachineController.tryActivateMachine()
        self.wooshSound().play()

    def playHighlight(self):
        self.highlightSound().play()


class NewYearMachineActivatorManager(CGF.ComponentManager):
    __nyMachineController = dependency.descriptor(INewYearSurpriseMachine)
    __newYearNavigation = dependency.descriptor(INewYearNavigation)

    def activate(self):
        self.__nyMachineController.onUpdateApplyCoin += self.__syncInteractive
        self.__nyMachineController.onActivationChanged += self.__syncInteractive
        self.__nyMachineController.onMachineBusyStatusUpdated += self.__syncInteractive
        self.__newYearNavigation.onChangeView += self.__syncInteractive
        self.__syncInteractive()

    def deactivate(self):
        self.__nyMachineController.onUpdateApplyCoin -= self.__syncInteractive
        self.__nyMachineController.onActivationChanged -= self.__syncInteractive
        self.__nyMachineController.onMachineBusyStatusUpdated -= self.__syncInteractive
        self.__newYearNavigation.onChangeView -= self.__syncInteractive

    @onAddedQuery(NyMachineActivationComponent, SelectionComponent)
    def handleBtnClickAdded(self, machineActComp, selectComp):
        selectComp.onClickAction += machineActComp.clickAction

    @onRemovedQuery(NyMachineActivationComponent, SelectionComponent)
    def handleBtnClickRemoved(self, machineActComp, selectComp):
        selectComp.onClickAction -= machineActComp.clickAction

    @onAddedQuery(NyMachineActivationComponent, IsHoveredComponent)
    def onHoverEnter(self, machineActComp, *_):
        machineActComp.playHighlight()
        self.__nyMachineController.onMachineButtonHovered(True)

    @onRemovedQuery(NyMachineActivationComponent, IsHoveredComponent)
    def onHoverLeave(self, *_):
        self.__nyMachineController.onMachineButtonHovered(False)

    def __syncInteractive(self, *args):
        inView = self.__newYearNavigation.getCurrentViewName() == ViewAliases.SURPRISE_MACHINE_VIEW
        canApply = self.__nyMachineController.canApplyCoin
        busy = self.__nyMachineController.isMachineBusy
        activated = self.__nyMachineController.isMachineActivated
        enable = inView and not activated and canApply and not busy
        if not enable:
            self.__nyMachineController.onMachineButtonHovered(False)
        setGroups(self.spaceID, NySurpriseMachineStates.MACHINE, enable)


@registerComponent
class NyCustomButtonComponent(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'NY Button Type'
    category = 'New Year'
    buttonType = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Button Type', value=NyBtnTypes.PUSH, annotations={'comboBox': {NyBtnTypes.PUSH: NyBtnTypes.PUSH,
                  NyBtnTypes.LEFT: NyBtnTypes.LEFT,
                  NyBtnTypes.RIGHT: NyBtnTypes.RIGHT}})
    highlightSound = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Highlight Sound', value=Sound2DComponent)
    animator = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Animator', value=AnimatorComponent)
    __nyMachineController = dependency.descriptor(INewYearSurpriseMachine)
    __nyCurrencyController = dependency.descriptor(INewYearCurrencyController)
    PRESS_ANIM = 'onButtonPress'
    CAN_APPLY_COIN_ANIM = 'canApplyCoin'

    def clickAction(self):
        if not self.__nyMachineController.canApplyCoin:
            return
        if self.buttonType == NyBtnTypes.PUSH:
            self.__handlePlayAction()
        elif not self.animator().isPlaying():
            self.__handlePlayAction()

    def handleApplyCoinAnimation(self):
        if self.buttonType != NyBtnTypes.PUSH:
            return
        currency = self.__nyCurrencyController.getGiftMachineTokenCount
        if currency > 0:
            if not self.animator().isPlaying():
                self.animator().startLayerByName(self.CAN_APPLY_COIN_ANIM)
        else:
            self.animator().stopLayerByName(self.CAN_APPLY_COIN_ANIM)

    def playHighlight(self):
        self.highlightSound().play()

    def __handlePlayAction(self):
        self.__nyMachineController.handleSurpriseMachineBtnPress(self.buttonType)
        self.animator().startLayerByName(self.PRESS_ANIM)


class NewYearMachineButtonsManager(CGF.ComponentManager):
    __nyMachineController = dependency.descriptor(INewYearSurpriseMachine)
    __nyCurrencyController = dependency.descriptor(INewYearCurrencyController)
    __newYearNavigation = dependency.descriptor(INewYearNavigation)

    def activate(self):
        self.__nyMachineController.onUpdateApplyCoin += self.__syncInteractive
        self.__nyMachineController.onActivationChanged += self.__syncInteractive
        self.__nyMachineController.onMachineBusyStatusUpdated += self.__syncInteractive
        self.__nyCurrencyController.onCurrencyUpdated += self.__onCurrencyUpdated
        self.__newYearNavigation.onChangeView += self.__syncInteractive
        self.__updateCurrency()
        self.__syncInteractive()

    def deactivate(self):
        self.__nyMachineController.onUpdateApplyCoin -= self.__syncInteractive
        self.__nyMachineController.onActivationChanged -= self.__syncInteractive
        self.__nyMachineController.onMachineBusyStatusUpdated -= self.__syncInteractive
        self.__nyCurrencyController.onCurrencyUpdated -= self.__onCurrencyUpdated
        self.__newYearNavigation.onChangeView -= self.__syncInteractive

    @onAddedQuery(NyCustomButtonComponent, SelectionComponent)
    def handleBtnClickAdded(self, btnComp, selectComp):
        selectComp.onClickAction += btnComp.clickAction

    @onRemovedQuery(NyCustomButtonComponent, SelectionComponent)
    def handleBtnClickRemoved(self, btnComp, selectComp):
        selectComp.onClickAction -= btnComp.clickAction

    @onAddedQuery(NyCustomButtonComponent, IsHoveredComponent)
    def onHoverEnter(self, btnComp, *_):
        btnComp.playHighlight()
        self.__nyMachineController.onMachineButtonHovered(True)

    @onRemovedQuery(NyCustomButtonComponent, IsHoveredComponent)
    def onHoverLeave(self, *_):
        self.__nyMachineController.onMachineButtonHovered(False)

    def __syncInteractive(self, *args):
        inView = self.__newYearNavigation.getCurrentViewName() == ViewAliases.SURPRISE_MACHINE_VIEW
        canApply = self.__nyMachineController.canApplyCoin
        busy = self.__nyMachineController.isMachineBusy
        activated = self.__nyMachineController.isMachineActivated
        enable = inView and activated and canApply and not busy
        if not enable:
            self.__nyMachineController.onMachineButtonHovered(False)
        setGroups(self.spaceID, NySurpriseMachineStates.BUTTONS, enable)

    def __onCurrencyUpdated(self, currency, _):
        if currency == NyCurrencyType.NYGIFTMACHINETOKEN:
            self.__updateCurrency()

    def __updateCurrency(self):
        for btnComp in CGF.Query(self.spaceID, NyCustomButtonComponent):
            btnComp.handleApplyCoinAnimation()


def setGroups(spaceID, kind, enable):
    hierarchyManager = CGF.HierarchyManager(spaceID)
    for go, grp in CGF.Query(spaceID, (CGF.GameObject, NyInteractiveGroup)):
        if grp.kind != kind:
            continue
        for child in hierarchyManager.getChildrenIncludingInactive(go):
            if enable:
                child.activate()
            child.deactivate()
