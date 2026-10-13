# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/battle/modifier_hint.py
from __future__ import absolute_import
from gui.impl import backport
from halloween.gui.scaleform.daapi.view.battle.battle_hint import BattleHint
from halloween.gui.scaleform.daapi.view.meta.BattleHintModifierMeta import BattleHintModifierMeta
from gui.impl.gen import R
from halloween.gui.sounds import playSound
from halloween.gui.sounds.sound_constants import PhaseModifierSounds

class HWPhaseModifierHint(BattleHint, BattleHintModifierMeta):
    ICONS_PATH = R.images.halloween.gui.maps.icons.battleHints
    BATTLE_HINT = R.strings.halloween_battle.battleHint

    def _showHint(self, model, params):
        vo = model.createVO(params)
        if vo:
            phaseName = params['phaseName']
            modifierName = params['modifierName']
            modifierColor = params['modifierColor']
            self.as_showHintS(vo)
            self.as_updateHintS({'phaseName': backport.text(self.BATTLE_HINT.phase.num(phaseName)()),
             'modifierName': backport.text(self.BATTLE_HINT.modifierName.dyn(modifierName)()),
             'modifierRule': backport.text(self.BATTLE_HINT.modifierRule.dyn(modifierName)()),
             'modifierColor': modifierColor,
             'iconSource': backport.image(self.ICONS_PATH.dyn(modifierName)())})
            playSound(PhaseModifierSounds.START.get(modifierName))
