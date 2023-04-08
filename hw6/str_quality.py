

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
        return 15
    if inputstr[i: j] == "CATD":
        return 10
    if inputstr[i: j] == "CA":
        return 16
    if inputstr[i: j] == "TD":
        return 17
    if inputstr[i: j] == "OG":
        return 15
    return 0
    
# Question 1
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

def hqs3(i,j):
    if (i == j):
        return 0
    return max(hqs3(i + 1,j), hqs3(i, j - 1), q(i,j))

# Question 2
def decomp(cut_num):
    indexs = []
    substrs= [] # Substrings based on cutting position
    substrs_indexs = [] # indexs of substrs
    
    # Transform binary number to indexs at splitting
    i = 1
    while (cut_num != 0):
        if cut_num % 2 == 1:
            indexs.append(i)
        i += 1;
        cut_num = cut_num >> 1
    
    
    # Get subsrings based on indexs of cutting
    indexs.reverse()
    if len(indexs) != 0:
        substrs.append(inputstr[ :n - indexs[0]])
        substrs_indexs.append((0, n - indexs[0]))
        for i in range(0, len(indexs) - 1):
            substrs.append(inputstr[n - indexs[i] : n - indexs[i + 1]])
            substrs_indexs.append((n - indexs[i], n - indexs[i + 1] ))
        substrs.append(inputstr[n - indexs[-1]: ])
        substrs_indexs.append((n - indexs[-1], n))
    else:
        substrs.append(inputstr)
        substrs_indexs.append((0,n))

    # print(substrs)
    # print(substrs_indexs)
    # Evaluate minimum quality of all substrings
    min_quality = 999999
    for substr_index in substrs_indexs:
        if q(substr_index[0], substr_index[1]) < min_quality:
            min_quality = q(substr_index[0], substr_index[1])

    return min_quality

def decompmax(cut_num):
    if cut_num == 2 ** n:
        return 0
    return max(decomp(cut_num), decompmax(cut_num + 1))

def decompamx_dp():
    decomplist = [0 for i in range(2 ** n)]
    for i in range(len(decomplist) - 2, -1, -1):
        decomplist[i] = max(decomp(i), decomplist[i + 1])
    return decomplist[0]

if __name__ == "__main__":

    print(decompmax( int('00000', 2)))
    print(decompamx_dp())


