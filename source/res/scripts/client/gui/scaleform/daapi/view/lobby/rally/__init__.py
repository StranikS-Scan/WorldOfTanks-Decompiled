# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rally/__init__.py


class NavigationStack(object):
    __stacks = {}

    @classmethod
    def clear(cls, key):
        if key in cls.__stacks:
            cls.__stacks[key] = []

    @classmethod
    def exclude(cls, key, flashAlias):
        items = cls.__stacks.get(key, [])[:]
        for item in items:
            if item[0] == flashAlias:
                cls.__stacks[key].remove(item)

    @classmethod
    def hasHistory(cls, key):
        return len(cls.__stacks[key]) if key in cls.__stacks else 0

    @classmethod
    def current(cls, key):
        return cls.__stacks[key][-1] if key in cls.__stacks and cls.__stacks[key] else None

    @classmethod
    def prev(cls, key):
        return cls.__stacks[key][-2] if key in cls.__stacks and len(cls.__stacks[key]) > 1 else None

    @classmethod
    def nav2Next(cls, key, flashAlias, pyAlias, itemID):
        item = (flashAlias, pyAlias, itemID)
        if key in cls.__stacks:
            if item not in cls.__stacks[key]:
                cls.__stacks[key].append(item)
        else:
            cls.__stacks[key] = [item]

    @classmethod
    def nav2Prev(cls, key):
        return cls.__stacks[key].pop() if key in cls.__stacks and cls.__stacks[key] else None
