# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/christmas/chests_view.py
from chat_shared import SYS_MESSAGE_TYPE
from debug_utils import LOG_DEBUG
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.view.lobby.server_events.events_helpers import getChristmasCarouselAwardVO
from gui.Scaleform.daapi.view.meta.ChristmasChestsViewMeta import ChristmasChestsViewMeta
from gui.Scaleform.locale.CHRISTMAS import CHRISTMAS
from gui.christmas.christmas_controller import g_christmasCtrl
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.shared.ItemsCache import g_itemsCache
from gui.shared.SoundEffectsId import SoundEffectsId
from gui.shared.events import LobbySimpleEvent
from gui.shared.formatters import text_styles
from gui.shared.utils.HangarSpace import g_hangarSpace
from helpers import i18n, dependency
from messenger.proto.events import g_messengerEvents
from skeletons.gui.server_events import IEventsCache

class SOUND_TYPES_IDS:
    AWARD = 'award'
    FLARE = 'flare'


class ChristmasChestsView(LobbySubView, ChristmasChestsViewMeta):
    __background_alpha__ = 0.0
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, ctx=None):
        super(ChristmasChestsView, self).__init__(ctx)
        self.__isBtnEnabled = bool(g_christmasCtrl.getClosedChestsCount())
        self.__bonuses = None
        self.__alreadyOpened = False
        self.__isCursorOver3dScene = True
        self.__selected3DEntity = None
        self.__returnCameraToHangar = True
        self.__isBonusReceived = False
        self.__isItemsCacheSynced = False
        return

    def onOpenBtnClick(self):
        if self.__isBtnEnabled:
            if not g_christmasCtrl.getClosedChestsCount():
                self.__returnCameraToHangar = False
                g_eventDispatcher.loadChristmasView()
            else:
                self.as_showAwardRibbonS(False)
                self.__disableBtn()
                self.__alreadyOpened = True
                g_christmasCtrl.openChest()

    def onPlaySound(self, soundType):
        if soundType == SOUND_TYPES_IDS.AWARD:
            self.app.soundManager.playEffectSound(SoundEffectsId.XMAS_AWARD_SHOW)
        elif soundType == SOUND_TYPES_IDS.FLARE:
            self.app.soundManager.playEffectSound(SoundEffectsId.XMAS_RIBBON_SHINE)
            g_christmasCtrl.finishRibbonAnimation()
            self.__enableOpenBtn()

    def onCloseWindow(self):
        g_eventDispatcher.loadHangar()

    def _populate(self):
        super(ChristmasChestsView, self)._populate()
        g_christmasCtrl.onChestsUpdate += self.__updateChestsInfo
        g_christmasCtrl.onCameraSwitchedToChest += self.__initScene
        g_christmasCtrl.onOpenChestAnimationStarted += self.__onOpenAnimationStarted
        g_christmasCtrl.onRibbonAnimationFinished += self.__enableContols
        g_christmasCtrl.onReceivedChestAnimationFinished += self.__enableOpenBtn
        g_christmasCtrl.onEventStopped += self.__checkChristmasState
        g_messengerEvents.serviceChannel.onChatMessageReceived += self.__onQuestComplete
        g_hangarSpace.onObjectSelected += self.__on3DObjectSelected
        g_hangarSpace.onObjectUnselected += self.__on3DObjectUnSelected
        g_hangarSpace.onObjectClicked += self.__on3DObjectClicked
        g_itemsCache.onSyncCompleted += self.__onItemsSynced
        self.addListener(LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, self.__onNotifyCursorOver3dScene)
        self.as_setInitDataS({'backBtnLabel': CHRISTMAS.CHESTVIEW_BACKBTN_LABEL,
         'backBtnDescrLabel': CHRISTMAS.CHESTVIEW_BACKBTN_DESCR_TOHANGAR,
         'closeBtnLabel': CHRISTMAS.CHESTVIEW_CLOSEBTNLABEL})
        g_christmasCtrl.switchToChest()
        g_christmasCtrl.lockAwardsWindowsAndFightBtn()
        self.__updateChestsInfo()
        self.__disableBtn()

    def _dispose(self):
        g_christmasCtrl.unlockAwardsWindowsAndFightBtn()
        g_christmasCtrl.onChestsUpdate -= self.__updateChestsInfo
        g_christmasCtrl.onCameraSwitchedToChest -= self.__initScene
        g_christmasCtrl.onReceivedChestAnimationFinished -= self.__enableOpenBtn
        g_christmasCtrl.onOpenChestAnimationStarted -= self.__onOpenAnimationStarted
        g_christmasCtrl.onRibbonAnimationFinished -= self.__enableContols
        g_christmasCtrl.onEventStopped -= self.__checkChristmasState
        g_hangarSpace.onObjectSelected -= self.__on3DObjectSelected
        g_hangarSpace.onObjectUnselected -= self.__on3DObjectUnSelected
        g_hangarSpace.onObjectClicked -= self.__on3DObjectClicked
        g_itemsCache.onSyncCompleted -= self.__onItemsSynced
        g_messengerEvents.serviceChannel.onChatMessageReceived -= self.__onQuestComplete
        self.removeListener(LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, self.__onNotifyCursorOver3dScene)
        self.__selected3DEntity = None
        self.__bonuses = None
        if g_christmasCtrl.isNavigationDisabled():
            g_christmasCtrl.finishRibbonAnimation()
        if self.__returnCameraToHangar:
            g_christmasCtrl.switchToHangar()
        if g_christmasCtrl.mayRemoveChest():
            g_christmasCtrl.removeChestFromScene()
        super(ChristmasChestsView, self)._dispose()
        return

    def __onNotifyCursorOver3dScene(self, event):
        self.__isCursorOver3dScene = event.ctx.get('isOver3dScene', False)
        if self.__selected3DEntity is not None:
            if self.__isCursorOver3dScene:
                self.__highlight3DEntity(self.__selected3DEntity)
            else:
                self.__fade3DEntity(self.__selected3DEntity)
        return

    def __on3DObjectSelected(self, entity):
        self.__selected3DEntity = entity
        if self.__isCursorOver3dScene and self.__isBtnEnabled:
            self.__highlight3DEntity(entity)

    def __on3DObjectUnSelected(self, entity):
        self.__selected3DEntity = None
        if self.__isCursorOver3dScene:
            self.__fade3DEntity(entity)
        return

    def __on3DObjectClicked(self):
        if self.__isCursorOver3dScene:
            if self.__selected3DEntity is not None:
                itemId = self.__selected3DEntity.selectionId
                if itemId == 'h07_newyear_box' and self.__isBtnEnabled:
                    self.onOpenBtnClick()
        return

    def __highlight3DEntity(self, entity):
        itemId = entity.selectionId
        if itemId == 'h07_newyear_box':
            entity.highlight(True)

    def __fade3DEntity(self, entity):
        entity.highlight(False)

    def __initScene(self):
        if not g_christmasCtrl.isChestOnScene() and g_christmasCtrl.getClosedChestsCount():
            g_christmasCtrl.playReceiveChestAnimation()
        else:
            self.__enableOpenBtn()

    def __disableBtn(self):
        self.__isBtnEnabled = False
        self.as_setOpenBtnEnabledS(self.__isBtnEnabled)

    def __updateChestsInfo(self, *args):
        chestsCount = g_christmasCtrl.getClosedChestsCount()
        if chestsCount:
            if self.__alreadyOpened:
                btnlabel = CHRISTMAS.CHESTVIEW_BTNLABEL_OPENNEXT
            else:
                btnlabel = CHRISTMAS.CHESTVIEW_BTNLABEL_OPEN
            countStr = text_styles.promoSubTitle(chestsCount)
            statusLabel = text_styles.highTitle(i18n.makeString(CHRISTMAS.CHESTVIEW_STATUSLABEL, count=countStr))
        else:
            btnlabel = CHRISTMAS.CHESTVIEW_BTNLABEL_BACKTOTREE
            statusLabel = ''
        self.as_setBottomTextsS(statusLabel, i18n.makeString(btnlabel))

    def __onGiftsReceived(self, bonuses):
        self.__isBonusReceived = True
        self.__bonuses = bonuses
        self.__checkReadyToOpen()

    def __checkChristmasState(self):
        if not g_christmasCtrl.isEventInProgress():
            self.onCloseWindow()

    def __enableOpenBtn(self):
        self.__isBtnEnabled = True
        if self.__isCursorOver3dScene and self.__selected3DEntity is not None:
            self.__highlight3DEntity(self.__selected3DEntity)
        self.as_setOpenBtnEnabledS(self.__isBtnEnabled)
        return

    def __checkReadyToOpen(self):
        if self.__isBonusReceived and self.__isItemsCacheSynced and self.__bonuses is not None:
            g_christmasCtrl.playExploseChestAnimation()
            self.as_setAwardDataS(getChristmasCarouselAwardVO(self.__bonuses))
            self.as_showAwardRibbonS(True)
        return

    def __onItemsSynced(self, *args):
        self.__isItemsCacheSynced = True
        self.__checkReadyToOpen()

    def __onOpenAnimationStarted(self):
        self.as_setControlsEnabledS(False)
        self.__isBonusReceived = False
        self.__isItemsCacheSynced = False

    def __enableContols(self):
        self.as_setControlsEnabledS(True)

    def __onQuestComplete(self, *ctx):
        _, message = ctx
        if message is not None and message.type == SYS_MESSAGE_TYPE.tokenQuests.index() and message.data is not None:
            christmasTreeQuests = self.eventsCache.getHiddenQuests(filterFunc=lambda q: q.getID().startswith('christmas'))
            for qID in message.data.get('completedQuestIDs', set()):
                treeQuest = christmasTreeQuests.get(qID)
                if treeQuest is not None:
                    self.__onGiftsReceived(treeQuest.getBonuses())

        return
