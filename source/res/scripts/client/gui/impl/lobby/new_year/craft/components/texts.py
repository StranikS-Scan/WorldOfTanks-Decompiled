# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/craft/components/texts.py
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.new_year.new_year_helper import formatRomanNumber
from items.components.ny_constants import CustomizationObjects, MAX_TOY_RANK
RANDOM_TOY_PARAM = 'random'
TOY_PLACES_STRINGS = {RANDOM_TOY_PARAM: R.strings.ny.craftView.objectTitle.random.place(),
 CustomizationObjects.FIR: R.strings.ny.craftView.objectTitle.Fir(),
 CustomizationObjects.FAIR: R.strings.ny.craftView.objectTitle.Fair(),
 CustomizationObjects.INSTALLATION: R.strings.ny.craftView.objectTitle.Installation()}
TOY_RANKS_STRINGS = tuple([ (formatRomanNumber(i) if i > 0 else backport.text(R.strings.ny.craftView.objectTitle.random.level())) for i in xrange(MAX_TOY_RANK + 1) ])
TOY_SETTING_STRINGS = tuple([R.strings.ny.craftView.objectTitle.random.collection(),
 R.strings.ny.craftView.monitor.setting.NewYear(),
 R.strings.ny.craftView.monitor.setting.Christmas(),
 R.strings.ny.craftView.monitor.setting.Oriental(),
 R.strings.ny.craftView.monitor.setting.Fairytale()])
TOY_TYPE_STRINGS = tuple([R.strings.ny.decorationTypes.typeDisplay.random(),
 R.strings.ny.decorationTypes.top(),
 R.strings.ny.decorationTypes.garland_fir(),
 R.strings.ny.decorationTypes.ball(),
 R.strings.ny.decorationTypes.floor(),
 R.strings.ny.decorationTypes.pavilion(),
 R.strings.ny.decorationTypes.kitchen(),
 R.strings.ny.decorationTypes.garland_fair(),
 R.strings.ny.decorationTypes.attraction(),
 R.strings.ny.decorationTypes.sculpture(),
 R.strings.ny.decorationTypes.sculpture_light(),
 R.strings.ny.decorationTypes.garland_installation(),
 R.strings.ny.decorationTypes.pyro(),
 R.strings.ny.decorationTypes.kiosk()])
