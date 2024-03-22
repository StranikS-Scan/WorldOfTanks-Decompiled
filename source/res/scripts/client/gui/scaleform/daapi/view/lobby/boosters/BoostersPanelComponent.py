# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/boosters/BoostersPanelComponent.py
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.meta.SlotsPanelMeta import SlotsPanelMeta
from gui.Scaleform.genConsts.BOOSTER_CONSTANTS import BOOSTER_CONSTANTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.goodies.goodie_items import MAX_ACTIVE_BOOSTERS_COUNT
from gui.shared.utils.functions import makeTooltip
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.game_control import IBoostersController
from skeletons.gui.goodies import IGoodiesCache
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
    boosters = dependency.descriptor(IBoostersController)
    goodiesCache = dependency.descriptor(IGoodiesCache)

    def __init__(self):
        super(BoostersPanelComponent, self).__init__()
        self._isPanelInactive = True
        self._wasPopulated = False
        self._slotsMap = {}
        self._slotProps = None
        return

    def setSettings(self, isPanelInactive=True):
        self._isPanelInactive = isPanelInactive
        if self._wasPopulated:
            self._buildList()

    def setSlotProps(self, slotProps):
        self._slotProps = slotProps
        self.as_setPanelPropsS(self._slotProps or _GUI_SLOTS_PROPS)

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
            tooltip = TOOLTIPS_CONSTANTS.BOOSTERS_BOOSTER_INFO
        return tooltip

    def _populate(self):
        super(BoostersPanelComponent, self)._populate()
        g_clientUpdateManager.addCallbacks({'goodies': self.__onUpdateGoodies})
        self.boosters.onPersonalReserveTick += self.__onUpdateGoodies
        self._buildList()
        self._wasPopulated = True

    def _dispose(self):
        self._isPanelInactive = None
        self._wasPopulated = None
        self._slotsMap = None
        self.boosters.onPersonalReserveTick -= self.__onUpdateGoodies
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(BoostersPanelComponent, self)._dispose()
        return

    def __getAvailableBoosters(self):
        criteria = REQ_CRITERIA.BOOSTER.IS_READY_TO_ACTIVATE
        return self.goodiesCache.getBoosters(criteria=criteria)

    def _buildList(self):
        result = []
        activeBoosters = self.goodiesCache.getBoosters(criteria=REQ_CRITERIA.BOOSTER.ACTIVE)
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

        self.as_setPanelPropsS(self._slotProps or _GUI_SLOTS_PROPS)
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
        return {'boosterId': booster.boosterID,
         'id': str(idx),
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
