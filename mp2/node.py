
import sys

class Node:
    def  __init__(self,nodeid,num,term,state,leader,log,commitIndex):
        self.id = nodeid
        self.num = num
        self.term = term
        self.state = state
        self.leader = leader
        self.log = log
        self.commitIndex = commitIndex
        return




if __name__ == "__main__":

    node = Node(int(sys.argv[1]),int(sys.argv[2]),1,"",None,[],None)

    print(f"Starting node {node.id}")


    while True:
        print(f"SEND {node.id} Msg {node.num}",flush=True)
        line = sys.stdin.readline()
        if line is None:
            break
        print(line)

