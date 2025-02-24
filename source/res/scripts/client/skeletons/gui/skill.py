# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/skill.py
from abc import ABCMeta, abstractproperty, abstractmethod
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Optional

class ISkill:
    __metaclass__ = ABCMeta

    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def customName(self):
        pass

    @abstractmethod
    def crewCustomName(self):
        pass


class ISkillPresenter(ISkill):
    __metaclass__ = ABCMeta

    @abstractmethod
    def userName(self):
        pass

    @abstractmethod
    def description(self):
        pass

    @abstractmethod
    def shortDescription(self):
        pass

    @abstractmethod
    def maxLvlDescription(self):
        pass

    @abstractmethod
    def currentLvlDescription(self):
        pass

    @abstractmethod
    def altDescription(self):
        pass

    @abstractmethod
    def altInfo(self):
        pass

    @abstractmethod
    def icon(self):
        pass

    @abstractmethod
    def extensionLessIconName(self):
        pass

    @abstractmethod
    def bigIconPath(self):
        pass


class ISkillData(ISkill):
    __metaclass__ = ABCMeta

    @abstractproperty
    def level(self):
        pass

    @abstractproperty
    def roleType(self):
        pass

    @abstractproperty
    def typeName(self):
        pass

    @abstractproperty
    def isEnable(self):
        pass

    @abstractproperty
    def isZero(self):
        pass

    @abstractproperty
    def isSituational(self):
        pass

    @abstractproperty
    def isLearned(self):
        pass

    @abstractproperty
    def isLearnedAsMajor(self):
        pass

    @abstractproperty
    def isLearnedAsBonus(self):
        pass

    @abstractproperty
    def isMaxLevel(self):
        pass

    @abstractproperty
    def isSkillActive(self):
        pass

    @abstractproperty
    def isRelevant(self):
        pass

    @abstractproperty
    def learnState(self):
        pass

    @abstractproperty
    def skillRole(self):
        pass

    @abstractproperty
    def tankmanRole(self):
        pass

    @abstractmethod
    def setIsSkillActive(self, isSkillActive):
        pass
