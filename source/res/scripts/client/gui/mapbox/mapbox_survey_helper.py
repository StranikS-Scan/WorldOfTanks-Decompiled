# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/mapbox/mapbox_survey_helper.py
from enum import Enum
import logging
import json
import typing
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.mapbox.map_box_question_model import QuestionType
from gui.shared.utils.functions import replaceHyphenToUnderscore
from helpers import dependency
from skeletons.gui.game_control import IMapboxController
from shared_utils import findFirst, first
_logger = logging.getLogger(__name__)
_STR_PATH = R.strings.mapbox.survey

class QuantifierTypes(Enum):
    SINGLE = 'single'
    MULTIPLE = 'multiple'

    @classmethod
    def hasValue(cls, value):
        return value in cls._value2member_map_


class Condition(object):
    __slots__ = ('__requiredQuestionId', '__requiredAnswers', '__requiredOptionId', '__quantifier', '__isRequiredAnswer')
    __mapboxCtrl = dependency.descriptor(IMapboxController)

    def __init__(self, requiredQuestionId, requiredOptionId, requiredAnswers, quantifier, isRequired=False):
        self.__requiredQuestionId = requiredQuestionId
        self.__requiredOptionId = requiredOptionId
        self.__requiredAnswers = requiredAnswers
        self.__quantifier = quantifier
        self.__isRequiredAnswer = isRequired

    def isValid(self):
        surveyManager = self.__mapboxCtrl.surveyManager
        selectedAnswers = surveyManager.getSelectedAnswers(self.__requiredQuestionId, self.__requiredOptionId)
        if not selectedAnswers and self.__isRequiredAnswer:
            return False
        return len(selectedAnswers) > 1 and set(selectedAnswers).issubset(set(self.__requiredAnswers)) if self.__quantifier == QuantifierTypes.MULTIPLE.value else len(set(selectedAnswers).intersection(set(self.__requiredAnswers))) == 1

    def clear(self):
        self.__requiredAnswers = []


class IQuestion(object):

    def getQuestionId(self):
        raise NotImplementedError

    def getQuestionType(self):
        raise NotImplementedError

    def isRequired(self):
        pass

    def isReadyToShow(self):
        raise NotImplementedError

    def getLinkedQuestionId(self):
        pass

    def getOptions(self):
        pass

    def isMultipleChoice(self):
        pass

    def isSyncronizedAnswers(self):
        pass

    def synchronizeAnswers(self, *args, **kwargs):
        pass

    def clear(self):
        pass

    def convertAnswers(self, answers, optionId):
        pass

    def validateAnswers(self, answers, previousAnswers):
        pass


class Question(IQuestion):
    __slots__ = ('__surveyGroup', '__questionId', '__isMultiple', '__isRequired', '__condition', '__answers', '__guiParameters', '__linkedParameters')
    _mapboxCtrl = dependency.descriptor(IMapboxController)

    def __init__(self, *args, **kwargs):
        self.__surveyGroup = kwargs.get('surveyGroup')
        self.__questionId = kwargs.get('questionId')
        self.__isRequired = kwargs.get('isRequired', False)
        self.__isMultiple = kwargs.get('isMultiple', False)
        self.__condition = kwargs.get('condition')
        self.__answers = kwargs.get('answers')
        self.__guiParameters = kwargs.get('guiParameters')
        self.__linkedParameters = kwargs.get('linkedParameters')

    def getQuestionId(self):
        return self.__questionId

    def isRequired(self):
        return self.__isRequired

    def isMultipleChoice(self):
        return self.__isMultiple

    def isUsingIcons(self):
        return self.__guiParameters.showIcons if self.__guiParameters is not None else False

    def isReadyToShow(self):
        return self.__condition is None or self.__condition.isValid()

    def getImage(self):
        if self.__guiParameters.useMapId:
            return '%s_%s' % (self.__guiParameters.image, self._mapboxCtrl.surveyManager.getMapId())
        else:
            if self.__guiParameters.useLinkedParams:
                sourceQuestionId = self.getLinkedQuestionId()
                if sourceQuestionId:
                    choice = first(self._mapboxCtrl.surveyManager.getSelectedAnswers(sourceQuestionId))
                    return '%s_%s' % (self.__guiParameters.image, replaceHyphenToUnderscore(choice))
            return self.__guiParameters.image if self.__guiParameters is not None else ''

    def getTitleParameters(self):
        if self.__linkedParameters is None or not self.__linkedParameters.param:
            return []
        else:
            param = self.__linkedParameters.param
            sourceQuestionId = param.fromQuestion
            pathPrefix = self._mapboxCtrl.surveyManager.getQuestion(sourceQuestionId).getPathPrefix()
            if param.answers is not None:
                strPath = _STR_PATH.dyn(self.__surveyGroup).response
                sources = [ answer for answer in param.answers if answer in self._mapboxCtrl.surveyManager.getSelectedAnswers(sourceQuestionId) ]
            else:
                strPath = _STR_PATH.dyn(self.__surveyGroup).question.option
                sources = [ option for option in param.options ]
            itemsResIds = [ strPath.dyn('_'.join((pathPrefix, replaceHyphenToUnderscore(source))))() for source in sources ]
            items = [ backport.text(resId) for resId in itemsResIds if resId != R.invalid() ]
            return [backport.text(_STR_PATH.listSeparator()).join(items)] if items and self.__linkedParameters.isJoined else items

    def getPathPrefix(self):
        return self.__guiParameters.pathPrefix

    def getLinkedQuestionId(self):
        return self.__linkedParameters.param.fromQuestion if self.__linkedParameters else None

    def getAnswers(self):
        return self.__answers.variants if self.__answers is not None else []

    def convertAnswers(self, answers, optionId):
        if len(answers) > 1:
            _logger.error('Incorrect answers for the question with questionId=%s', self.__questionId)
            return []
        return answers[0].get('choices', []) if answers else []

    def validateAnswers(self, answers, oldAnswers):
        groupsAnswers = self.__answers.responseGroups if self.__answers is not None else None
        if groupsAnswers is None:
            return answers
        else:
            newChoices = first(answers, {}).get('choices', [])
            if any([ set(newChoices).issubset(group) for group in groupsAnswers ]):
                return answers
            newChoice = set(newChoices) - set(first(oldAnswers, {}).get('choices', []))
            requiredGroup = findFirst(lambda group: newChoice.issubset(set(group)), groupsAnswers, [])
            answers[0]['choices'] = set(requiredGroup).intersection(newChoices)
            return answers

    def clear(self):
        if self.__condition is not None:
            self.__condition.clear()
            self.__condition = None
        self.__guiParameters = None
        self.__linkedParameters = None
        self.__answers = None
        return


class _TableQuestion(Question):
    __slots__ = ('__options',)

    def __init__(self, *args, **kwargs):
        super(_TableQuestion, self).__init__(*args, **kwargs)
        self.__options = kwargs.get('options')

    def getQuestionType(self):
        return QuestionType.TABLE

    def convertAnswers(self, answers, optionId):
        answer = findFirst(lambda answer: answer.get('optionId') == optionId, answers)
        return answer.get('choices', []) if answer is not None else []

    def getOptions(self):
        if self.__options is None:
            return []
        elif self.__options.fromQuestion is None:
            return self.__options.answers
        else:
            return [ option for option in self.__options.answers if option in self._mapboxCtrl.surveyManager.getSelectedAnswers(self.__options.fromQuestion) ]

    def validateAnswers(self, answers, oldAnswers):
        _logger.debug('Unsupported operation for a table question')
        return answers

    def clear(self):
        self.__options = None
        super(_TableQuestion, self).clear()
        return


class _InteractiveMapQuestion(Question):
    __slots__ = ()

    def getQuestionType(self):
        return QuestionType.INTERACTIVE_MAP

    def convertAnswers(self, answers, optionId):
        if not answers:
            return []
        choices = answers[0].get('choices', [])
        return [ json.dumps(item) for item in choices ]

    def validateAnswers(self, answers, oldAnswers):
        _logger.debug('Unsupported operation for a question with the interactive map')
        return answers


class _VehicleQuestion(Question):
    __slots__ = ()

    def getQuestionType(self):
        return QuestionType.VEHICLE

    def convertAnswers(self, answers, optionId):
        return first(answers, {}).get('choices', []) if answers else []


class _ImageQuestion(Question):
    __slots__ = ()

    def getQuestionType(self):
        return QuestionType.IMAGE


class _MulptipleChoiceQuestion(Question):
    __slots__ = ()

    def getQuestionType(self):
        return QuestionType.MULTIPLE_CHOICE


class _TextQuestion(Question):
    __slots__ = ()

    def getQuestionType(self):
        return QuestionType.TEXT

    def validateAnswers(self, answers, oldAnswers):
        _logger.debug('Unsupported operation for a text question')
        return answers


class AlternativeQuestion(IQuestion):
    __slots__ = ('__questionId', '_alternatives', '__isSynchronizedAnswers')

    def __init__(self, *args, **kwargs):
        self.__questionId = kwargs.get('questionId', None)
        self._alternatives = kwargs.get('alternatives', [])
        self.__isSynchronizedAnswers = kwargs.get('isSynchronizedAnswers', False)
        return

    def getQuestionType(self):
        return QuestionType.ALTERNATIVE

    def getQuestionId(self):
        return self.__questionId

    def isSyncronizedAnswers(self):
        return self.__isSynchronizedAnswers

    def selectAlternative(self):
        question = findFirst(lambda q: q.isReadyToShow(), self._alternatives)
        return question

    def getAlternative(self, questionId):
        return findFirst(lambda q: q.getQuestionId() == questionId, self._alternatives)

    def getLinkedQuestionId(self):
        for q in self._alternatives:
            if q.getLinkedQuestionId():
                return q.getLinkedQuestionId()

        return None

    def getAlternatives(self):
        return self._alternatives

    def isReadyToShow(self):
        return any((q.isReadyToShow() for q in self._alternatives))

    def clear(self):
        for question in self._alternatives:
            question.clear()

        self._alternatives = []


class AlternativeOneManyQuestion(AlternativeQuestion):
    __slots__ = ()
    __CHOICES_IN_SIMPLE_QUESTION = 1
    __MIN_CHOICES_IN_TABLE_QUESTION = 2

    def synchronizeAnswers(self, surveyData, altQuestion, newAnswers):
        choices = set([ choice for answer in newAnswers for choice in answer.get('choices', []) ])
        simpleQuestion = findFirst(lambda q: q.getQuestionType() == QuestionType.IMAGE, self._alternatives)
        tableQuestion = findFirst(lambda q: q.getQuestionType() == QuestionType.TABLE, self._alternatives)
        if simpleQuestion is None or tableQuestion is None:
            _logger.error('Invalid alternatives for the question')
            return
        else:
            tableQuestId = tableQuestion.getQuestionId()
            simpleQuestId = simpleQuestion.getQuestionId()
            if len(choices) == self.__CHOICES_IN_SIMPLE_QUESTION:
                self.__moveCommonAnswers(tableQuestId, simpleQuestId, surveyData, choices)
            elif len(choices) == self.__MIN_CHOICES_IN_TABLE_QUESTION and surveyData.get(simpleQuestId, []):
                self.__moveCommonAnswers(simpleQuestId, tableQuestId, surveyData, choices)
            else:
                leftAnswers = self.__findSavedAnswers(tableQuestId, surveyData, choices)
                self.__updateAnswers(tableQuestId, surveyData, leftAnswers)
            return

    def __moveCommonAnswers(self, qId1, qId2, surveyData, choices):
        leftAnswers = self.__findSavedAnswers(qId1, surveyData, choices)
        self.__updateAnswers(qId2, surveyData, leftAnswers)
        surveyData.pop(qId1, None)
        return

    @staticmethod
    def __updateAnswers(qId, surveyData, leftAnswers):
        if leftAnswers:
            surveyData[qId] = leftAnswers
        else:
            surveyData.pop(qId, None)
        return

    @staticmethod
    def __findSavedAnswers(qId, surveyData, choices):
        return [ answer for answer in surveyData.get(qId, []) if answer.get('optionId') in choices ]


_SUPPORTED_QUESTION_TYPES = {QuestionType.IMAGE.value: _ImageQuestion,
 QuestionType.VEHICLE.value: _VehicleQuestion,
 QuestionType.TABLE.value: _TableQuestion,
 QuestionType.INTERACTIVE_MAP.value: _InteractiveMapQuestion,
 QuestionType.TEXT.value: _TextQuestion,
 QuestionType.MULTIPLE_CHOICE.value: _MulptipleChoiceQuestion,
 QuestionType.ALTERNATIVE.value: AlternativeQuestion}

def getQuestionClass(questionType):
    return _SUPPORTED_QUESTION_TYPES.get(questionType)
