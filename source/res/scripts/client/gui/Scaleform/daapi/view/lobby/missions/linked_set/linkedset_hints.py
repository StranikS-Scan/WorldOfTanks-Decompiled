# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/linked_set/linkedset_hints.py
from gui.impl.wrappers.background_blur import WGUIBackgroundBlurSupportImpl
from gui.Scaleform.daapi.view.meta.LinkedSetHintsViewMeta import LinkedSetHintsViewMeta
from gui.Scaleform.genConsts.APP_CONTAINERS_NAMES import APP_CONTAINERS_NAMES
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import LinkedSetEvent
from gui.sounds.ambients import BattleResultsEnv
from gui.Scaleform.daapi.view.lobby.missions.missions_helper import getLinkedSetBonuses
from gui.server_events.bonuses import mergeBonuses

class LinkedSetHintsView(LinkedSetHintsViewMeta):
    __sound_env__ = BattleResultsEnv

    def __init__(self, ctx):
        super(LinkedSetHintsView, self).__init__()
        self.ctx = ctx
        self._messagesLeft = ctx['messages']
        self._withBlur = ctx.get('withBlur', False)
        self._currentMessage = self._messagesLeft.pop(0)
        self.__blur = WGUIBackgroundBlurSupportImpl()

    def updateMessages(self, messages):
        self._messagesLeft = messages

    def closeView(self):
        callback = self._currentMessage.get('callback', None)
        if callback:
            callback()
        self._currentMessage = None
        if self._messagesLeft:
            self._currentMessage = self._messagesLeft.pop(0)
        if self._currentMessage:
            self._updateView()
        else:
            self.destroy()
        return

    def _populate(self):
        super(LinkedSetHintsView, self)._populate()
        self._updateView()
        if self._withBlur:
            blurLayers = [APP_CONTAINERS_NAMES.VIEWS, APP_CONTAINERS_NAMES.SUBVIEW, APP_CONTAINERS_NAMES.BROWSER]
            self.__blur.enable(APP_CONTAINERS_NAMES.DIALOGS, blurLayers)
        self.fireEvent(LinkedSetEvent(LinkedSetEvent.HINTS_VIEW, ctx={'shown': True}), scope=EVENT_BUS_SCOPE.LOBBY)

    def _dispose(self):
        super(LinkedSetHintsView, self)._dispose()
        if self._withBlur:
            self.__blur.disable()
        self.fireEvent(LinkedSetEvent(LinkedSetEvent.HINTS_VIEW, ctx={'shown': False}), scope=EVENT_BUS_SCOPE.LOBBY)

    def _updateView(self):
        self.as_setDataS(self._getViewCtxFromMessage(self._currentMessage))
        soundID = self._currentMessage.get('soundID', None)
        if soundID:
            self.soundManager.playInstantSound(soundID)
        return

    def _getViewCtxFromMessage(self, message):
        return {'iconPath': message.get('iconPath', ''),
         'icon': message.get('icon', ''),
         'title': message.get('title', ''),
         'description': message.get('description', ''),
         'buttonLabel': message.get('buttonLabel', ''),
         'back': message.get('back', 'red'),
         'awards': self._getAwards(message.get('bonuses', []))}

    def _getAwards(self, bonuses):
        return [ {'icon': award['imgSource'],
         'value': award['label'],
         'tooltip': award.get('tooltip', None),
         'specialAlias': award.get('specialAlias', None),
         'specialArgs': award.get('specialArgs', None),
         'overlayType': award.get('overlayType')} for award in getLinkedSetBonuses(mergeBonuses(bonuses)) if award ]
