# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/mapbox/mapbox_survey_view.py
import json
import typing
from constants import Configs
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer, Array
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.mapbox.map_box_survey_view_model import MapBoxSurveyViewModel
from gui.impl.gen.view_models.views.lobby.mapbox.map_box_option_model import MapBoxOptionModel
from gui.impl.gen.view_models.views.lobby.mapbox.map_box_question_model import QuestionType
from gui.impl.lobby.mapbox.sound import getMapboxViewSoundSpace
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from helpers import dependency, server_settings, unicodeToStr
from skeletons.gui.game_control import IMapboxController
from skeletons.gui.lobby_context import ILobbyContext
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.mapbox.map_box_question_model import MapBoxQuestionModel
    from gui.impl.gen.view_models.views.lobby.mapbox.map_box_answers_model import MapBoxAnswersModel
    from gui.mapbox.mapbox_survey_helper import Question

class MapBoxSurvey(ViewImpl):
    __slots__ = ('__mapName', '__closeCallback')
    _COMMON_SOUND_SPACE = getMapboxViewSoundSpace()
    __mapboxCtrl = dependency.descriptor(IMapboxController)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, mapName, closeCallback):
        settings = ViewSettings(R.views.lobby.mapbox.MapBoxSurveyView(), model=MapBoxSurveyViewModel())
        self.__mapName = mapName
        self.__closeCallback = closeCallback
        super(MapBoxSurvey, self).__init__(settings)

    @property
    def viewModel(self):
        return super(MapBoxSurvey, self).getViewModel()

    def _initialize(self):
        super(MapBoxSurvey, self)._initialize()
        self.__addListeners()

    def _finalize(self):
        self.__mapboxCtrl.surveyManager.clearSurvey()
        self.__removeListeners()
        super(MapBoxSurvey, self)._finalize()

    def _onLoading(self, *args, **kwargs):
        surveyManager = self.__mapboxCtrl.surveyManager
        surveyManager.startSurvey(self.__mapName)
        question = surveyManager.getQuestion()
        self.__updateViewModel(question)

    @server_settings.serverSettingsChangeListener(Configs.MAPBOX_CONFIG.value)
    def __onServerSettingsChanged(self, _):
        if not self.__mapboxCtrl.getModeSettings().isEnabled:
            self.destroyWindow()

    def __addListeners(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        self.viewModel.onClose += self.__onClose
        self.viewModel.onShowPreviousPage += self.__onShowPreviousPage
        self.viewModel.onShowNextPage += self.__onShowNextPage
        self.viewModel.onAnswerQuestion += self.__onAnswerQuestion
        self.viewModel.onReady += self.__onConfirmCompletion

    def __removeListeners(self):
        self.viewModel.onClose -= self.__onClose
        self.viewModel.onShowPreviousPage -= self.__onShowPreviousPage
        self.viewModel.onShowNextPage -= self.__onShowNextPage
        self.viewModel.onAnswerQuestion -= self.__onAnswerQuestion
        self.viewModel.onReady -= self.__onConfirmCompletion
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged

    def __updateViewModel(self, question):
        if question is None:
            raise SoftException('There is an invalid question for the mapbox survey')
        surveyManager = self.__mapboxCtrl.surveyManager
        with self.getViewModel().transaction() as model:
            model.setMapId(surveyManager.getMapId())
            model.setCurrentPage(surveyManager.getCurrentQuestionIdx())
            model.setTotalPagesCount(surveyManager.getTotalQuestionsCount())
            model.setCanContinue(surveyManager.canContinue())
            self.__fillQuestionModel(model.question, question)
        return

    def __fillQuestionModel(self, model, question):
        model.setType(question.getQuestionType())
        model.setImagePath(question.getImage())
        model.setQuestionId(question.getQuestionId())
        model.setShowIcons(question.isUsingIcons())
        self.__fillTitleParameters(model, question)
        self.__fillAnswers(model.answers, question)
        self.__fillOptions(model.options, question)

    def __fillAnswers(self, model, question, optionId=None):
        model.setIsMultipleChoice(question.isMultipleChoice())
        variants = model.getVariants()
        variants.clear()
        for answer in question.getAnswers():
            variants.addString(answer)

        variants.invalidate()
        self.__updateSelectedVariants(model, question.getQuestionId(), optionId)

    def __fillOptions(self, model, question):
        model.clearItems()
        if question.getQuestionType() == QuestionType.TABLE:
            for optionId in question.getOptions():
                optionModel = MapBoxOptionModel()
                optionModel.setOptionId(optionId)
                self.__fillAnswers(optionModel.answers, question, optionId)
                model.addViewModel(optionModel)

        model.invalidate()

    def __fillTitleParameters(self, model, question):
        titleParameters = model.getTitleParams()
        titleParameters.clear()
        for parameter in question.getTitleParameters():
            titleParameters.addResource(parameter)

        titleParameters.invalidate()

    def __updateSelectedVariants(self, model, questionId, optionId=None):
        selectedVariants = model.getSelectedVariants()
        selectedVariants.clear()
        for answer in self.__mapboxCtrl.surveyManager.getSelectedAnswers(questionId, optionId):
            selectedVariants.addString(answer)

        selectedVariants.invalidate()

    def __onConfirmCompletion(self):
        self.__onClose()

    def __onClose(self):
        self.destroyWindow()
        if self.__closeCallback is not None:
            self.__closeCallback()
        return

    def __onShowPreviousPage(self):
        question = self.__mapboxCtrl.surveyManager.getPreviousQuestion()
        if question is None:
            return
        else:
            self.__updateViewModel(question)
            return

    def __onShowNextPage(self):
        surveyManager = self.__mapboxCtrl.surveyManager
        if not surveyManager.canContinue():
            return
        else:
            question = surveyManager.getNextQuestion()
            if question is None:
                surveyData = surveyManager.getSurveyData()
                self.__mapboxCtrl.handleSurveyCompleted(surveyData)
                self.__setFinalScreen()
            else:
                self.__updateViewModel(question)
            return

    def __onAnswerQuestion(self, args):
        data = unicodeToStr(json.loads(args['answer']))
        qId = data.get('questionId', '')
        answers = data.get('answers', [])
        surveyManager = self.__mapboxCtrl.surveyManager
        if answers:
            surveyManager.saveAnswers(qId, answers)
        with self.getViewModel().transaction() as model:
            model.setCanContinue(surveyManager.canContinue())
            question = surveyManager.getQuestion(qId)
            if question.getQuestionType() == QuestionType.TABLE:
                for optionModel in model.question.options.getItems():
                    optionId = optionModel.getOptionId()
                    self.__updateSelectedVariants(optionModel.answers, qId, optionId)

                model.question.options.invalidate()
            else:
                self.__updateSelectedVariants(model.question.answers, qId)

    def __setFinalScreen(self):
        surveyManager = self.__mapboxCtrl.surveyManager
        with self.getViewModel().transaction() as model:
            model.setMapId(surveyManager.getMapId())
            totalQuestions = surveyManager.getTotalQuestionsCount()
            model.setTotalPagesCount(totalQuestions)
            model.setCurrentPage(totalQuestions)
            model.setIsSurveyFinish(True)
            model.question.setQuestionId('')
            model.question.setType(QuestionType.UNDEFINED)


class MapBoxSurveyWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, mapName, closeCallback=None):
        super(MapBoxSurveyWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=MapBoxSurvey(mapName, closeCallback), layer=WindowLayer.OVERLAY)
