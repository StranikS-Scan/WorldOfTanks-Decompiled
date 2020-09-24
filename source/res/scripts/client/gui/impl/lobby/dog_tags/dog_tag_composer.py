# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/dog_tags/dog_tag_composer.py
from collections import defaultdict
from enum import Enum
import typing
from debug_utils import LOG_DEBUG_DEV
from dog_tags_common.number_formatter import formatComponentValue, customRound
from dog_tags_common.config.common import ComponentViewType, ComponentPurpose, NO_PROGRESS
from gui.dog_tag_composer import DogTagComposerClient
from gui.impl.gen.view_models.views.lobby.dog_tags.dt_grid_section import DtGridSection
from gui.impl.gen.view_models.views.lobby.dog_tags.dt_component import DtComponent
from dog_tags_common.components_config import componentConfigAdapter as componentConfig, SourceData, DictIterator
from helpers import getLanguageCode
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
if typing.TYPE_CHECKING:
    from typing import Dict, Iterable
    from account_helpers.dog_tags import DogTags
    from dog_tags_common.config.dog_tag_framework import ComponentDefinition
    from dog_tags_common.player_dog_tag import DisplayableDogTag
    from frameworks.wulf import Array
    from gui.impl.gen.view_models.views.lobby.dog_tags.dt_dog_tag import DtDogTag
    from gui.impl.gen.view_models.views.lobby.dog_tags.dog_tags_view_model import DogTagsViewModel
    from gui.impl.gen.view_models.views.lobby.premacc.dashboard.prem_dashboard_dog_tags_card_model import PremDashboardDogTagsCardModel

class PurposeGroup(Enum):
    TRIUMPH = 'TRIUMPH'
    DEDICATION = 'DEDICATION'
    SEASON = 'SEASON'


PURPOSE_TO_PURPOSE_GROUP_MAP = {ComponentPurpose.SKILL: PurposeGroup.SEASON,
 ComponentPurpose.TRIUMPH: PurposeGroup.TRIUMPH,
 ComponentPurpose.DEDICATION: PurposeGroup.DEDICATION}

class DogTagComposerLobby(DogTagComposerClient):
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, dtHelper):
        self._dtHelper = dtHelper
        self.serverSettings = self.lobbyContext.getServerSettings

    def fillModel(self, model, dogtag):
        model.setPlayerName(self._formatName(dogtag.getNickName()))
        model.setClanTag(dogtag.getClanTag())
        engravingId = dogtag.getComponentByType(ComponentViewType.ENGRAVING).compId
        backgroundId = dogtag.getComponentByType(ComponentViewType.BACKGROUND).compId
        self._fillComponentModel(componentConfig.getComponentById(backgroundId), model.background)
        self._fillComponentModel(componentConfig.getComponentById(engravingId), model.engraving)

    def fillDTCardModel(self, model):
        displayableDT = self._dtHelper.getDisplayableDT()
        engraving = displayableDT.getComponentByType(ComponentViewType.ENGRAVING)
        background = displayableDT.getComponentByType(ComponentViewType.BACKGROUND)
        engravingImage = self.getComponentImage(engraving.compId, engraving.grade)
        bgImage = self.getComponentImage(background.compId)
        model.setIsAvailable(self.serverSettings().isDogTagCustomizationScreenEnabled())
        model.setEngraving(engravingImage)
        model.setBackground(bgImage)
        model.Counter.setValue(len(self._dtHelper.getUnseenComps()))
        LOG_DEBUG_DEV('Dashboard dogtag images - engraving: {}, background: {}'.format(engravingImage, bgImage))

    def fillGrid(self, viewModel):
        unlockedComponents = self._dtHelper.getUnlockedComps()
        allComponents = self._getVisibleComponents(unlockedComponents)
        gridSectionArray = viewModel.getBackgroundGrid()
        gridSectionArray.clear()
        self._fillSectionArray(gridSectionArray, allComponents, unlockedComponents, ComponentViewType.BACKGROUND)
        gridSectionArray.invalidate()
        gridSectionArray = viewModel.getEngravingGrid()
        gridSectionArray.clear()
        self._fillSectionArray(gridSectionArray, allComponents, unlockedComponents, ComponentViewType.ENGRAVING)
        gridSectionArray.invalidate()

    def updateComponentModel(self, viewModel, compId):
        comp = componentConfig.getComponentById(compId)
        componentModel = self._getCorrespondingCompModel(viewModel, comp)
        self._fillComponentModel(comp, componentModel, comp.componentId in self._dtHelper.getUnlockedComps())

    @staticmethod
    def _getVisibleComponents(unlockedComponents):
        nonDeprecated = componentConfig.getAllComponents(SourceData.NON_DEPRECATED_ONLY)
        unlockedBeforeDeprecation = {}
        for compId in unlockedComponents:
            comp = componentConfig.getComponentById(compId, SourceData.DEPRECATED_ONLY)
            if comp is not None:
                unlockedBeforeDeprecation[compId] = comp

        return DictIterator(nonDeprecated, unlockedBeforeDeprecation)

    @staticmethod
    def _getCorrespondingCompModel(viewModel, comp):
        if comp.viewType == ComponentViewType.ENGRAVING:
            gridSections = viewModel.getEngravingGrid()
        else:
            gridSections = viewModel.getBackgroundGrid()
        for gridSection in gridSections:
            for componentModel in gridSection.getItems():
                if comp.componentId == componentModel.getId():
                    return componentModel

    def _fillSectionArray(self, section, components, unlockedComponents, componentType):
        sectionComponents = defaultdict(dict)
        for compId, comp in components.iteritems():
            if comp.viewType == componentType:
                purpose = comp.purpose
                if purpose == ComponentPurpose.SKILL and not self.serverSettings().isSkillComponentsEnabled():
                    continue
                if comp.purpose == ComponentPurpose.BASE:
                    purpose = ComponentPurpose.TRIUMPH_MEDAL
                sectionComponents[purpose][compId] = comp

        for purpose in sectionComponents.keys():
            if not sectionComponents[purpose]:
                continue
            gridSection = self._createSection(sectionComponents[purpose], unlockedComponents, self.getPurposeRes(purpose))
            if purpose in PURPOSE_TO_PURPOSE_GROUP_MAP:
                purposeGroup = PURPOSE_TO_PURPOSE_GROUP_MAP[purpose]
                gridSection.setTooltipTitle(self.getPurposeGroupRes(purposeGroup.value))
                gridSection.setTooltipDescription(self.getPurposeTooltipRes(purposeGroup.value))
            section.addViewModel(gridSection)

    def _createSection(self, components, unlockedIds, sectionName):
        gridSection = DtGridSection()
        gridSection.setTitle(sectionName)
        itemsArray = gridSection.getItems()
        defaults, unlocked, locked = {}, {}, {}
        for compId, component in components.iteritems():
            if component.isDefault:
                defaults[compId] = component
            if compId in unlockedIds:
                unlocked[compId] = component
            locked[compId] = component

        self._fillItems(defaults, itemsArray, True)
        self._fillItems(unlocked, itemsArray, True)
        self._fillItems(locked, itemsArray, False)
        return gridSection

    def _fillItems(self, components, itemsArray, unlocked):
        componentIds = sorted(components.keys())
        for componentId in componentIds:
            componentModel = DtComponent()
            self._fillComponentModel(components[componentId], componentModel, unlocked)
            itemsArray.addViewModel(componentModel)

    def _fillComponentModel(self, componentDef, model, isUnlocked=True):
        model.setId(componentDef.componentId)
        model.setPurpose(componentDef.purpose.value.lower())
        model.setType(componentDef.viewType.value.lower())
        currProg = self._dtHelper.getComponentProgress(componentDef.componentId)
        nextGrade = currProg.grade + 1
        currProgValue = customRound(currProg.value, 2)
        model.setIsLocked(not isUnlocked)
        model.setCurrentGradeValue(self.__getUnlockThresholdForGrade(componentDef.componentId, currProg.grade))
        model.setNextGradeValue(self.__getUnlockThresholdForGrade(componentDef.componentId, nextGrade))
        model.setCurrentProgress(currProgValue)
        progressFormatted = formatComponentValue(getLanguageCode(), currProgValue, componentDef.numberType)
        model.setDisplayableProgress(progressFormatted)
        model.setCurrentGrade(currProg.grade if isUnlocked else 0)
        model.setIsNew(componentDef.componentId in self._dtHelper.getUnseenComps())
        model.setIsDeprecated(componentDef.isDeprecated)
        model.setProgressNumberType(componentDef.numberType.value)
        if componentDef.purpose == ComponentPurpose.SKILL and isUnlocked and currProgValue < componentDef.grades[0]:
            model.setIsDemoted(True)

    @staticmethod
    def __getUnlockThresholdForGrade(compId, grade):
        if compId not in componentConfig.getAllComponents():
            return NO_PROGRESS
        comp = componentConfig.getComponentById(compId)
        if not comp.grades:
            return NO_PROGRESS
        return NO_PROGRESS if grade >= len(comp.grades) else comp.grades[grade]
