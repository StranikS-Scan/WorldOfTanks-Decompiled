# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/boosters/BoostersPanelComponent.py
from gui import game_control
from helpers import i18n
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.goodies.Booster import MAX_ACTIVE_BOOSTERS_COUNT
from gui.goodies.GoodiesCache import g_goodiesCache
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.genConsts.BOOSTER_CONSTANTS import BOOSTER_CONSTANTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.daapi.view.meta.SlotsPanelMeta import SlotsPanelMeta
from gui.shared.ItemsCache import g_itemsCache
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from gui.shared.utils.functions import makeTooltip
_GUI_SLOTS_PROPS = {'slotsCount': MAX_ACTIVE_BOOSTERS_COUNT,
 'slotWidth': 50,
 'paddings': 64,
 'groupPadding': 18,
 'ySlotPosition': 5,
 'offsetSlot': 13,
 'useOnlyLeftBtn': True}
ADD_BOOSTER_ID = 'add'
_ADD_AVAILABLE_BOOSTER_ID = 'addAvailable'
_EMPTY_BOOSTER_ID = 'empty'

class BoostersPanelComponent(SlotsPanelMeta):

    def __init__(self):
        super(BoostersPanelComponent, self).__init__()
        self._items = g_itemsCache.items
        self._isPanelInactive = True
        self._wasPopulated = False
        self._slotsMap = {}

    def setSettings(self, isPanelInactive = True):
        self._isPanelInactive = isPanelInactive
        if self._wasPopulated:
            self._buildList()

    def getBoosterSlotID(self, idx):
        return self._slotsMap.get(int(idx), None)

    def getSlotTooltipBody(self, slotIdx):
        boosterID = self._slotsMap.get(int(slotIdx), None)
        tooltip = ''
        if boosterID in (ADD_BOOSTER_ID, _ADD_AVAILABLE_BOOSTER_ID):
            if not self._isPanelInactive:
                body = TOOLTIPS.BOOSTERSPANEL_OPENBOOSTERSWINDOW_BODY
                tooltip = makeTooltip(None, body)
        else:
            booster = g_goodiesCache.getBooster(int(boosterID))
            tooltip = makeTooltip(i18n.makeString(MENU.BOOSTERSWINDOW_BOOSTERSTABLERENDERER_HEADER, boosterName=booster.userName, quality=booster.qualityStr), booster.description, i18n.makeString(TOOLTIPS.BOOSTERSPANEL_BOOSTERDESCRIPTION_NOTE, time=booster.getUsageLeftTimeStr()))
        return tooltip

    def _populate(self):
        super(BoostersPanelComponent, self)._populate()
        g_clientUpdateManager.addCallbacks({'goodies': self.__onUpdateGoodies})
        game_control.g_instance.boosters.onBoosterChangeNotify += self.__onUpdateGoodies
        self._buildList()
        self._wasPopulated = True

    def _dispose(self):
        self._items = None
        self._isPanelInactive = None
        self._wasPopulated = None
        self._slotsMap = None
        game_control.g_instance.boosters.onBoosterChangeNotify -= self.__onUpdateGoodies
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(BoostersPanelComponent, self)._dispose()
        return

    def __getAvailableBoosters(self):
        criteria = REQ_CRITERIA.BOOSTER.IS_READY_TO_ACTIVATE
        return g_goodiesCache.getBoosters(criteria=criteria)

    def _buildList(self):
        result = []
        activeBoosters = g_goodiesCache.getBoosters(criteria=REQ_CRITERIA.BOOSTER.ACTIVE)
        activeBoostersList = sorted(activeBoosters.values(), key=lambda b: b.getUsageLeftTime(), reverse=True)
        availableBoostersCount = len(self.__getAvailableBoosters())
        activeBoostersCount = min(len(activeBoostersList), MAX_ACTIVE_BOOSTERS_COUNT)
        freeSlotsCount = MAX_ACTIVE_BOOSTERS_COUNT - min(activeBoostersCount, MAX_ACTIVE_BOOSTERS_COUNT)
        addBoostersSlotsCount = min(freeSlotsCount, availableBoostersCount)
        self._slotsMap = {}
        for idx in range(0, activeBoostersCount):
            booster = activeBoostersList[idx]
            self._slotsMap[idx] = booster.boosterID
            result.append(self.__makeBoosterVO(idx, booster))

        icon = ''
        if not self._isPanelInactive:
            icon = RES_ICONS.MAPS_ICONS_ARTEFACT_EMPTYORDER
        addAndActiveBoostersCount = activeBoostersCount + addBoostersSlotsCount
        for idx in range(activeBoostersCount, MAX_ACTIVE_BOOSTERS_COUNT):
            self._slotsMap[idx], slotLinkage = self.getEmptySlotParams(idx, addAndActiveBoostersCount)
            result.append(self.__makeEmptyBoosterVO(idx, slotLinkage, icon))

        self.as_setPanelPropsS(_GUI_SLOTS_PROPS)
        self.as_setSlotsS(result)

    def getEmptySlotParams(self, idx, addAndActiveBoostersCount):
        if idx < addAndActiveBoostersCount and not self._isPanelInactive:
            slotLinkage = BOOSTER_CONSTANTS.SLOT_ADD_UI
            emptyBoosterID = _ADD_AVAILABLE_BOOSTER_ID
        else:
            slotLinkage = BOOSTER_CONSTANTS.SLOT_UI
            emptyBoosterID = ADD_BOOSTER_ID
        return (emptyBoosterID, slotLinkage)

    def __makeBoosterVO(self, idx, booster):
        return {'id': str(idx),
         'icon': booster.icon,
         'inCooldown': booster.inCooldown,
         'cooldownPercent': booster.getCooldownAsPercent(),
         'leftTime': booster.getUsageLeftTime(),
         'leftTimeText': booster.getShortLeftTimeStr(),
         'showLeftTime': True,
         'isDischarging': True,
         'isInactive': self._isPanelInactive,
         'isEmpty': False,
         'qualityIconSrc': booster.getQualityIcon(),
         'slotLinkage': BOOSTER_CONSTANTS.SLOT_UI}

    def __makeEmptyBoosterVO(self, idx, slotLinkage, icon):
        return {'id': str(idx),
         'isInactive': self._isPanelInactive,
         'isEmpty': True,
         'icon': icon,
         'slotLinkage': slotLinkage,
         'showLeftTime': False}

    def __onUpdateGoodies(self, *args):
        self._buildList()
