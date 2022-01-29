# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lunar_ny/main_view/main_view_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.lunar_ny.bonuses_model import BonusesModel
from gui.impl.gen.view_models.views.lobby.lunar_ny.fill_envelope_view_model import FillEnvelopeViewModel
from gui.impl.gen.view_models.views.lobby.lunar_ny.main_view.album.album_model import AlbumModel
from gui.impl.gen.view_models.views.lobby.lunar_ny.main_view.info.info_model import InfoModel
from gui.impl.gen.view_models.views.lobby.lunar_ny.main_view.send_envelopes.send_envelopes_model import SendEnvelopesModel
from gui.impl.gen.view_models.views.lobby.lunar_ny.main_view.store_envelopes.store_envelopes_model import StoreEnvelopesModel

class Tab(IntEnum):
    SENDENVELOPES = 0
    ALBUM = 1
    STOREENVELOPES = 2
    INFO = 3


class MainViewModel(ViewModel):
    __slots__ = ('onViewedTab', 'onClose')

    def __init__(self, properties=10, commands=2):
        super(MainViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def bonuses(self):
        return self._getViewModel(0)

    @property
    def storeEnvelopes(self):
        return self._getViewModel(1)

    @property
    def album(self):
        return self._getViewModel(2)

    @property
    def sendEnvelopes(self):
        return self._getViewModel(3)

    @property
    def info(self):
        return self._getViewModel(4)

    @property
    def fillEnvelope(self):
        return self._getViewModel(5)

    def getFillEnvelopeIsVisible(self):
        return self._getBool(6)

    def setFillEnvelopeIsVisible(self, value):
        self._setBool(6, value)

    def getCurrentTab(self):
        return Tab(self._getNumber(7))

    def setCurrentTab(self, value):
        self._setNumber(7, value.value)

    def getIsGiftSystemEnabled(self):
        return self._getBool(8)

    def setIsGiftSystemEnabled(self, value):
        self._setBool(8, value)

    def getIsLongDisconnectedFromCenter(self):
        return self._getBool(9)

    def setIsLongDisconnectedFromCenter(self, value):
        self._setBool(9, value)

    def _initialize(self):
        super(MainViewModel, self)._initialize()
        self._addViewModelProperty('bonuses', BonusesModel())
        self._addViewModelProperty('storeEnvelopes', StoreEnvelopesModel())
        self._addViewModelProperty('album', AlbumModel())
        self._addViewModelProperty('sendEnvelopes', SendEnvelopesModel())
        self._addViewModelProperty('info', InfoModel())
        self._addViewModelProperty('fillEnvelope', FillEnvelopeViewModel())
        self._addBoolProperty('fillEnvelopeIsVisible', False)
        self._addNumberProperty('currentTab')
        self._addBoolProperty('isGiftSystemEnabled', True)
        self._addBoolProperty('isLongDisconnectedFromCenter', False)
        self.onViewedTab = self._addCommand('onViewedTab')
        self.onClose = self._addCommand('onClose')
