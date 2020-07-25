# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/linked_set/linkedset_hints.py
from gui.Scaleform.daapi.view.meta.LinkedSetHintsViewMeta import LinkedSetHintsViewMeta
from gui.impl import backport
from gui.impl.gen import R
from gui.sounds.ambients import BattleResultsEnv
from gui.Scaleform.daapi.view.lobby.missions.missions_helper import getLinkedSetBonuses
from gui.server_events.bonuses import mergeBonuses

class LinkedSetHintsView(LinkedSetHintsViewMeta):
    __sound_env__ = BattleResultsEnv

    def __init__(self, ctx):
        super(LinkedSetHintsView, self).__init__()
        self.ctx = ctx
        self._messagesLeft = ctx['messages']
        self._currentMessage = self._messagesLeft.pop(0)

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

    def _updateView(self):
        self.as_setDataS(self._getViewCtxFromMessage(self._currentMessage))
        soundID = self._currentMessage.get('soundID', None)
        if soundID:
            self.soundManager.playInstantSound(soundID)
        return

    def _getViewCtxFromMessage(self, message):
        return {'icon': backport.image(R.images.gui.maps.icons.linkedSet.icons.dyn(message.get('icon', ''))()),
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
         'specialArgs': award.get('specialArgs', None)} for award in getLinkedSetBonuses(mergeBonuses(bonuses)) if award ]
