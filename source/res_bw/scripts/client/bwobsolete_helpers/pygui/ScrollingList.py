# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bwobsolete_helpers/PyGUI/ScrollingList.py
import BigWorld, GUI, Keys
import Utils
from PyGUIBase import PyGUIBase
ITEM_MARGIN = 0.05

class ScrollingList(PyGUIBase):
    factoryString = 'PyGUI.ScrollingList'

    def __init__(self, component):
        PyGUIBase.__init__(self, component)
        self.selection = 0
        self.itemGuiName = ''
        self.backFn = None
        self.budget = Utils.Budget(self.createItem, self.deleteItem)
        self.selectItemCallback = lambda : None
        self.maxVisibleItems = 0
        self.totalHeightScreenClip = 0.0
        component.focus = True
        component.crossFocus = True
        return

    def active(self, state):
        if state == self.isActive:
            return
        PyGUIBase.active(self, state)
        self.selectItem(self.selection)

    def onSelect(self, pageControl):
        pass

    def createItem(self):
        assert self.itemGuiName != ''
        g = GUI.load(self.itemGuiName)
        setattr(self.items, 'm%d' % (len(self.items.children),), g)
        g.script.doLayout(self)
        return g

    def deleteItem(self, c):
        self.items.delChild(c)

    def setupItems(self, backFn, setupParams):
        self.backFn = backFn
        oldidx = -1
        if self.selection < len(self.items.children):
            oldidx = self.selection
        self.budget.balance(len(setupParams))
        num = len(setupParams)
        for i in xrange(0, num):
            g = self.items.children[i][1]
            g.script.setup(setupParams[i], i)
            g.script.select(0)

        if num > 0:
            self.doLayout(None)
            if oldidx >= 0:
                self.selectItem(oldidx)
        return

    def doLayout(self, parent):
        PyGUIBase.doLayout(self, parent)
        y = 1.0
        totalHeight = 0
        itemHeight = 0
        screenWidth = BigWorld.screenWidth()
        for discard, i in self.component.items.children:
            i.position.y = y
            thisItemHeight = i.script.adjustFont(screenWidth)
            if itemHeight == 0 and thisItemHeight != 0:
                itemHeight = thisItemHeight
            y = y - itemHeight - ITEM_MARGIN
            totalHeight += itemHeight + ITEM_MARGIN

        self.component.items.height = totalHeight
        heightMode = self.component.items.heightMode
        self.component.items.heightMode = 'LEGACY'
        self.totalHeightScreenClip = float(self.component.items.height)
        self.component.items.heightMode = heightMode
        self.items.script.maxScroll[1] = max(0, self.totalHeightScreenClip - self.component.height)
        self.items.script.minScroll[1] = 0
        if self.items.script.maxScroll[1] == 0.0:
            self.scrollUp.visible = 0
            self.scrollDown.visible = 0
        self.maxVisibleItems = int(2.0 / itemHeight) if itemHeight > 0 else 1

    def canSelect(self, idx):
        if idx < 0:
            return 0
        if idx >= len(self.items.children):
            return 0
        return self.items.children[idx][1].script.canSelect()

    def moveSelection(self, dist):
        self.selectItem(self.getSelectionOffset(dist))

    def scrollList(self, dist):
        self.items.script.scrollBy(0, 0.1 * dist)
        self.scrollUp.visible = self.items.script.canScrollUp()
        self.scrollDown.visible = self.items.script.canScrollDown()

    def getSelectionOffset(self, dist):
        curIdx = self.selection
        if dist == 0:
            return curIdx
        newIdx = (curIdx + dist) % len(self.items.children)
        direction = -1 if dist < 0 else 1
        while not self.canSelect(newIdx):
            newIdx = (newIdx + direction) % len(self.items.children)
            if newIdx == curIdx:
                return newIdx

        return newIdx

    def selectItem(self, idx = 0, bringIntoView = True, animate = True, forceReselect = False):
        num = len(self.items.children)
        if num == 0 or idx == self.selection and not forceReselect:
            return
        oldIdx = self.selection
        if idx >= num:
            idx = num - 1
        if idx < 0:
            idx = 0
        self.selection = idx
        if oldIdx >= 0 and oldIdx < num:
            self.items.children[oldIdx][1].script.select(0)
        self.items.children[idx][1].script.select(1)
        if bringIntoView:
            self.checkSelectionVisible(animate)
        self.updateControlBar()
        try:
            self.selectItemCallback(idx)
        except Exception as e:
            print 'ERROR: ScrollingList.selectItem callback', e

    def executeSelected(self, playSound = True):
        BigWorld.playSound('ui/boop')
        entry = self.items.children[self.selection][1]
        i = entry.script.onSelect(self)
        self.updateControlBar()

    def updateControlBar(self):
        pass

    def checkSelectionVisible(self, animate = True):
        if self.items.script.maxScroll[1] == 0.0:
            self.items.script.scrollTo(0, 0, animate)
            self.scrollUp.visible = 0
            self.scrollDown.visible = 0
            return
        self.scrollToItem(self.selection, animate)

    def scrollToItem(self, idx, animate = True):
        itemHeight = self.totalHeightScreenClip / len(self.component.items.children)
        itemScrollY = itemHeight * idx
        currentScroll = self.items.script.scroll[1]
        if itemScrollY < currentScroll + itemHeight:
            scrollTarget = itemScrollY - itemHeight
        elif itemScrollY > currentScroll + self.component.height - itemHeight * 2.0:
            scrollTarget = itemScrollY - self.component.height + itemHeight * 2.0
        else:
            scrollTarget = currentScroll
        self.items.script.scrollTo(0, scrollTarget, animate)
        self.scrollUp.visible = self.items.script.canScrollUp()
        self.scrollDown.visible = self.items.script.canScrollDown()

    def handleTraversalKeys(self, event):
        if not event.isKeyDown():
            return False
        elif event.key in [Keys.KEY_JOYDDOWN, Keys.KEY_DOWNARROW, Keys.KEY_S]:
            if len(self.items.children) == 0:
                return True
            oidx = None
            idx = self.selection
            while idx != oidx:
                if oidx == None:
                    oidx = idx
                idx += 1
                if idx >= len(self.items.children):
                    idx = 0
                if self.canSelect(idx):
                    self.selectItem(idx)
                    break

            BigWorld.playSound('ui/tick')
            return True
        elif event.key in [Keys.KEY_JOYDUP, Keys.KEY_UPARROW, Keys.KEY_W]:
            if len(self.items.children) == 0:
                return 1
            oidx = None
            idx = self.selection
            while idx != oidx:
                if oidx == None:
                    oidx = idx
                idx -= 1
                if idx < 0:
                    idx = len(self.items.children) - 1
                if self.canSelect(idx):
                    self.selectItem(idx)
                    break

            BigWorld.playSound('ui/tick')
            return True
        else:
            if event.key == Keys.KEY_PGUP:
                dist = self.maxVisibleItems
                if self.selection - dist < 0:
                    dist = self.selection
                self.moveSelection(-dist)
            elif event.key == Keys.KEY_PGDN:
                dist = self.maxVisibleItems
                if self.selection + dist >= len(self.items.children):
                    dist = len(self.items.children) - self.selection - 1
                self.moveSelection(dist)
            elif event.key == Keys.KEY_HOME:
                self.selectItem(0)
            elif event.key == Keys.KEY_END:
                self.selectItem(len(self.items.children) - 1)
            return False

    def handleKeyEvent(self, event):
        key = event.key
        if event.isKeyDown():
            if self.handleTraversalKeys(event):
                return True
            if key == [Keys.KEY_JOYA] or key == Keys.KEY_RETURN and not BigWorld.isKeyDown(Keys.KEY_LALT) and not BigWorld.isKeyDown(Keys.KEY_RALT):
                if len(self.items.children) == 0:
                    return True
                BigWorld.sinkKeyEvents(Keys.KEY_RETURN)
                self.executeSelected()
                return 1
            if key in [Keys.KEY_JOYB,
             Keys.KEY_JOYBACK,
             Keys.KEY_ESCAPE,
             Keys.KEY_BACKSPACE]:
                if self.backFn != None:
                    self.active(0)
                    BigWorld.playSound('ui/boop')
                    self.backFn()
                    return 1
        return False

    def onLoad(self, section):
        self.itemGuiName = section.readString('itemGui', '')
        assert self.itemGuiName != ''

    def onBound(self):
        PyGUIBase.onBound(self)
        try:
            self.items = self.component.items
        except:
            print 'the scrolling list should have a items area!!!'

        if hasattr(self.component, 'scrollUp'):
            self.scrollUp = self.component.scrollUp
        if hasattr(self.component, 'scrollDown'):
            self.scrollDown = self.component.scrollDown
