class Ops:
    def __init__(self):
        pass

    NOT = 'NOT'

    EQ = '='
    NOT_EQ = '!='
    GT = '>'
    GT_EQ = '>='
    LT = '<'
    LT_EQ = '<='

    LIKE = 'LIKE'
    IN = 'IN'

    AND = 'AND'
    OR = 'OR'


class AbstractNode:
    def __init__(self):
        pass

    def to_sql(self):
        pass

    def __str__(self):
        return self.to_sql()

    def __repr__(self):
        return self.to_sql()

    # query methods ###############

    def EQ(self, rvalue):
        return EqNode(self, rvalue)

    def NOT_EQ(self, rvalue):
        return NotEqNode(self, rvalue)

    def GT(self, rvalue):
        return GtNode(self, rvalue)

    def GT_EQ(self, rvalue):
        return GtEqNode(self, rvalue)

    def LT(self, rvalue):
        return LtNode(self, rvalue)

    def LT_EQ(self, rvalue):
        return LtEqNode(self, rvalue)

    def LIKE(self, rvalue):
        return LikeNode(self, rvalue)

    def IN(self, *values):
        return InNode(self, *values)

    def AND(self, *values):
        return AndNode(self, *values)

    def OR(self, *values):
        return OrNode(self, *values)

    # DSL ##############################################################

    # ==, in
    def __eq__(self, others):
        length = 1
        try:
            length = len(others)
        except:
            pass

        return self.EQ(others) if type(others) in (str, unicode) or length == 1 else self.IN(*others)

    # !=
    def __ne__(self, others):
        length = 1
        try:
            length = len(others)
        except:
            pass

        return self.NOT_EQ(others) if type(others) in (str, unicode) or length == 1 else self.IN(*others).negate()

    # LIKE
    # def __xor__(self, other):
    #     return self.LIKE(other)

    # LIKE
    def __mod__(self, other):
        return self.LIKE(other)

    # >
    def __gt__(self, other):
        return self.GT(other)

    # >=
    def __ge__(self, other):
        return self.GT_EQ(other)

    # <
    def __lt__(self, other):
        return self.LT(other)

    # <=
    def __le__(self, other):
        return self.LT_EQ(other)

    # &
    def __and__(self, other):
        return self.AND(other)

    # |
    def __or__(self, other):
        return self.OR(other)


class AbstractNegateNode:
    def __init__(self):
        pass

    def negate(self):
        return NotNode(self)


class AbstractJoinNode(AbstractNode, AbstractNegateNode):
    def __init__(self, op, nodes):
        self.op = op
        self.nodes = nodes

    def to_sql(self):
        return '{}'.format(' {} '.format(self.op)).join('({})'.format(str(node)) for node in self.nodes)


class ValueNode(AbstractNode):
    def __init__(self, *values):
        self.values = values

    def to_sql(self):
        return ', '.join(str(val) for val in self.values)

    def __len__(self):
        return len(self.values)

    def __iter__(self):
        return self.values.__iter__()


# class StringNode(ValueNode):
#     def __init__(self, *values):
#         ValueNode.__init__(self, *(repr(val) for val in values))


class NotNode(AbstractNode):
    def __init__(self, node):
        self.node = node

    def to_sql(self):
        return 'NOT {}'.format(str(self.node))


class AndNode(AbstractJoinNode):
    def __init__(self, *nodes):
        AbstractJoinNode.__init__(self, Ops.AND, nodes)


class OrNode(AbstractJoinNode):
    def __init__(self, *nodes):
        AbstractJoinNode.__init__(self, Ops.OR, nodes)


class BinaryNode(AbstractNode, AbstractNegateNode):
    def __init__(self, lnode, op, rnode):
        self.lnode = lnode
        self.rnode = rnode
        self.op = op

    def to_sql(self):
        return '{} {} {}'.format(str(self.lnode),
                                 self.op,
                                 repr(self.rnode) if type(self.rnode) in (str, unicode) else str(self.rnode))


class LikeNode(BinaryNode):
    def __init__(self, lvalue, rvalue):
        BinaryNode.__init__(self, lvalue, Ops.LIKE, rvalue)


class EqNode(BinaryNode):
    def __init__(self, lvalue, rvalue):
        BinaryNode.__init__(self, lvalue, Ops.EQ, rvalue)


class NotEqNode(BinaryNode):
    def __init__(self, lvalue, rvalue):
        BinaryNode.__init__(self, lvalue, Ops.NOT_EQ, rvalue)


class GtNode(BinaryNode):
    def __init__(self, lvalue, rvalue):
        BinaryNode.__init__(self, lvalue, Ops.GT, rvalue)


class GtEqNode(BinaryNode):
    def __init__(self, lvalue, rvalue):
        BinaryNode.__init__(self, lvalue, Ops.GT_EQ, rvalue)


class LtNode(BinaryNode):
    def __init__(self, lvalue, rvalue):
        BinaryNode.__init__(self, lvalue, Ops.LT, rvalue)


class LtEqNode(BinaryNode):
    def __init__(self, lvalue, rvalue):
        BinaryNode.__init__(self, lvalue, Ops.LT_EQ, rvalue)


class InNode(BinaryNode):
    def __init__(self, lnode, *values):
        BinaryNode.__init__(self, lnode, Ops.IN, values)

    def to_sql(self):
        return '{} IN ({})'.format(str(self.lnode), ','.join(repr(node) for node in self.rnode))
