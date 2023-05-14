
import sys
import time
import threading

hbinterval = 0.01

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
        self.lasttime = None
        return
    
    def output_state(self):
        print(f"STATE term={self.term}", flush=True)
        print(f"STATE state=\"{self.state}\"", flush=True)
        if self.leader == None:
            # print(f"STATE leader=0",flush=True)
            print(f"STATE leader=\"None\"",flush=True)
        else:
            print(f"STATE leader={self.leader}", flush=True)
        # print(f"STATE log={self.term}", flush=True)
        # print(f"STATE commitIndex={self.term}", flush=True)
    
nodelock = threading.Lock()

def check_timeout(node):
    # Start election
    while True:
        if node.state == "FOLLOWER":
            if time.time() - node.lasttime >= node.timeout:
                node.term += 1
                node.votenum = 1
                node.state = "CANDIDATE"
                print(f"STATE state=\"{node.state}\"")
                print(f"STATE term={node.term}")
                for nodeid in range(node.num):
                    if nodeid == node.id: continue
                    print(f"SEND {nodeid} RequestVotes {node.term}",flush=True)
    return


if __name__ == "__main__":

    timeout = (int(sys.argv[1]) + 1) * 0.2
    node = Node(int(sys.argv[1]),int(sys.argv[2]),timeout,1,"FOLLOWER",None,[],None)

    node.lasttime = time.time()
    node.votenum = 0
    check_timeout_thread = threading.Thread(target=check_timeout,args=(node,))
    check_timeout_thread.start()

    while True:
        if node.state == "LEADER":
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

            # Set as leader
            if node.votenum > node.num / 2:
                node.leader = node.id
                node.state = "LEADER"
                print(f"STATE state=\"{node.state}\"")
                print(f"STATE leader={node.leader}")
                continue

        if node.state == "FOLLOWER":
            # Receive Message
            # Follower may wait for some time here
            line = sys.stdin.readline()  
            if line is None: break
            line = line.strip()
            # If the node has become candidate after timeout
            # But the node still has to wait for this message to arrive
            # and then it releazes it is candidate now
            # This may need to be improved
            node.lasttime = time.time()
            ###############################################
            if node.state == "CANDIDATE":
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

                # Set as leader
                if node.votenum > node.num / 2:
                    node.leader = node.id
                    node.state = "LEADER"
                    print(f"STATE state=\"{node.state}\"")
                    print(f"STATE leader={node.leader}")
                    continue
            ###############################################


            # Receive RequestVote
            if "RequestVotes" in line:
                sender_id = line.split(" ")[1]
                sender_term = line.split(" ")[3]
                if int(sender_term) < node.term:
                    print(f"SEND {sender_id} RequestVotesResponse {node.term} false",flush=True)
                    continue
                if int(sender_term) > node.term:
                    node.term = int(sender_term)
                    node.votedfor = None
                if node.votedfor == None or sender_id != None:
                    node.votedfor = sender_id
                    node.leader = sender_id
                    print(f"SEND {sender_id} RequestVotesResponse {node.term} true", flush=True)
                    continue

            # Receive AppendEntries
            if "AppendEntries" in line:
                sender_id = line.split(" ")[1]
                sender_term = line.split(" ")[3]
                node.leader = sender_id
                print(f"SEND {sender_id} AppendEntriesResponse {sender_term} true", flush=True)
                print(f"STATE term={node.term}")
                print(f"STATE state=\"{node.state}\"")
                print(f"STATE leader={node.leader}")
                continue
    print("Somehow it comes to an end")

        



        






