# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/football_buffon_recruitment_panel.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.BuffonRecruitmentMeta import BuffonRecruitmentMeta
from gui.Scaleform.locale.FOOTBALL2018 import FOOTBALL2018
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showHangar
from gui.shared.events import LoadViewEvent
from gui.shared.gui_items import Tankman
from helpers import dependency
from helpers.i18n import makeString as _ms
from items import makeIntCompactDescrByID
from items.tankmen import getNationConfig
from skeletons.gui.game_control import IFootballMetaGame
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from football_hangar_common import OsBitness

class BuffonRecruitment(BuffonRecruitmentMeta):
    itemsCache = dependency.descriptor(IItemsCache)
    eventCache = dependency.descriptor(IEventsCache)
    footballMetaGame = dependency.descriptor(IFootballMetaGame)

    def __init__(self, ctx):
        super(BuffonRecruitment, self).__init__(ctx)
        self.__currentSelectedNationID = None
        self.__selectedVehClass = None
        self.__selectedVehicle = None
        self.__selectedTmanRole = None
        self.__buffonRankID = 5
        return

    def _populate(self):
        super(BuffonRecruitment, self)._populate()
        self.footballMetaGame.onBuffonRecruited += self.__buffonRecruited
        self.as_initDataS({'title': _ms(FOOTBALL2018.CARDCOLLECTION_RECRUITMENT_TITLE),
         'applyButtonLabel': _ms(FOOTBALL2018.CARDCOLLECTION_RECRUITMENT_BUTTON_RECRUIT),
         'cancelButtonLabel': _ms(FOOTBALL2018.CARDCOLLECTION_RECRUITMENT_BUTTON_LATER),
         'nameLabelStr': _ms(FOOTBALL2018.CARDCOLLECTION_RECRUITMENT_NAME_LABEL),
         'rankLabelStr': _ms(FOOTBALL2018.CARDCOLLECTION_RECRUITMENT_MILITARY_RANK_LABEL),
         'name': _ms(FOOTBALL2018.CARDCOLLECTION_RECRUITMENT_NAME),
         'rank': self.__getRole(nation=0, role='commander'),
         'highQualityAnimations': OsBitness.is64Bit()})

    def _dispose(self):
        self.footballMetaGame.onBuffonRecruited -= self.__buffonRecruited
        super(BuffonRecruitment, self)._dispose()

    def onCloseView(self):
        if self.eventCache.isEventEnabled():
            self.fireEvent(LoadViewEvent(VIEW_ALIAS.FOOTBALL_CARD_COLLECTION), EVENT_BUS_SCOPE.LOBBY)
        else:
            showHangar()

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(BuffonRecruitment, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == VIEW_ALIAS.RECRUIT_PARAMS:
            viewPy.init()
            viewPy.onDataChange += self.__onRecruitParamsChange
            viewPy.setLockedRole('commander')

    def _onUnregisterFlashComponent(self, viewPy, alias):
        if alias == VIEW_ALIAS.RECRUIT_PARAMS:
            viewPy.onDataChange -= self.__onRecruitParamsChange
        super(BuffonRecruitment, self)._onUnregisterFlashComponent(viewPy, alias)

    def onApply(self, data):
        self.__currentSelectedNationID = data.nation
        self.__selectedVehClass = data.vehicleClass
        self.__selectedVehicle = data.vehicle
        self.__selectedTmanRole = data.tankmanRole
        vehicleDescr = makeIntCompactDescrByID('vehicle', int(data.nation), int(data.vehicle))
        self.footballMetaGame.recruitBuffon(vehicleDescr)

    def __buffonRecruited(self, success):
        if success:
            self.onCloseView()

    def __onRecruitParamsChange(self, nation, vehClass, vehicle, tManRole):
        self.as_updateRankS(self.__getRole(nation=nation, role=tManRole))

    def __getRole(self, nation, role):
        selectedNationID = int(nation)
        rankIDs = getNationConfig(int(nation)).getRoleRanks(role)
        maxRankIdx = min(self.__buffonRankID, len(rankIDs) - 1)
        return Tankman.getRankUserName(selectedNationID, maxRankIdx)
