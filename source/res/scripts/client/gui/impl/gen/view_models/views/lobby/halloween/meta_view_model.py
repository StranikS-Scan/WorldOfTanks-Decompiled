# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/halloween/meta_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.halloween.meta_interrogation_model import MetaInterrogationModel
from gui.impl.gen.view_models.views.lobby.halloween.timeline_view_model import TimelineViewModel

class PageTypeEnum(Enum):
    TASKS = 'task'
    VIDEO = 'video'
    FINAL_VIDEO = 'finalVideo'
    PROGRESS = 'progress'
    MEMORIES = 'memories'
    FINAL_REWARD = 'finalReward'


class MetaViewModel(ViewModel):
    __slots__ = ('onClose', 'onTankPreview', 'onShowInfoPage', 'onDecodeVideo', 'onPlayVideo', 'onSkipTasks')
    PRICE_TOOLTIP_ID = 'eventMetaPriceTooltipID'
    INTERROGATION_TOOLTIP_ID = 'eventMetaInterrogationTooltipID'
    INTERROGATION_DONE_TOOLTIP_ID = 'eventMetaInterrogationDoneTooltipID'
    FINAL_INTERROGATION_TOOLTIP_ID = 'eventMetaFinalInterrogationTooltipID'
    INTRO_VIDEO_ITEM_ID = -1

    def __init__(self, properties=6, commands=6):
        super(MetaViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def interrogation(self):
        return self._getViewModel(0)

    @property
    def timeline(self):
        return self._getViewModel(1)

    def getPageType(self):
        return PageTypeEnum(self._getString(2))

    def setPageType(self, value):
        self._setString(2, value.value)

    def getPrevUnlocked(self):
        return self._getNumber(3)

    def setPrevUnlocked(self, value):
        self._setNumber(3, value)

    def getCurrentUnlocked(self):
        return self._getNumber(4)

    def setCurrentUnlocked(self, value):
        self._setNumber(4, value)

    def getTotal(self):
        return self._getNumber(5)

    def setTotal(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(MetaViewModel, self)._initialize()
        self._addViewModelProperty('interrogation', MetaInterrogationModel())
        self._addViewModelProperty('timeline', TimelineViewModel())
        self._addStringProperty('pageType')
        self._addNumberProperty('prevUnlocked', 0)
        self._addNumberProperty('currentUnlocked', 0)
        self._addNumberProperty('total', 0)
        self.onClose = self._addCommand('onClose')
        self.onTankPreview = self._addCommand('onTankPreview')
        self.onShowInfoPage = self._addCommand('onShowInfoPage')
        self.onDecodeVideo = self._addCommand('onDecodeVideo')
        self.onPlayVideo = self._addCommand('onPlayVideo')
        self.onSkipTasks = self._addCommand('onSkipTasks')
