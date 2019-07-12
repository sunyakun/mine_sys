from abc import abstractmethod


class Model:
    name = None
    exception = None

    def __init__(self, name):
        self._data = []
        self.name = name

    @property
    def data(self):
        return self._data

    @abstractmethod
    def add(self, value):
        pass

    def to_json_able(self):
        """
        json able是指可以使用json.dumps转换成json格式字符串的python对象
        """
        return {
            "name": self.name,
            "data": self._data
        }


class Node:
    name = str()
    lines = None

    def __init__(self, name):
        self.lines = list()
        self.name = name

    def add_line(self, line):
        if isinstance(line, Line):
            self.lines.append(line)
        else:
            raise TypeError('line type must be %s' % Line)

    def __repr__(self):
        return '%s' % self.name


class Line:
    name = str()
    parent = None
    child = None

    def __init__(self, parent, child):
        if isinstance(parent, Node) and isinstance(child, Node):
            self.parent = parent
            self.child = child
        else:
            raise ValueError('child and parent type must be %s' % Node)

    @abstractmethod
    def to_dict(self):
        pass

    def __repr__(self):
        return '<%s>-<%s>' % (self.parent.name, self.child.name)


class DecisionTree(Model):

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        if not isinstance(value, Node):
            raise TypeError("value type must be %s type" % Node)
        self._data = value

    def add(self, value):
        self.data = value

    @classmethod
    def _to_dict(cls, data):
        return {
            "name": data.name,
            "children": [{
                "name": line.name,
                "children": [cls._to_dict(line.child)]
            } for line in data.lines]
        }

    def to_json_able(self):
        return self._to_dict(self._data)

    def forecast(self, value):
        raise NotImplemented()


# class DecisionIterator:
#     """
#     层次遍历决策树
#     """
#
#     def __init__(self, root):
#         self.cursor = root
#         self.line_queue = []
#         self.node_queue = []
#
#     def __next__(self):
#         if self.cursor is None:
#             raise StopIteration()
#         res = self.cursor
#         if isinstance(self.cursor, Node):
#             for line in self.cursor.lines:
#                 self.node_queue.append(line.child)
#
#             self.line_queue = self.cursor.lines
#             if self.line_queue:
#                 self.cursor = self.line_queue.pop(0)
#             elif len(self.node_queue):
#                 self.cursor = self.node_queue.pop(0)
#             else:
#                 self.cursor = None
#         elif isinstance(self.cursor, Line):
#             if len(self.line_queue):
#                 self.cursor = self.line_queue.pop(0)
#             elif len(self.node_queue):
#                 self.cursor = self.node_queue.pop(0)
#             else:
#                 raise Exception("data structure error!")
#         return res
#
#     def __iter__(self):
#         return self


class PieGraph(Model):

    def __init__(self, name):
        super().__init__(name)
        self._data = []

    def add(self, item: dict):
        if "value" not in item or "name" not in item:
            raise DataFormatError(
                'data format must like {"value":"foo","name":"bar"}')
        self._data.append(item)


class ThreeDHistogram(Model):

    def __init__(self, name):
        super().__init__(name)
        self._data = []

    def add(self, value):
        if len(value) != 3:
            raise DataFormatError('Length must be 3')
        self._data.append(value)


class Scatter(Model):
    label = int()

    def add(self, value):
        self._data.append(value)


class DataFormatError(Exception):
    pass
