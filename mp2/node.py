
import sys
import time
import threading

hbinterval = 0.00001

class Node:
    def  __init__(self,nodeid,num):
        self.id = nodeid
        self.num = num
        self.timeout = (nodeid + 1) * 0.2
        self.term = 1
        self.state = "FOLLOWER"
        self.leader = None
        self.log = [None]
        self.logindex = 0
        self.commitIndex = 0
        # Candidate
        self.votenum = 0
        # Follower
        self.votedfor = 0
        self.lasttime = time.time()
        # Leader
        self.replica_num = 0
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

    node = Node(int(sys.argv[1]),int(sys.argv[2]) )

    check_timeout_thread = threading.Thread(target=check_timeout,args=(node,))
    check_timeout_thread.start()

    while True:
        if node.state == "LEADER":
            for nodeid in range(node.num):
                if nodeid == node.id: continue
                if node.logindex == 0:
                    print(f"SEND {nodeid} AppendEntries {node.term} {node.id}", flush=True)
                else:
                    print(f"SEND {nodeid} AppendEntries {node.term} {node.id} [\"{node.log[node.logindex][1]}\"]",flush=True)

            # Receive Message
            line = sys.stdin.readline()  
            if line is None: break
            line = line.strip()
            # time.sleep(hbinterval)

            if "AppendEntriesResponse" in line:
                if node.commitIndex < node.logindex:
                    reply = line.split(" ")[4]
                    if reply == "true":
                        node.replica_num += 1
                continue

            # Make Committment
            if node.replica_num > node.num / 2:
                node.commitIndex = node.logindex
                print(f"STATE commitIndex={node.commitIndex}")
                print(f"COMMITTED {node.log[node.logindex][1]} {node.commitIndex}", flush=True)
                for nodeid in range(node.num):
                    if nodeid == node.id: continue
                    print(f"SEND {nodeid} Committed {node.term} {node.commitIndex}", flush=True)

            # Receive Log from client
            if "LOG" in line:
                content = line.split(" ")[1]
                node.log.append([node.term, content])
                node.logindex += 1
                node.replica_num = 1
                print(f"STATE log[{node.logindex}]=[{node.term},\"{content}\"]")
                continue

            # A leader with higher term because of network partition
            if "AppendEntries" in line:
                sender_id = int(line.split(" ")[1])
                sender_term = int(line.split(" ")[3])
                if sender_term > node.term:
                    node.term = sender_term
                    node.leader = sender_id
                    node.state = "FOLLOWER"
                    print(f"STATE term={node.term}")
                    print(f"STATE state=\"{node.state}\"")
                    print(f"STATE leader={node.leader}")
                continue


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
                    node.leader = int(sender_id)
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
                    node.votedfor = int(sender_id)
                    node.leader = int(sender_id)
                    print(f"SEND {sender_id} RequestVotesResponse {node.term} true", flush=True)
                    continue

            # Receive AppendEntries
            if "AppendEntries" in line:
                sender_id = line.split(" ")[1]
                sender_term = line.split(" ")[3]
                node.leader = int(sender_id)
                node.term = int(sender_term)

                print(f"STATE term={node.term}")
                print(f"STATE state=\"{node.state}\"")
                print(f"STATE leader={node.leader}")
                if len(line.split(" ")) == 6:
                    content = line.split(" ")[5]
                    content = content[2:-2]
                    node.log.append([node.term,content])
                    node.logindex += 1
                    print(f"STATE log[{node.logindex}]=[{node.term},\"{content}\"]")
                print(f"SEND {sender_id} AppendEntriesResponse {sender_term} true", flush=True)
                continue

            # Receive committed
            if "Committed" in line:
                sender_id = int(line.split(" ")[1])
                commitIndex = int(line.split(" ")[4])
                node.commitIndex = commitIndex # Or node.logindex

                print(f"STATE commitIndex={node.commitIndex}")
                print(f"COMMITTED {node.log[node.logindex][1]} {node.commitIndex}", flush=True)
                continue

    print("Somehow it comes to an end")

        



        






