

inputstr = "CATDOG"
n = len(inputstr)

def q(i,j):
    if inputstr[i: j] == "CATDOG":
        return 10
    if inputstr[i: j] == "CAT":
        return 9
    if inputstr[i: j] == "DOG":
        return 10
    if inputstr[i: j] == "ATDO":
        return 11
    if inputstr[i: j] == "CATD":
        return 13
    if inputstr[i: j] == "C":
        return 13
    if inputstr[i: j] == "A":
        return 10
    return 0
    
# Highest quality subsring
def hqs(i,j,x):
    if (i == j):
        return x;
    if q(i, j) > x:
        return hqs(i,j, q(i,j))
    else:
        return max(hqs(i + 1, j, x), hqs(i, j - 1, x))

def hqs2(i,j,x):
    if (i == j):
        return x

    m = max(hqs2(i + 1, j, x), hqs2(i, j - 1, x))
    if q(i, j) >x:
        m = max(m, q(i,j))
    return m

if __name__ == "__main__":

    print(hqs(0, n, 0))
    print(hqs2(0, n, 0))

