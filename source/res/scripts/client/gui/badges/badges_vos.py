# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/badges/badges_vos.py
from gui.impl import backport
from gui.impl.gen.resources import R
from gui.shared.formatters import text_styles, icons
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.settings import ICONS_SIZES
_UNIQUE_SUFFIX_BADGE_TOOLTIPS = {}

def getSuffixBadgeTooltip(badge):
    return _UNIQUE_SUFFIX_BADGE_TOOLTIPS.get(badge.getName(), TOOLTIPS_CONSTANTS.BADGES_SUFFIX_ITEM) if badge.isSuffixLayout() else ''


def makeBadgeVO(badge):
    return {'id': badge.badgeID,
     'title': text_styles.stats(badge.getUserName()),
     'description': text_styles.main(badge.getUserDescription()),
     'enabled': badge.isAchieved,
     'selected': badge.isSelected,
     'highlightIcon': badge.getHighlightIcon(),
     'isFirstLook': badge.isNew(),
     'visual': badge.getBadgeVO(ICONS_SIZES.X80)}


def makeSuffixBadgeVO(badge):
    stripImg = R.images.gui.maps.icons.library.badges.strips.c_68x28.dyn('strip_{}'.format(badge.badgeID))
    labelDyn = R.strings.badge.suffix.dyn('badge_{}'.format(badge.badgeID))
    labelText = text_styles.main(backport.text(labelDyn())) if labelDyn else ''
    activeLabelText = text_styles.stats(backport.text(labelDyn())) if labelDyn else ''
    return {'id': badge.badgeID,
     'label': text_styles.concatStylesToSingleLine(labelText, icons.starYellow(0)) if badge.isTemporary else labelText,
     'activeLabel': text_styles.concatStylesToSingleLine(activeLabelText, icons.starYellow(0)) if badge.isTemporary else activeLabelText,
     'tooltip': getSuffixBadgeTooltip(badge),
     'stripImg': backport.image(stripImg()) if stripImg else '',
     'img': badge.getSuffixSmallIcon(),
     'hasFootnoteMark': badge.isTemporary}
