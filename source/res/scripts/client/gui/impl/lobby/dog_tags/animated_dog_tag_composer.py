# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/dog_tags/animated_dog_tag_composer.py
import logging
from collections import defaultdict
import typing
from dog_tags_common.components_config import componentConfigAdapter as componentConfig
from advanced_achievements_client.getters import getAchievementByID
from dog_tags_common.config.common import ComponentViewType, ComponentPurpose
from gui.impl.gen.view_models.views.lobby.dog_tags.animated_dog_tag_component import AnimatedDogTagComponent
from gui.impl.lobby.achievements.profile_utils import fillAdvancedAchievementModel
from gui.impl.lobby.dog_tags.dog_tag_composer import DogTagComposerLobby
from gui.limited_ui.lui_rules_storage import LUI_RULES
from gui.server_events import settings as userSettings
if typing.TYPE_CHECKING:
    from typing import Iterable
    from dog_tags_common.components_config import DictIterator
    from dog_tags_common.player_dog_tag import DisplayableDogTag
    from frameworks.wulf import Array
    from gui.clans.clan_account_profile import ClanAccountProfile
    from gui.impl.gen.view_models.views.lobby.dog_tags.animated_dog_tags_view_model import AnimatedDogTagsViewModel
    from gui.impl.gen.view_models.views.lobby.account_dashboard.dog_tag_model import DogTagModel
    from gui.impl.gen.view_models.views.lobby.achievements.advanced_achievement_model import AdvancedAchievementModel
_logger = logging.getLogger(__name__)

class AnimatedDogTagComposer(DogTagComposerLobby):

    def fillModel(self, model, dogtag, isUnlocked=True):
        super(AnimatedDogTagComposer, self).fillModel(model, dogtag, isUnlocked)
        model.setAnimation(dogtag.getComponentByType(ComponentViewType.BACKGROUND).componentDefinition.animation)
        model.setIsShowInPrebattle(dogtag.getComponentByType(ComponentViewType.BACKGROUND).componentDefinition.isShowInPrebattle)
        model.setIsSelected(self.isDogTagEquipped(dogtag))

    def fillEntryPoint(self, model):
        super(AnimatedDogTagComposer, self).fillEntryPoint(model)
        dogTag = self.getSelectedDogTag()
        engraving = dogTag.getComponentByType(ComponentViewType.ENGRAVING)
        model.setEngraving(self.getComponentImage(engraving.compId, localized=True))
        counter = 0
        isEmptyCounter = False
        if self._limitedUIController.isRuleCompleted(LUI_RULES.DogTagHangarHint):
            counter = len(self._dtHelper.getUnseenCoupledComps()) / 2
            animatedDogTagsVisited = userSettings.getDogTagsSettings().animatedDogTagsVisited
            isEmptyCounter = counter == 0 and not animatedDogTagsVisited
            if isEmptyCounter:
                counter = 1
        model.setIsEmptyCounter(isEmptyCounter)
        model.setCounter(counter)

    def fillAnimatedDogTags(self, viewModel, backgroundId=0, engravingId=0):
        unlockedComponents = self._dtHelper.getUnlockedComps()
        allComponents = self._getVisibleComponents(unlockedComponents)
        dogTags = viewModel.getDogTags()
        dogTags.clear()
        self._fillItemsArray(dogTags, allComponents, unlockedComponents)
        dogTags.invalidate()
        viewModel.setInitialIndex(self.getInitialIndex(dogTags, backgroundId, engravingId))

    def getSelectedDogTag(self, clanProfile=None):
        components = userSettings.getDogTagsSettings().selectedAnimated
        if not components:
            equippedDogTag = self._dtHelper.getDisplayableDT()
            equippedBackground = equippedDogTag.getComponentByType(ComponentViewType.BACKGROUND)
            equippedEngraving = equippedDogTag.getComponentByType(ComponentViewType.ENGRAVING)
            if equippedBackground.componentDefinition.purpose == ComponentPurpose.COUPLED:
                components = [equippedBackground.compId, equippedEngraving.compId]
            else:
                components = componentConfig.getDefaultAnimatedDogTag()
        return self._dtHelper.getDisplayableDTForComponents(components, clanProfile)

    def getInitialIndex(self, itemsArray, backgroundId, engravingId):
        for index, value in enumerate(itemsArray):
            if value.background.getId() == backgroundId and value.engraving.getId() == engravingId:
                return index

    def fillRequiredAchievement(self, model, unlockKey):
        achievementCategory, achievementId, achievementStage = unlockKey
        achievement = getAchievementByID(int(achievementId), achievementCategory)
        fillAdvancedAchievementModel(achievement, model)
        model.setStage(int(achievementStage))

    def _fillItemsArray(self, itemsArray, components, unlockedIds):
        componentsCouples = defaultdict(dict)
        for comp in components.itervalues():
            purpose = comp.purpose
            if purpose != ComponentPurpose.COUPLED:
                continue
            if comp.viewType == ComponentViewType.BACKGROUND:
                componentsCouples[comp.componentId][ComponentViewType.BACKGROUND] = comp
            componentsCouples[comp.coupledComponentId][ComponentViewType.ENGRAVING] = comp

        for couple in [ componentsCouples[key] for key in sorted(componentsCouples.iterkeys()) ]:
            backgroundId = couple[ComponentViewType.BACKGROUND].componentId
            engravingId = couple[ComponentViewType.ENGRAVING].componentId
            isUnlocked = backgroundId in unlockedIds and engravingId in unlockedIds
            displayableDogTag = self._dtHelper.getDisplayableDTForComponents([backgroundId, engravingId])
            dogTagModel = AnimatedDogTagComponent()
            self.fillModel(dogTagModel, displayableDogTag, isUnlocked)
            unlockKey = couple[ComponentViewType.ENGRAVING].unlockKey
            self.fillRequiredAchievement(dogTagModel.requiredAchievement, unlockKey)
            itemsArray.addViewModel(dogTagModel)
