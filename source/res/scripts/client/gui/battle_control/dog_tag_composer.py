# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/dog_tag_composer.py
from dog_tags_common.config.common import ComponentViewType
from dog_tags_common.number_formatter import formatComponentValue
from dog_tags_common.player_dog_tag import DisplayableDogTag
from gui.dog_tag_composer import DogTagComposerClient
from helpers import getLanguageCode
STARTING_GRADE_OFFSET = 1

class DogTagComposerInBattle(DogTagComposerClient):

    def getModel(self, dt):
        engraving = dt.getComponentByType(ComponentViewType.ENGRAVING)
        background = dt.getComponentByType(ComponentViewType.BACKGROUND)
        isMaxLevel = engraving.grade + STARTING_GRADE_OFFSET == len(engraving.componentDefinition.grades)
        return {'background': {'imageStr': self.getComponentImage(background.compId, 0)},
         'engraving': {'imageStr': self.getComponentImage(engraving.compId, engraving.grade),
                       'name': self.getComponentTitle(engraving.compId),
                       'value': formatComponentValue(getLanguageCode(), engraving.value, engraving.componentDefinition.numberType)},
         'playerName': self._formatName(dt.getNickName()),
         'clanTag': dt.getClanTag(),
         'isEngravingMaxLevel': isMaxLevel}

    def getModelFromDict(self, dogTag):
        return self.getModel(DisplayableDogTag.fromDict(dogTag))


layoutComposer = DogTagComposerInBattle()
