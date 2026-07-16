# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/skill.py
from __future__ import absolute_import
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Optional

class ISkill(object):

    @property
    def name(self):
        raise NotImplementedError

    @property
    def customName(self):
        raise NotImplementedError

    @property
    def crewCustomName(self):
        raise NotImplementedError


class ISkillPresenter(ISkill):

    @property
    def userName(self):
        raise NotImplementedError

    @property
    def description(self):
        raise NotImplementedError

    @property
    def shortDescription(self):
        raise NotImplementedError

    @property
    def maxLvlDescription(self):
        raise NotImplementedError

    @property
    def currentLvlDescription(self):
        raise NotImplementedError

    @property
    def altDescription(self):
        raise NotImplementedError

    @property
    def altInfo(self):
        raise NotImplementedError

    @property
    def icon(self):
        raise NotImplementedError

    @property
    def extensionLessIconName(self):
        raise NotImplementedError

    @property
    def bigIconPath(self):
        raise NotImplementedError


class ISkillData(ISkill):

    @property
    def level(self):
        raise NotImplementedError

    @property
    def roleType(self):
        raise NotImplementedError

    @property
    def typeName(self):
        raise NotImplementedError

    @property
    def isEnable(self):
        raise NotImplementedError

    @property
    def isZero(self):
        raise NotImplementedError

    @property
    def isSituational(self):
        raise NotImplementedError

    @property
    def isLearned(self):
        raise NotImplementedError

    @property
    def isLearnedAsMajor(self):
        raise NotImplementedError

    @property
    def isLearnedAsBonus(self):
        raise NotImplementedError

    @property
    def isMaxLevel(self):
        raise NotImplementedError

    @property
    def isSkillActive(self):
        raise NotImplementedError

    @property
    def isRelevant(self):
        raise NotImplementedError

    @property
    def learnState(self):
        raise NotImplementedError

    @property
    def skillRole(self):
        raise NotImplementedError

    @property
    def tankmanRole(self):
        raise NotImplementedError

    def setIsSkillActive(self, isSkillActive):
        raise NotImplementedError
