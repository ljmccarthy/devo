import collections

class LruQueue(object):
    def __init__(self, contents=(), maxlen=None):
        self.deque = collections.deque(contents, maxlen)

    def __iter__(self):
        return iter(self.deque)

    def __len__(self):
        return len(self.deque)

    def add(self, item):
        if item in self.deque:
            self.deque.remove(item)
        self.deque.appendleft(item)

    def access(self, index):
        item = self.deque[index]
        del self.deque[index]
        self.deque.appendleft(item)
        return item
