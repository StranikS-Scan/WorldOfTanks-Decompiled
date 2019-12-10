# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/craft_machine/texts.py
from gui.impl import backport
from gui.impl.gen import R
from helpers import int2roman
from items.components.ny_constants import CustomizationObjects, MAX_TOY_RANK
RANDOM_TOY_PARAM = 'random'
TOY_PLACES_STRINGS = {RANDOM_TOY_PARAM: R.strings.ny.craftView.objectTitle.random.place(),
 CustomizationObjects.FIR: R.strings.ny.craftView.objectTitle.Fir(),
 CustomizationObjects.TABLEFUL: R.strings.ny.craftView.objectTitle.Tableful(),
 CustomizationObjects.INSTALLATION: R.strings.ny.craftView.objectTitle.Installation(),
 CustomizationObjects.ILLUMINATION: R.strings.ny.craftView.objectTitle.Illumination()}
TOY_RANKS_STRINGS = tuple([ (int2roman(i) if i > 0 else backport.text(R.strings.ny.craftView.objectTitle.random.level())) for i in xrange(MAX_TOY_RANK + 1) ])
TOY_SETTING_STRINGS = tuple([R.strings.ny.craftView.objectTitle.random.collection(),
 R.strings.ny.settings.NewYear(),
 R.strings.ny.settings.Christmas(),
 R.strings.ny.settings.Fairytale(),
 R.strings.ny.settings.Oriental()])
TOY_TYPE_STRINGS = tuple([R.strings.ny.decorationTypes.typeDisplay.random(),
 R.strings.ny.decorationTypes.top(),
 R.strings.ny.decorationTypes.garland(),
 R.strings.ny.decorationTypes.ball(),
 R.strings.ny.decorationTypes.floor(),
 R.strings.ny.decorationTypes.table(),
 R.strings.ny.decorationTypes.kitchen(),
 R.strings.ny.decorationTypes.tent(),
 R.strings.ny.decorationTypes.sculpture(),
 R.strings.ny.decorationTypes.decoration(),
 R.strings.ny.decorationTypes.snow_item(),
 R.strings.ny.decorationTypes.trees(),
 R.strings.ny.decorationTypes.ground_light(),
 R.strings.ny.decorationTypes.pyro()])
