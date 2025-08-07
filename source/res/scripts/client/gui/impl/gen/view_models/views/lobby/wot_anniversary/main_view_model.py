# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wot_anniversary/main_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.wot_anniversary.album_card_view_model import AlbumCardViewModel
from gui.impl.gen.view_models.views.lobby.wot_anniversary.event_model import EventModel
from gui.impl.gen.view_models.views.lobby.wot_anniversary.media_resource_model import MediaResourceModel
from gui.impl.gen.view_models.views.lobby.wot_anniversary.progression_step_model import ProgressionStepModel
from gui.impl.gen.view_models.views.lobby.wot_anniversary.slot_model import SlotModel
from gui.impl.gen.view_models.views.lobby.wot_anniversary.videos_resource_model import VideosResourceModel

class MainViewModel(ViewModel):
    __slots__ = ('onClose', 'onOpenInfoPage', 'onOpenCardPreview', 'onOpenEnvelope', 'onOpenRewardScreen', 'onSetAnimationDisabled', 'onSecondPageOpened')

    def __init__(self, properties=15, commands=7):
        super(MainViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def firstFilledOverlay(self):
        return self._getViewModel(0)

    @staticmethod
    def getFirstFilledOverlayType():
        return MediaResourceModel

    @property
    def secondFilledOverlay(self):
        return self._getViewModel(1)

    @staticmethod
    def getSecondFilledOverlayType():
        return MediaResourceModel

    @property
    def event(self):
        return self._getViewModel(2)

    @staticmethod
    def getEventType():
        return EventModel

    @property
    def videos(self):
        return self._getViewModel(3)

    @staticmethod
    def getVideosType():
        return VideosResourceModel

    @property
    def envelopeCard(self):
        return self._getViewModel(4)

    @staticmethod
    def getEnvelopeCardType():
        return AlbumCardViewModel

    def getStartDate(self):
        return self._getNumber(5)

    def setStartDate(self, value):
        self._setNumber(5, value)

    def getEndDate(self):
        return self._getNumber(6)

    def setEndDate(self, value):
        self._setNumber(6, value)

    def getBlur(self):
        return self._getBool(7)

    def setBlur(self, value):
        self._setBool(7, value)

    def getEnvelopeCardOpened(self):
        return self._getBool(8)

    def setEnvelopeCardOpened(self, value):
        self._setBool(8, value)

    def getInteractionBlock(self):
        return self._getBool(9)

    def setInteractionBlock(self, value):
        self._setBool(9, value)

    def getEnvelopeOpening(self):
        return self._getBool(10)

    def setEnvelopeOpening(self, value):
        self._setBool(10, value)

    def getAnimationDisabled(self):
        return self._getBool(11)

    def setAnimationDisabled(self, value):
        self._setBool(11, value)

    def getResourceLoading(self):
        return self._getBool(12)

    def setResourceLoading(self, value):
        self._setBool(12, value)

    def getSlots(self):
        return self._getArray(13)

    def setSlots(self, value):
        self._setArray(13, value)

    @staticmethod
    def getSlotsType():
        return SlotModel

    def getProgressionSteps(self):
        return self._getArray(14)

    def setProgressionSteps(self, value):
        self._setArray(14, value)

    @staticmethod
    def getProgressionStepsType():
        return ProgressionStepModel

    def _initialize(self):
        super(MainViewModel, self)._initialize()
        self._addViewModelProperty('firstFilledOverlay', MediaResourceModel())
        self._addViewModelProperty('secondFilledOverlay', MediaResourceModel())
        self._addViewModelProperty('event', EventModel())
        self._addViewModelProperty('videos', VideosResourceModel())
        self._addViewModelProperty('envelopeCard', AlbumCardViewModel())
        self._addNumberProperty('startDate', 0)
        self._addNumberProperty('endDate', 0)
        self._addBoolProperty('blur', False)
        self._addBoolProperty('envelopeCardOpened', False)
        self._addBoolProperty('interactionBlock', False)
        self._addBoolProperty('envelopeOpening', False)
        self._addBoolProperty('animationDisabled', False)
        self._addBoolProperty('resourceLoading', False)
        self._addArrayProperty('slots', Array())
        self._addArrayProperty('progressionSteps', Array())
        self.onClose = self._addCommand('onClose')
        self.onOpenInfoPage = self._addCommand('onOpenInfoPage')
        self.onOpenCardPreview = self._addCommand('onOpenCardPreview')
        self.onOpenEnvelope = self._addCommand('onOpenEnvelope')
        self.onOpenRewardScreen = self._addCommand('onOpenRewardScreen')
        self.onSetAnimationDisabled = self._addCommand('onSetAnimationDisabled')
        self.onSecondPageOpened = self._addCommand('onSecondPageOpened')
