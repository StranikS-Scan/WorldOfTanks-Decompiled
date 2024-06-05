# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/dog_tag_composer.py
from dog_tags_common.config.common import ComponentViewType, ComponentPurpose
from dog_tags_common.number_formatter import formatComponentValue
from dog_tags_common.player_dog_tag import DisplayableDogTag
from gui.dog_tag_composer import DogTagComposerClient
from helpers import getLanguageCode
STARTING_GRADE_OFFSET = 1

class DogTagComposerInBattleGF(DogTagComposerClient):

    def fillModel(self, model, dogTag):
        model.setPlayerName(dogTag.getNickName())
        model.setClanTag(dogTag.getClanTag())
        background = dogTag.getComponentByType(ComponentViewType.BACKGROUND)
        model.background.setId(background.compId)
        model.background.setCurrentProgress(background.value)
        model.background.setCurrentGrade(background.grade)
        model.setAnimation(background.componentDefinition.animation)
        engraving = dogTag.getComponentByType(ComponentViewType.ENGRAVING)
        model.engraving.setId(engraving.compId)
        model.engraving.setCurrentProgress(engraving.value)
        model.engraving.setCurrentGrade(engraving.grade)


class DogTagComposerInBattleSF(DogTagComposerClient):

    def getModel(self, dt):
        engraving = dt.getComponentByType(ComponentViewType.ENGRAVING)
        background = dt.getComponentByType(ComponentViewType.BACKGROUND)
        grades = engraving.componentDefinition.grades
        isMaxLevel = grades is not None and engraving.grade + STARTING_GRADE_OFFSET == len(grades)
        return {'background': {'componentID': background.compId,
                        'imageStr': self.getComponentImage(background.compId, 0)},
         'engraving': {'componentID': engraving.compId,
                       'imageStr': self.getComponentImage(engraving.compId, engraving.grade, localized=engraving.componentDefinition.purpose == ComponentPurpose.COUPLED),
                       'name': self.getComponentTitle(engraving.compId),
                       'value': formatComponentValue(getLanguageCode(), engraving.value, engraving.componentDefinition.numberType)},
         'playerName': dt.getNickName(),
         'clanTag': dt.getClanTag(),
         'isEngravingMaxLevel': isMaxLevel,
         'animationSrc': self.getAnimationSrc(engraving.componentDefinition.animation),
         'bottomPlateSrc': self.getBottomPlateImage(background.compId)}

    def getModelFromDict(self, dogTag):
        return self.getModel(DisplayableDogTag.fromDict(dogTag))


layoutComposer = DogTagComposerInBattleSF()
