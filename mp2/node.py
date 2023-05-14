
import sys
import time
import threading

hbinterval = 1

class Node:
    def  __init__(self,nodeid,num,timeout, term,state,leader,log,commitIndex):
        self.id = nodeid
        self.num = num
        self.timeout = timeout
        self.term = term
        self.state = state
        self.leader = leader
        self.log = log
        self.commitIndex = commitIndex
        # Candidiate
        self.votenum = None
        # Follower
        self.votedfor = None
        return
    
    def output_state(self):
        print(f"STATE term={self.term}", flush=True)
        print(f"STATE state=\"{self.state}\"", flush=True)
        if self.leader == None:
            print(f"STATE leader=\"None\"",flush=True)
        else:
            print(f"STATE leader={self.leader}", flush=True)
        # print(f"STATE log={self.term}", flush=True)
        # print(f"STATE commitIndex={self.term}", flush=True)
    
    def check_timeout(self):
        # Start election
        while True:
            if self.state == "FOLLOWER":
                if time.time() - self.lasttime >= self.timeout:
                    self.term += 1
                    self.votenum += 1
                    self.state = "CANDIDATE"
                    for nodeid in range(self.num):
                        if nodeid == self.id: continue
                        print(f"SEND {nodeid} RequestVotes {self.term}",flush=True)
        return



if __name__ == "__main__":

    timeout = (int(sys.argv[1]) + 1) * 2
    node = Node(int(sys.argv[1]),int(sys.argv[2]),timeout,1,"FOLLOWER",None,[],None)

    node.lasttime = time.time()
    node.votenum = 0

    check_timeout_thread = threading.Thread(target=node.check_timeout)
    check_timeout_thread.start()

    while True:

        if node.state == "LEADER":
            node.output_state()
            for nodeid in range(node.num):
                if nodeid == node.id: continue
                print(f"SEND {nodeid} AppendEntries {node.term} {node.id}", flush=True)

            # Receive Message
            line = sys.stdin.readline()  
            if line is None: break
            line = line.strip()
            time.sleep(hbinterval)

            if "AppendEntriesResponse" in line:
                continue
            if "LOG" in line:
                print("---Leader election ENDs!---")  
                break

        if node.state == "CANDIDATE":
            node.output_state()
            # Receive Message
            line = sys.stdin.readline()  
            if line is None: break
            line = line.strip()

            # Receive RPC from valid leadre
            if "AppendEntries" in line:
                sender_id = line.split(" ")[1]
                node.leader = sender_id
                node.state = "FOLLOWER"
                continue

            # Receive RequestVote Response
            if "RequestVotesResponse" in line:
                reply = line.split(" ")[4]
                if reply == "true":
                    node.votenum += 1
                continue

            # Set as leader
            if node.votenum > node.num / 2:
                node.leader = node.id
                node.state = "LEADER"
                continue

        if node.state == "FOLLOWER":
            node.output_state()
            # Receive Message
            line = sys.stdin.readline()  
            if line is None: break
            line = line.strip()

            # Receive RequestVote
            if "RequestVotes" in line:
                sender_id = line.split(" ")[1]
                sender_term = line.split(" ")[3]
                node.lasttime = time.time()
                if int(sender_term) < node.term:
                    print(f"SEND {sender_id} RequestVotesResponse {node.term} false",flush=True)
                    continue
                if int(sender_term) > node.term:
                    node.term = int(sender_term)
                    node.votedfor = None
                if node.votedfor == None or sender_id != None:
                    node.votedfor = sender_id
                    print(f"SEND {sender_id} RequestVotesResponse {node.term} true", flush=True)
                    continue

            # Receive AppendEntries
            if "AppendEntries" in line:
                sender_id = line.split(" ")[1]
                sender_term = line.split(" ")[3]
                node.lasttime = time.time()
                node.leader = sender_id
                print(f"SEND {sender_id} AppendEntriesResponse {sender_term} true", flush=True)

    print("Somehow it comes to an end")

        



        






