

n = 2
initpeg = [i for i in range(n , 0, -1)]

# Leftmost item in list means bottom of the peg
pegs = [[], initpeg, []]



def hanoi(n, src, dest, tmp):

    if (n == 0):
        return

    if (n > 0):
        hanoi(n - 1, src, tmp, dest)

        disk = pegs[src][-1]
        pegs[src].pop()
        pegs[dest].append(disk)
        print(pegs)

        hanoi(n - 1, tmp, dest, src)


def hanoi0(n,src,dest,tmp):
    return

        



if __name__ == "__main__":

    print(pegs)
    # print(pegs)



