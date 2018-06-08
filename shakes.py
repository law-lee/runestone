import random
def generate(strlen):
    alphabets = 'abcdefghijklmnopqrstuvwxyz '
    res = ''
    for i in range(strlen):
        res = res + alphabets[random.randrange(27)]

    return res

def score(goalstr,newstr):
    strlen = len(goalstr)
    sco = 0
    for i in range(strlen):
        if goalstr[i] == newstr[i]:
            sco +=  1

    return float(sco) / strlen

def main():
    goalstr = 'methinks it is like a weasel'
    strlen = len(goalstr)
    newstr = generate(strlen)
    oldscore = score(goalstr,newstr)
    num = 0
    best = 0
    while oldscore < 1:
        if oldscore > best:
            num += 1
            best = oldscore
            newstr = generate(strlen)
            newscore = score(goalstr,newstr)
            oldscore = newscore
            print(newscore, newstr)
            if num == 1000 :
                print(newscore,newstr)
                num = 0
main()

