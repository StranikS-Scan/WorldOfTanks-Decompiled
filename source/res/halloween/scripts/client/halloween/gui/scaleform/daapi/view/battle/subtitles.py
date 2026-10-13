# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/battle/subtitles.py
from __future__ import absolute_import
import BigWorld
from Avatar import PlayerAvatar
from gui import makeHtmlString
from halloween.gui.scaleform.daapi.view.meta.HWSubtitlesMeta import HWSubtitlesMeta
from halloween.gui.sounds.sound_constants import VO
from helpers import i18n, dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class BattleSubtitles(HWSubtitlesMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(BattleSubtitles, self).__init__()
        self._currentMessage = ''
        self._isPostMortem = False
        self._isSubtitleVisible = True

    def _populate(self):
        super(BattleSubtitles, self)._populate()
        if not VO.SUBTITLES_ENABLED_SETTING:
            self._hide()
            return
        else:
            avatar = BigWorld.player()
            if avatar:
                self._soundNotifications = avatar.soundNotifications
                if self._soundNotifications:
                    self._soundNotifications.onSubtitleShow += self._onSubtitleShow
                    self._soundNotifications.onSubtitleHide += self._onSubtitleHide
            ctrl = self.sessionProvider.shared.vehicleState
            if ctrl is not None:
                ctrl.onPostMortemSwitched += self._onPostMortemSwitched
                ctrl.onRespawnBaseMoving += self._onRespawnBaseMoving
                ctrl.onVehicleControlling += self._onVehicleControlling
            return

    def _destroy(self):
        super(BattleSubtitles, self)._destroy()
        if not VO.SUBTITLES_ENABLED_SETTING:
            return
        else:
            player = BigWorld.player()
            if isinstance(player, PlayerAvatar):
                self._soundNotifications = player.soundNotifications
                if self._soundNotifications:
                    self._soundNotifications.onSubtitleShow -= self._onSubtitleShow
                    self._soundNotifications.onSubtitleHide -= self._onSubtitleHide
            ctrl = self.sessionProvider.shared.vehicleState
            if ctrl is not None:
                ctrl.onPostMortemSwitched -= self._onPostMortemSwitched
                ctrl.onRespawnBaseMoving -= self._onRespawnBaseMoving
                ctrl.onVehicleControlling -= self._onVehicleControlling
            return

    def _onSubtitleShow(self, msgKey):
        self._currentMessage = makeHtmlString('html_templates:battle', 'subtitle', {'subtitle': i18n.makeString(msgKey)})
        self._show()

    def _onSubtitleHide(self):
        self._currentMessage = ''
        self._hide()

    def _show(self):
        if self._currentMessage and self._isSubtitleVisible:
            self.as_showS(self._currentMessage)

    def _hide(self):
        self.as_hideS()

    def _onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        self._isPostMortem = True
        self._isSubtitleVisible = False
        self._hide()

    def _onRespawnBaseMoving(self):
        self._isPostMortem = False
        self._isSubtitleVisible = True

    def _onVehicleControlling(self, vehicle):
        if not self._isPostMortem:
            return
        self._isSubtitleVisible = BigWorld.player().playerVehicleID != vehicle.id
        if not self._isSubtitleVisible:
            self._hide()
        else:
            self._show()
