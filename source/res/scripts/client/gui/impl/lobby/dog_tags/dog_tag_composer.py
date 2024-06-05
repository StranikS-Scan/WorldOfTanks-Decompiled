# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/dog_tags/dog_tag_composer.py
import logging
from collections import defaultdict
import typing
from enum import Enum
from gui.impl.lobby.dog_tags.dog_tag_processors import getCoupledDogTagProgress
from gui.server_events import settings as userSettings
from dog_tags_common.components_config import componentConfigAdapter as componentConfig, SourceData, DictIterator
from dog_tags_common.config.common import ComponentViewType, ComponentPurpose, NO_PROGRESS
from dog_tags_common.number_formatter import formatComponentValue, customRound
from gui.dog_tag_composer import DogTagComposerClient
from gui.impl.gen.view_models.views.lobby.account_dashboard.dog_tag_model import DogTagModel
from gui.impl.gen.view_models.views.lobby.dog_tags.dt_component import DtComponent
from gui.impl.gen.view_models.views.lobby.dog_tags.dt_grid_section import DtGridSection
from gui.limited_ui.lui_rules_storage import LuiRules
from helpers import dependency
from helpers import getLanguageCode
from helpers.dependency import replace_none_kwargs
from skeletons.gui.game_control import ILimitedUIController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Dict, Iterable
    from account_helpers.dog_tags import DogTags
    from dog_tags_common.config.dog_tag_framework import ComponentDefinition
    from dog_tags_common.dog_tags_storage import ProgressRecord
    from dog_tags_common.player_dog_tag import DisplayableDogTag
    from frameworks.wulf import Array
    from gui.clans.clan_account_profile import ClanAccountProfile
    from gui.impl.gen.view_models.views.lobby.dog_tags.dt_dog_tag import DtDogTag
    from gui.impl.gen.view_models.views.lobby.dog_tags.dog_tags_view_model import DogTagsViewModel
_logger = logging.getLogger(__name__)

class TooltipPurposeGroup(Enum):
    TRIUMPH = 'TRIUMPH'
    DEDICATION = 'DEDICATION'
    SEASON = 'SEASON'


class SectionType(Enum):
    BACKGROUND = ComponentViewType.BACKGROUND.value
    ENGRAVING = ComponentViewType.ENGRAVING.value
    COUPLED = 'coupled'


class EngravingSection(Enum):
    TRIUMPH = 'TRIUMPH'
    DEDICATION = 'DEDICATION'
    SKILL = 'SKILL'


class BackgroundSection(Enum):
    TRIUMPH_MEDAL = 'TRIUMPH_MEDAL'


class CoupledSection(Enum):
    Animated = 'ANIMATED'


PURPOSE_TO_TOOLTIP_PURPOSE_GROUP_MAP = {EngravingSection.SKILL: TooltipPurposeGroup.SEASON,
 EngravingSection.TRIUMPH: TooltipPurposeGroup.TRIUMPH,
 EngravingSection.DEDICATION: TooltipPurposeGroup.DEDICATION}
SECTION_ORDER_MAP = {SectionType.BACKGROUND: [BackgroundSection.TRIUMPH_MEDAL],
 SectionType.ENGRAVING: [EngravingSection.DEDICATION, EngravingSection.SKILL, EngravingSection.TRIUMPH],
 SectionType.COUPLED: [CoupledSection.Animated]}
IN_SECTION_ORDER_WEIGHT = [ComponentPurpose.RANKED_SKILL, ComponentPurpose.SKILL]
SECTION_BY_PURPOSE = {ComponentPurpose.TRIUMPH: EngravingSection.TRIUMPH,
 ComponentPurpose.SKILL: EngravingSection.SKILL,
 ComponentPurpose.RANKED_SKILL: EngravingSection.SKILL,
 ComponentPurpose.DEDICATION: EngravingSection.DEDICATION,
 ComponentPurpose.BASE: BackgroundSection.TRIUMPH_MEDAL,
 ComponentPurpose.TRIUMPH_MEDAL: BackgroundSection.TRIUMPH_MEDAL,
 ComponentPurpose.COUPLED: CoupledSection.Animated}
SECTION_TYPE_BY_COMPONENT_VIEW_TYPE = {ComponentViewType.BACKGROUND: SectionType.BACKGROUND,
 ComponentViewType.ENGRAVING: SectionType.ENGRAVING}

class DogTagComposerLobby(DogTagComposerClient):
    lobbyContext = dependency.descriptor(ILobbyContext)
    _limitedUIController = dependency.descriptor(ILimitedUIController)

    def __init__(self, dtHelper):
        self._dtHelper = dtHelper
        self.serverSettings = self.lobbyContext.getServerSettings
        self.__dossierDescr = None
        return

    def fillModel(self, model, dogtag, isUnlocked=True):
        model.setPlayerName(dogtag.getNickName())
        model.setClanTag(dogtag.getClanTag())
        engravingId = dogtag.getComponentByType(ComponentViewType.ENGRAVING).compId
        backgroundId = dogtag.getComponentByType(ComponentViewType.BACKGROUND).compId
        self._fillComponentModel(componentConfig.getComponentById(backgroundId), model.background, isUnlocked)
        self._fillComponentModel(componentConfig.getComponentById(engravingId), model.engraving, isUnlocked)

    def fillEntryPoint(self, model):
        dogTag = self.getSelectedDogTag()
        engraving = dogTag.getComponentByType(ComponentViewType.ENGRAVING)
        background = dogTag.getComponentByType(ComponentViewType.BACKGROUND)
        engravingImage = self.getComponentImage(engraving.compId, engraving.grade)
        bgImage = self.getComponentImage(background.compId)
        model.setEngraving(engravingImage)
        model.setBackground(bgImage)
        count = 0
        isEmptyCounter = False
        if self._limitedUIController.isRuleCompleted(LuiRules.DOG_TAG_HINT):
            customizableDogTagsVisited = userSettings.getDogTagsSettings().customizableDogTagsVisited
            count = len(self._dtHelper.getUnseenComps())
            isEmptyCounter = count == 0 and not customizableDogTagsVisited
            if isEmptyCounter:
                count = 1
        model.setCounter(count)
        model.setIsEmptyCounter(isEmptyCounter)
        grades = engraving.componentDefinition.grades
        if engraving and grades and engraving.grade == len(grades) - 1 and engraving.componentDefinition.purpose != ComponentPurpose.COUPLED:
            model.setIsHighlighted(True)
        else:
            model.setIsHighlighted(False)
        model.setIsSelected(self.isDogTagEquipped(dogTag))
        _logger.debug('Dashboard dogtag images - engraving: %s, background: %s', engravingImage, bgImage)

    def getSelectedDogTag(self, clanProfile=None):
        components = userSettings.getDogTagsSettings().selectedCustomizable
        if not components:
            equippedDogTag = self._dtHelper.getDisplayableDT()
            equippedBackground = equippedDogTag.getComponentByType(ComponentViewType.BACKGROUND)
            equippedEngraving = equippedDogTag.getComponentByType(ComponentViewType.ENGRAVING)
            if equippedBackground.componentDefinition.purpose == ComponentPurpose.COUPLED:
                components = [ component.componentId for component in componentConfig.getDefaultDogTag().components ]
            else:
                components = [equippedBackground.compId, equippedEngraving.compId]
        return self._dtHelper.getDisplayableDTForComponents(components, clanProfile)

    def fillGrid(self, viewModel):
        unlockedComponents = self._dtHelper.getUnlockedComps()
        allComponents = self._getVisibleComponents(unlockedComponents)
        gridSectionArray = viewModel.getBackgroundGrid()
        gridSectionArray.clear()
        self._fillSectionArray(gridSectionArray, allComponents, unlockedComponents, SectionType.BACKGROUND)
        gridSectionArray.invalidate()
        gridSectionArray = viewModel.getEngravingGrid()
        gridSectionArray.clear()
        self._fillSectionArray(gridSectionArray, allComponents, unlockedComponents, SectionType.ENGRAVING)
        gridSectionArray.invalidate()

    def updateComponentModel(self, viewModel, compId):
        comp = componentConfig.getComponentById(compId)
        componentModel = self._getCorrespondingCompModel(viewModel, comp)
        self._fillComponentModel(comp, componentModel, comp.componentId in self._dtHelper.getUnlockedComps())

    def isDogTagEquipped(self, dogTag):
        background = dogTag.getComponentByType(ComponentViewType.BACKGROUND).compId
        engraving = dogTag.getComponentByType(ComponentViewType.ENGRAVING).compId
        equippedDogTag = self._dtHelper.getDisplayableDT()
        equippedBackground = equippedDogTag.getComponentByType(ComponentViewType.BACKGROUND).compId
        equippedEngraving = equippedDogTag.getComponentByType(ComponentViewType.ENGRAVING).compId
        return background == equippedBackground and engraving == equippedEngraving

    @staticmethod
    def _getVisibleComponents(unlockedComponents):
        nonDeprecated = {}
        for compId, comp in componentConfig.getAllComponents(SourceData.NON_DEPRECATED_ONLY).iteritems():
            if not comp.isSecret or compId in unlockedComponents:
                nonDeprecated[compId] = comp

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

    def _fillSectionArray(self, section, components, unlockedComponents, sectionType):
        sectionComponents = defaultdict(dict)
        for compId, comp in components.iteritems():
            if comp.viewType not in SECTION_TYPE_BY_COMPONENT_VIEW_TYPE:
                _logger.error('Not supported component viewType "%s"', comp.viewType)
                continue
            if SECTION_TYPE_BY_COMPONENT_VIEW_TYPE[comp.viewType] == sectionType:
                purpose = comp.purpose
                if purpose == ComponentPurpose.SKILL and not self.serverSettings().isSkillComponentsEnabled():
                    continue
                if purpose not in SECTION_BY_PURPOSE:
                    _logger.error('Not supported purpose "%s"', purpose)
                    continue
                sectionName = SECTION_BY_PURPOSE[purpose]
                sectionComponents[sectionName][compId] = comp

        for sectionName in SECTION_ORDER_MAP[sectionType]:
            if not sectionComponents[sectionName]:
                continue
            gridSection = self._createSection(sectionComponents[sectionName], unlockedComponents, self.getPurposeRes(sectionName))
            if sectionName in PURPOSE_TO_TOOLTIP_PURPOSE_GROUP_MAP:
                purposeGroup = PURPOSE_TO_TOOLTIP_PURPOSE_GROUP_MAP[sectionName]
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

    @staticmethod
    def _getSortedKeys(item):
        maxIdx = len(IN_SECTION_ORDER_WEIGHT)
        purpose = item.purpose
        itemOrderIdx = IN_SECTION_ORDER_WEIGHT.index(purpose) if purpose in IN_SECTION_ORDER_WEIGHT else maxIdx
        return (itemOrderIdx, item.componentId)

    def _fillItems(self, components, itemsArray, unlocked):
        for component in sorted(components.values(), key=self._getSortedKeys):
            componentModel = DtComponent()
            self._fillComponentModel(component, componentModel, unlocked)
            itemsArray.addViewModel(componentModel)

    def _fillComponentModel(self, componentDef, model, isUnlocked=True):
        model.setId(componentDef.componentId)
        model.setPurpose(componentDef.purpose.value.lower())
        model.setType(componentDef.viewType.value.lower())
        currProg = self.__getComponentProgress(componentDef)
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
        model.setIsExternalUnlockOnly(componentDef.isExternalUnlockOnly)
        if componentDef.purpose == ComponentPurpose.SKILL and isUnlocked and currProgValue < componentDef.grades[0]:
            model.setIsDemoted(True)

    def __getComponentProgress(self, component):
        return getCoupledDogTagProgress(self._getDossier(), component) if component.purpose == ComponentPurpose.COUPLED else self._dtHelper.getComponentProgress(component.componentId)

    @replace_none_kwargs(itemsCache=IItemsCache)
    def _getDossier(self, itemsCache=None):
        if self.__dossierDescr is None:
            self.__dossierDescr = itemsCache.items.getAccountDossier().getDossierDescr()
        return self.__dossierDescr

    @staticmethod
    def __getUnlockThresholdForGrade(compId, grade):
        if compId not in componentConfig.getAllComponents():
            return NO_PROGRESS
        comp = componentConfig.getComponentById(compId)
        if not comp.grades:
            return NO_PROGRESS
        return NO_PROGRESS if grade >= len(comp.grades) else comp.grades[grade]
