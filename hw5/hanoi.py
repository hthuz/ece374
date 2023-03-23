

n = 8
initpeg = [i for i in range(n , 0, -1)]

# Leftmost item in list means bottom of the peg
pegs = [[],initpeg, []]



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

    if (n == 0):
        return

    if (n > 0):

        hanoi0(n - 1, src, dest, tmp)

        disk = pegs[src][-1]
        pegs[src].pop()
        pegs[tmp].append(disk)
        print(pegs)

        hanoi0(n - 1, dest, src, tmp)

        disk = pegs[tmp][-1]
        pegs[tmp].pop()
        pegs[dest].append(disk)
        print(pegs)

        hanoi0(n - 1,src, dest, tmp )

    return

        

def hanoibyebye(n,src,dest, tmp,max_n):

    if n == 0:
        return

    if n > 0:

        hanoibyebye(n - 1, src, tmp, dest,max_n)

        disk = pegs[src][-1]
        pegs[src].pop()

        if (disk != max_n):
            pegs[dest].append(disk)
        else:
            max_n -= 1

        print(pegs)

        hanoibyebye(n - 1, tmp, dest, src,max_n)

if __name__ == "__main__":

    print(pegs)
    hanoibyebye(n,1,2,0,n)
    print(pegs)



