import turtle
import random

def tree(branchLen,t):
    if branchLen > 5:
        t.down()
        t.pensize(branchLen/5)
        t.pencolor(0,255-branchLen,0)
        angle = random.randrange(15,45)
        subx = random.randrange(5,20)
        t.forward(branchLen)
        t.right(angle)
        tree(branchLen-subx,t)
        t.left(angle*2)
        tree(branchLen-subx,t)
        t.right(angle)
        t.up()
        t.backward(branchLen)

def main():
    t = turtle.Turtle()
    myWin = turtle.Screen()
    t.left(90)
    t.up()
    t.backward(100)
    t.down()
    t.color("green")
    tree(75,t)
    myWin.exitonclick()

main()