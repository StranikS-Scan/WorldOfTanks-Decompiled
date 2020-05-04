# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/dialogs/event_deserter_meta.py
from gui.Scaleform.daapi.view.battle.event.game_event_getter import GameEventGetterMixin
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta
from gui.battle_control import avatar_getter
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.events import ShowDialogEvent
IMAGE_OFFSET_Y = 270

class EventIngameDeserterDialogMeta(I18nConfirmDialogMeta, GameEventGetterMixin):

    def __init__(self, key, focusedID=None):
        GameEventGetterMixin.__init__(self)
        msgCtx = None
        playerVehicleID = avatar_getter.getPlayerVehicleID()
        teammateLifecycleData = self.teammateLifecycle.getParams()
        playerData = teammateLifecycleData.get(playerVehicleID, {})
        maxLivesLimit = teammateLifecycleData.get('maxLivesLimit', 0)
        playerLives = playerData.get('lives', 0)
        playerDeath = playerData.get('death', 0)
        lockedLives = maxLivesLimit - playerLives - playerDeath
        if playerLives == 0 and lockedLives > 0:
            key += '/lockedLivesAvailable'
            info = self.scenarioGoals.getLastGoal()
            goalId = info['uid']
            goalSubstring = backport.text(R.strings.event.goals.substring.dyn(goalId)())
            msgCtx = {'goal': goalSubstring}
        super(EventIngameDeserterDialogMeta, self).__init__(key, messageCtx=msgCtx, focusedID=focusedID)
        return

    def getEventType(self):
        return ShowDialogEvent.SHOW_EVENT_DESERTER_DLG

    def getImagePath(self):
        return backport.image(R.images.gui.maps.icons.battle.deserterLeaveBattle())

    def getOffsetY(self):
        return IMAGE_OFFSET_Y
