# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/doc_loaders/surveys_loader.py
from collections import namedtuple, defaultdict
import logging
from gui.mapbox.mapbox_survey_helper import Condition, QuantifierTypes, AlternativeOneManyQuestion, AlternativeQuestion, getQuestionClass
import resource_helper
from soft_exception import SoftException
from shared_utils import findFirst
_logger = logging.getLogger(__name__)
_SURVEYS_XML_PATH = 'gui/surveys.xml'
_SURVEYS = None
_Survey = namedtuple('_Survey', ('surveyGroup', 'surveyId', 'questions'))
_GuiParams = namedtuple('_GuiParams', ('pathPrefix', 'image', 'showIcons', 'useMapId', 'useLinkedParams'))
_AdditionalParam = namedtuple('_AdditionalParam', ('fromQuestion', 'answers', 'options'))
_TextParams = namedtuple('_TextParams', ('param', 'isJoined'))
_Responses = namedtuple('_Responses', ('variants', 'responseGroups'))

def _readCondition(section, isRequired):
    if not section.has_key('condition'):
        return None
    else:
        subSection = section['condition']
        requiredQuestionId = subSection['requiredQuestionId'].asString
        requiredOptionId = subSection.readString('requiredOptionId')
        requiredAnswers = [ answerId for answerId in subSection['requiredAnswers'].asString.split(' ') ]
        if not requiredAnswers:
            raise SoftException('Unfilled required answers for the condition')
        innerSubsection = subSection['requiredAnswers']
        quantifier = QuantifierTypes.SINGLE.value if not innerSubsection.keys() else innerSubsection['quantifier'].asString
        if not QuantifierTypes.hasValue(quantifier):
            raise SoftException('Unsupported condition type for the mapbox survey')
        return Condition(requiredQuestionId, requiredOptionId, requiredAnswers, quantifier, isRequired)


def _readSourceSection(section):
    questionId = None
    answers = None
    options = None
    if section.has_key('useAnswers'):
        questionId, answers = _readSomeSourceSection(section, 'useAnswers')
    elif section.has_key('useOptions'):
        questionId, options = _readSomeSourceSection(section, 'useOptions')
    return _AdditionalParam(questionId, answers, options) if questionId is not None else None


def _readSomeSourceSection(section, sectionName):
    if section.has_key(sectionName):
        answers = section.readString(sectionName).split(' ')
        innerSubsection = section[sectionName]
        if not innerSubsection.has_key('questionID'):
            raise SoftException('Invalid {} section for the mapbox survey'.format(sectionName))
        questionId = innerSubsection['questionID'].asString
        return (questionId, answers)
    else:
        return (None, None)


def _readLinkedParameters(section):
    if not section.has_key('linkedParameters'):
        return None
    else:
        param = _readSourceSection(section['linkedParameters'])
        if param:
            isJoined = section['linkedParameters'].readBool('join')
            return _TextParams(param, isJoined)
        return None


def _readGuiParameters(section):
    return _GuiParams(pathPrefix=section.readString('pathPrefix'), image=section.readString('image'), showIcons=section.readBool('showIcons'), useMapId=section.readBool('useMapId'), useLinkedParams=section.readBool('useLinkedParams'))


def _readOptions(section):
    if not section.has_key('options'):
        return None
    else:
        optionsSection = section['options']
        result = _readSourceSection(optionsSection)
        return result if result is not None else _AdditionalParam(fromQuestion=None, answers=optionsSection.asString.split(' '), options=None)


def _readResponses(section):
    variants = section.readString('responses')
    if section.has_key('responseGroups'):
        groups = [ group.asString.split(' ') for group in section['responseGroups'].values() ]
    else:
        groups = None
    return _Responses(variants.split(' ') if variants else [], groups)


def _readQuestion(surveyGroup, questionSection, questionTypes):
    qId = questionSection['questionId'].asString
    isRequired = questionSection['isRequired'].asBool
    isMultiple = questionSection['isMultiple'].asBool
    condition = _readCondition(questionSection, isRequired)
    guiParameters = _readGuiParameters(questionSection)
    responses = _readResponses(questionSection)
    options = _readOptions(questionSection)
    linkedParameters = _readLinkedParameters(questionSection)
    qType = questionSection['questionType'].asString
    if qType not in questionTypes:
        raise SoftException('Incorrect question type "%s" in the survey settings' % qType)
    clz = getQuestionClass(qType)
    return clz(surveyGroup=surveyGroup, questionId=qId, questionType=qType, isMultiple=isMultiple, isRequired=isRequired, condition=condition, answers=responses, options=options, linkedParameters=linkedParameters, guiParameters=guiParameters)


def _readAlternativeQuestion(surveyGroup, questionSection, questionTypes, qId):
    alternativeQuestions = [ _readQuestion(surveyGroup, variant, questionTypes) for variant in questionSection['alternatives'].values() ]
    isSynchronizedAnswers = questionSection.readBool('synchronizeAnswers')
    clz = AlternativeOneManyQuestion if isSynchronizedAnswers else AlternativeQuestion
    return clz(questionId=qId, alternatives=alternativeQuestions, isSynchronizedAnswers=isSynchronizedAnswers)


def _readSurveys():
    result = defaultdict(list)
    ctx, root = resource_helper.getRoot(_SURVEYS_XML_PATH)
    questionTypes = frozenset(root['questionTypes'].asString.split(' '))
    for _, surveySection in resource_helper.getIterator(ctx, root['surveys']):
        bonusType = surveySection['bonusType'].asInt
        if not bonusType:
            raise SoftException('Incorrect bonusType for a survey')
        surveyGroup = surveySection['surveyGroup'].asString
        if not surveyGroup:
            raise SoftException('Empty survey group')
        surveyId = surveySection['surveyId'].asString
        if not surveyId:
            raise SoftException('Empty survey id')
        questions = []
        for questionSection in surveySection['questions'].values():
            if questionSection.has_key('alternatives'):
                qId = questionSection['questionId'].asString
                question = _readAlternativeQuestion(surveyGroup, questionSection, questionTypes, qId)
            else:
                question = _readQuestion(surveyGroup, questionSection, questionTypes)
            questions.append(question)

        result[bonusType].append(_Survey(surveyGroup, surveyId, questions))

    resource_helper.purgeResource(_SURVEYS_XML_PATH)
    return result


def getSurvey(bonusType, surveyId):
    global _SURVEYS
    if _SURVEYS is None:
        _SURVEYS = _readSurveys()
    surveys = _SURVEYS.get(bonusType, [])
    return findFirst(lambda e: e.surveyId == surveyId, surveys)
