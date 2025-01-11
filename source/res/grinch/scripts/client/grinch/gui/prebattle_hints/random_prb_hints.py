# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/prebattle_hints/random_prb_hints.py
import random
from GrinchAccountSettings import getSettings, PRB_HINT_NUM, setSettings
from gui import makeHtmlString
from gui.impl import backport
from gui.impl.gen import R

def _createHtmlTextWithDescr(title, descrTxt):
    return makeHtmlString('html_templates:battle/loadingScreenSimple', 'mainTip', ctx={'title': backport.text(title),
     'description': backport.text(descrTxt)})


def _makeImgPath(index):
    return 'grinch/gui/maps/icons/map/screen/prebattle_hints/hint_{}.dds'.format(index)


class PrbRandomHintManager(object):

    def __init__(self):
        super(PrbRandomHintManager, self).__init__()
        self._imgAndText = []
        prbHintsTexts = R.strings.grinch.battle.loadingScreen
        prbHintsImgs = R.images.grinch.gui.maps.icons.map.screen.prebattle_hints
        totalHintCount = max(prbHintsTexts.length(), prbHintsImgs.length())
        foundTexts = []
        foundImgs = []
        for i in range(totalHintCount):
            itemIndex = i + 1
            txtItem = prbHintsTexts.dyn('hint{}'.format(itemIndex))
            if txtItem:
                foundTexts.append(txtItem)
            imgRPath = prbHintsImgs.dyn('hint_{}'.format(itemIndex))
            imgStrPath = None
            if imgRPath:
                imgStrPath = _makeImgPath(itemIndex)
                foundImgs.append(imgStrPath)
            self._imgAndText.append((imgStrPath, _createHtmlTextWithDescr(txtItem.title(), txtItem.description()) if txtItem else None))

        random.shuffle(foundImgs)
        random.shuffle(foundTexts)
        for i, (img, txt) in enumerate(self._imgAndText):
            if img is None:
                if len(foundImgs) > 1:
                    self._imgAndText[i] = (foundImgs.pop(), txt)
                else:
                    self._imgAndText[i] = (foundImgs[0], txt)
            if txt is None:
                imgRef = self._imgAndText[i][0]
                if len(foundTexts) > 1:
                    self._imgAndText[i] = (imgRef, foundTexts.pop())
                elif len(foundTexts) == 1:
                    self._imgAndText[i] = (imgRef, foundTexts[0])
                else:
                    self._imgAndText[i] = (imgRef, '')

        self._imgAndText = tuple(self._imgAndText)
        return

    def incrementAndSave(self):
        currHintNum = getSettings(PRB_HINT_NUM)
        setSettings(PRB_HINT_NUM, (currHintNum + 1) % len(self._imgAndText))

    def getHintText(self):
        return self._imgAndText[getSettings(PRB_HINT_NUM)][1]

    def getHintImagePath(self):
        return self._imgAndText[getSettings(PRB_HINT_NUM)][0]
