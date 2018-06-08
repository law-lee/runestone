class Stack:
    '''implement a stack with list, stack is A LIFO'''
    def __init__(self):
        self.stack = []

    def push(self,item):
        self.stack.append(item)

    def pop(self):
        return self.stack.pop()

    def peek(self):
        return self.stack[-1]

    def isEmpty(self):
        if self.stack:
            return False
        else:
            return True

    def size(self):
        return len(self.stack)

def matches(s1,s2):
    s = '{[('
    sv = '}])'
    if s.index(s1) == sv.index(s2):
        return True
    else:
        return False

def parChecker(symbolString):
    stack = Stack()
    balanced = True
    index = 0
    while index < len(symbolString) and balanced:
        symbol = symbolString[index]
        if symbol in '{[(':
            stack.push(symbol)
        else:
            if stack.isEmpty():
                balanced = False
            else:
                c = stack.pop()
                if not matches(c,symbol):
                    balanced = False

        index += 1
    if stack.isEmpty() and balanced:
        return True
    else:
        return False

def basestring(ch):
    s = '0123456789ABCDEF'
    return s[ch]
def convertByBase(num,base):
    s = Stack()

    while num != 0:
        rem = num % base
        s.push(rem)
        num = num // base

    st = ''
    while not s.isEmpty():
        st += basestring(s.pop())
    return st

'''
Assume the infix expression is a string of tokens delimited by spaces.
 The operator tokens are *, /, +, and -, along with the left and right parentheses,
  ( and ). The operand tokens are the single-character identifiers A, B, C, and so
  on. The following steps will produce a string of tokens in postfix order.

Create an empty stack called opstack for keeping operators. Create an empty list for output.
Convert the input infix string to a list by using the string method split.
Scan the token list from left to right.
If the token is an operand, append it to the end of the output list.
If the token is a left parenthesis, push it on the opstack.
If the token is a right parenthesis, pop the opstack until the corresponding left parenthesis is removed. Append each operator to the end of the output list.
If the token is an operator, *, /, +, or -, push it on the opstack. However, first remove any operators already on the opstack that have higher or equal precedence and append them to the output list.
When the input expression has been completely processed, check the opstack. Any operators still on the stack can be removed and appended to the end of the output list.
'''

def infixToPostfix(infixexpr):
    prec = {}
    prec["*"] = 3
    prec["/"] = 3
    prec["+"] = 2
    prec["-"] = 2
    prec["("] = 1
    opStack = Stack()
    postfixList = []
    tokenList = infixexpr.split()

    for token in tokenList:
        if token in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" or token in "0123456789":
            postfixList.append(token)
        elif token == '(':
            opStack.push(token)
        elif token == ')':
            topToken = opStack.pop()
            while topToken != '(':
                postfixList.append(topToken)
                topToken = opStack.pop()
        else:
            while (not opStack.isEmpty()) and \
               (prec[opStack.peek()] >= prec[token]):
                  postfixList.append(opStack.pop())
            opStack.push(token)

    while not opStack.isEmpty():
        postfixList.append(opStack.pop())
    return " ".join(postfixList)

print(infixToPostfix("A * B + C * D"))
print(infixToPostfix("( A + B ) * C - ( D - E ) * ( F + G )"))

print(convertByBase(120,16))