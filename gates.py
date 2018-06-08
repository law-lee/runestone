class LogicGate:
    '''A logic gate should contain name and output'''
    def __init__(self,n):
        self.name = n
        self.output = None

    def getName(self):
        return self.name

    def getOutput(self):
        self.output = self.performGateLogic()
        return self.output

class BianryGate(LogicGate):
    '''A binary gate contains two pins'''
    def __init__(self,n):
        LogicGate.__init__(self,n)
        self.pinA = None
        self.pinB = None

    def setPinA(self,p):
        if self.pinA == None:
            self.pinA = p

    def setPinB(self,p):
        if self.pinB == None:
            self.pinB=p

    def getPinA(self):
        if self.pinA == None:
            return int(input("Enter Pin A input for gate "+self.getName()+"-->"))
        elif isinstance(self.pinA, Connector):
            return self.pinA.getFromGate().getOutput()
        else:
            return self.pinA

    def getPinB(self):
        if self.pinB == None:
            return int(input("Enter Pin B input for gate "+self.getName()+"-->"))
        elif isinstance(self.pinB, Connector):
            return  self.pinB.getFromGate().getOutput()
        else:
            return self.pinB

    def setConnectPin(self,source):
        if self.pinA == None:
            self.pinA = source
        elif self.pinB == None:
            self.pinB = source
        else:
            print("No empty Pin !")

class UnaryGate(LogicGate):
    '''A unary gate contains one pin'''
    def __init__(self,n):
        LogicGate.__init__(self,n)

        self.pinO = None
    def setpinO(self,p):
        if self.pinO == None:
            self.pinO = p

    def getpinO(self):
        if self.pinO == None:
            return int(input("Enter Pin input for gate "+self.getName()+"-->"))
        elif isinstance(self.pinO, Connector):
            return  self.pinO.getFromGate().getOutput()
        else:
            return self.pinO

    def setConnectPin(self,source):
        if self.pinO == None:
            self.pinO = source
        else:
            print("No empty Pin !")

class AndGate(BianryGate):
    '''And gate perform and logic algorithm'''
    def __init__(self,n):
        BianryGate.__init__(self,n)

    def performGateLogic(self):
        a = self.getPinA()
        b = self.getPinB()
        if a == 1 and b == 1:
            return 1
        else:
            return 0

class OrGate(BianryGate):
    '''Or gate perform or logic algorithm'''
    def __init__(self,n):
        BianryGate.__init__(self,n)

    def performGateLogic(self):
        a = self.getPinA()
        b = self.getPinB()
        if a == 0 and b == 0:
            return 0
        else:
            return 1

class NotGate(UnaryGate):
    '''Not gate perform not logic algorithm'''
    def __init__(self,n):
        UnaryGate.__init__(self,n)

    def performGateLogic(self):
        a = self.getpinO()
        if a == 0:
            return 1
        else:
            return 0

class Connector:
    '''A connector connect a logic gate's output and a logic gate's input'''
    def __init__(self,fgate,tgate):
        self.fromgate = fgate
        self.togate = tgate
        tgate.setConnectPin(self)

    def getFromGate(self):
        return self.fromgate

    def getToGate(self):
        return self.togate

class ExorGate(BianryGate):
    '''EXOR gate different inputs OUTPUT 1  '''
    def __init__(self,n):
        BianryGate.__init__(self,n)

    def performGateLogic(self):
        a = self.getPinA()
        b = self.getPinB()
        if (a==0 and b==1) or (a==1 and b==0):
            return 1
        else:
            return 0

class HalfAdder:
    '''A half adder needs two input ,two output'''
    def __init__(self,a=None,b=None):
        self.inA = a
        self.inB = b
        self.xorg = ExorGate("XorG")
        self.andg = AndGate("AndG")
        self.xorg.setPinA(self.inA)
        self.andg.setPinA(self.inA)
        self.xorg.setPinB(self.inB)
        self.andg.setPinB(self.inB)
        self.sum = self.xorg.getOutput()
        self.carry = self.andg.getOutput()

    def getresult(self):
        return str(self.carry)+str(self.sum)

class FullAdder:
    '''A full adder has three inputs a,b,Cin , two outputs Sum,Cout'''
    def __init__(self,a=None,b=None,Cin=None):
        self.inA = a
        self.inB = b
        self.Cin = Cin

        self.xorg1 = ExorGate("XorG1")
        self.xorg2 = ExorGate("XorG2")
        self.andg1 = AndGate("AndG1")
        self.andg2 = AndGate("AndG2")
        self.org1 = OrGate("OrG1")

        self.xorg1.setPinA(self.inA)
        self.xorg1.setPinB(self.inB)
        self.andg1.setPinA(self.inA)
        self.andg1.setPinB(self.inB)
        self.xorg2.setPinB(self.Cin)
        self.andg2.setPinB(self.Cin)
        Connector(self.xorg1,self.xorg2)
        Connector(self.xorg1,self.andg2)
        Connector(self.andg2,self.org1)
        Connector(self.andg1,self.org1)

        self.sum = self.xorg2.getOutput()
        self.carry = self.org1.getOutput()

    def getCin(self):
        return  self.Cin

    def getSum(self):
        return self.sum

    def getresult(self):
        return str(self.carry) + str(self.sum)




def main():
    while True:
        a = int(input("Input adder A: "))
        b = int(input("Input adder B: "))
        cin = int(input("Input Cin: "))
        ha = FullAdder(a,b,cin)
        print(ha.getresult())

if __name__ == '__main__':
    main()