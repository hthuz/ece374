import socket
import sys
import time
import threading
import csv





########
# class
########
# queue element is [msg_content,msg_id,final_priority,deliverable,sender, [[turn,suggestor],[turn,suggestor]]]
class hold_queue:
    def __init__(self):
        self.queue = []
   
    def displayqueue(self):
        print("#######   queue start  ########")
        for i in range(0,len(self.queue)):
            print (self.queue[i])
        print("#######    queue end   ########")
        
    
    def queue_append(self,datalist):
        self.queue.append(datalist)
    
    def queue_find_index(self,msg_id):
        index = -1
        for i in range(len(self.queue)):      
            if (self.queue[i])[1] == msg_id:
                index = i
        return index

    def queue_update_element(self,index,final_priority,deliverable,suggestor):
        self.queue[index][2] = final_priority
        self.queue[index][3] = deliverable
        self.queue[index][4] = suggestor

    def sort_queue(self):
        self.queue.sort(key=lambda x:(x[2], x[3], x[4]))
        # smaller final_priority will be at the head
        # smaller deliverable will be at the head， undiliverable will be at the head
        # smaller suggestor will be at the head
        
    def feedbacklist_append(self, index, proposed_info):
        (self.queue[index][5]).append(proposed_info)
        
    def feedbacklist_check(self, index):
        return len(self.queue[index][5])

    def feedbacklist_sort(self, index):
        (self.queue[index][5]).sort(key=lambda x:(x[0],x[1]))

    def feedbacklist_agreed_priority(self,index):
        return self.queue[index][5][0][0]
    
    def feedbacklist_suggested_id(self,index):
        return self.queue[index][5][0][1]
    
    def check_and_remove(self):
        while (len(self.queue) > 0 and self.queue[0][3] == 1):
            popdata = self.queue[0]
            self.queue.remove(self.queue[0])
            handle_transaction(popdata[0])
            # print (f"deliver:{popdata}")
            



###########
# variable
###########

node_name = ""
node_num = 0
node_id = ""
node_port = 0

# node_id : value
other_node_ip = dict()    
other_node_port = dict()
send_conn = dict()

receive_conn = []
receive_prepared = []
seen_typemid = []


queue = hold_queue()
turn = 0 # Lamport Timestamp
terminate = 0

# lock
seen_lock = threading.Lock()
queue_lock = threading.Lock()
turn_lock = threading.Lock()

DELIVERABLE = 1
UNDELIVERABLE = 0

################
#### Transaction Related
################

# Account : Balance
bank = dict()


###################
# message function
###################
def askMessage(msg_id,message_content, send_priority,need_multicast):
    string = "ask"+"|" +  msg_id  + "|" + message_content + "|" + send_priority +"|"+ need_multicast+"|"
    return string.ljust(128," ")

def feedbackMessage(msg_id, proposed_priority, suggestor,need_multicast):
    string = "feedback"+"|"+ msg_id + "|" + proposed_priority+ "|" + suggestor +"|"+ need_multicast+"|"
    return string.ljust(128," ")

def decidedMessage(msg_id, agreed_priority, suggested_id,need_multicast):
    string = "decided"+"|"+msg_id+"|"+ agreed_priority+"|"+suggested_id + "|" + need_multicast+"|"
    return string.ljust(128," ")


##########
# readtxt
##########
def readtxt(filename):
    global other_node_ip
    global other_node_port
    global node_num
    f = open(filename, 'r', encoding='utf-8')
    for line in f:
        data_line = line.strip("\n").split()
        if len(data_line) == 1:
            node_num = int(data_line[0])
        else:
            other_node_id = (data_line[0])[4]
            ip = data_line[1]
            port = int(data_line[2])

            other_node_ip[other_node_id] = ip
            other_node_port[other_node_id] = port
    return 


#################
# establish_send
#################
def establish_send(node_id, ip, port):
    global node_name
    global node_num
    global send_conn

    # Keep connecting until all connections are set
    while (len(send_conn) != node_num):
        # i is id of other nodes
        try:
            con = socket.socket()
            con.connect((ip, port))
            send_conn[node_id] = con
            break
        except:
            continue
    print(f"#1 {node_name} send connection established")
    return


###########################
# receive_message_thread
###########################
def receive_message(i):
    global queue
    global node_id
    global turn
    global node_num
    global receive_conn
    global receive_prepared
    global seen_typemid


    con = receive_conn[i]
    while not terminate:
        receive_prepared [i] = 1
        data = con.recv(128).decode('utf-8')
        if (len(data) != 128):
            data += con.recv(128).decode('utf-8')

        # print(data.strip(" "))
        datalist = data.split("|")
        msg_type = datalist[0]
        msg_id = datalist[1]
        typemid = msg_type + "|" + msg_id

        if (msg_type == "feedback"):
            typemid = typemid + "|feebacker:" + datalist[3]

        # judge if it is in the seen list
        seen_lock.acquire()
        if (typemid in seen_typemid):
            # print("reject:"+typemid)
            seen_lock.release()   # fuck it!
            continue
        # print("accept:"+typemid)
            
        # update seen msg list when receive
        seen_typemid.append(typemid)
        seen_lock.release()

        if (msg_type == "ask"):
            msg_content = datalist[2]
            original_priority = int(datalist[3])
            need_multicast = int(datalist[4])

            # update queue
            # [content,msg_id,final_priority,deliverable,suggestor,[]]
            queue_lock.acquire()
            queue.queue_append([msg_content,msg_id,original_priority,UNDELIVERABLE,int(msg_id[0]),[]])
            queue.sort_queue()
            # myqueue.displayqueue()
            queue_lock.release()

            # add the my_turn
            turn_lock.acquire()
            turn += 1
            cur_turn = turn
            turn_lock.release()

            # update seen msg list when send
            typemid1 = "feedback" + "|" + msg_id + "|feebacker:" + node_id
            seen_lock.acquire()
            seen_typemid.append(typemid1)
            seen_lock.release()

            # send feedback message
            # print("send:"+typemid1)
            feedbackmessage = feedbackMessage(msg_id,str(cur_turn), node_id,str(1))
            multicast_message(feedbackmessage)

            if (need_multicast == 1):
                # print("multicast:"+typemid)
                askmessage = askMessage(msg_id,msg_content, str(original_priority),str(0))
                multicast_message(askmessage)


        if (msg_type == "feedback"):

            proposed_priority = int(datalist[2])
            suggestor = int(datalist[3])
            need_multicast = int(datalist[4])

            if (msg_id[0] == node_id):
                # update queue
                # [content,mid,final_priority,deliverable,sender,[]]
                queue_lock.acquire()
                index = queue.queue_find_index(msg_id)
                if index == -1: 
                    print(" cannot find the messages")
                    return -1
                queue.feedbacklist_append(index, [proposed_priority,suggestor])
                if (queue.feedbacklist_check(index) == node_num + 1):

                    # update seen_typemid when send
                    typemid2 = "decided"+"|" + msg_id
                    seen_lock.acquire()
                    seen_typemid.append(typemid2)
                    seen_lock.release()

                    # multicast decide message
                    queue.feedbacklist_sort(index)
                    agreed_priority = queue.feedbacklist_agreed_priority(index)
                    suggested_id = queue.feedbacklist_suggested_id(index)
                    # print("send:"+typemid2)
                    decidedmessage = decidedMessage(msg_id,str(agreed_priority), str(suggested_id),str(1))
                    multicast_message(decidedmessage)

                    # update queue value
                    queue.queue_update_element(index,agreed_priority,DELIVERABLE ,suggested_id)
                    queue.sort_queue()
                    queue.check_and_remove()

                # myqueue.displayqueue()
                queue_lock.release()

            if (need_multicast == 1):
                # print("multicast:"+typemid)
                feedbackmessage = feedbackMessage(msg_id, str(proposed_priority), str(suggestor),str(0))
                multicast_message(feedbackmessage)



        if (msg_type == "decided"):
                
            msg_content = datalist[0]
            priority = int(datalist[2])
            suggestor_id = int(datalist[3])
            need_multicast = int(datalist[4])

            # update priority and suggested_id
            queue_lock.acquire()
            index = queue.queue_find_index(msg_id)
            if (index == -1):
                print ("fail "+ msg_id +"\n")
                # myqueue.displayqueue()
                return -1
            queue.queue_update_element(index,priority,1,suggestor_id)
            queue.sort_queue()  # must sort immediatly
            # myqueue.displayqueue()

            # check if deliverable, remove from queue
            queue.check_and_remove()
            queue_lock.release()

            if (need_multicast == 1):
                # print("multicast:"+typemid)
                decidedmessage = decidedMessage(msg_id, str(priority), str(suggestor_id), str(0))
                multicast_message(decidedmessage)

            
        # con.send("ack".encode('utf-8'))
        # print("receive "+data)
    
    
###########################
# send_message thread
############################

def multicast_message(msg_content):
    global send_conn
    for key in send_conn:
        (send_conn[key]).send("{0}".format(msg_content).encode("utf-8"))
        # (send_conn[key]).recv(1024).decode("utf-8")


def handle_transaction(msg_content):
    global bank

    if "DEPOSIT" in msg_content:
        account, amount = msg_content.split(' ')[1], int(msg_content.split(' ')[2])
        if account not in bank:
            bank[account] = 0
        bank[account] += amount

    if "TRANSFER" in msg_content:
        account, dest, amount = msg_content.split(' ')[1], msg_content.split(' ')[3], int(msg_content.split(' ')[4])
        if account not in bank:
            print("Error!, Account not in Bank!")
            exit(1)
        if dest not in bank:
            bank[dest] = 0

        # Do Transaction
        if bank[account] - amount >= 0:
            bank[account] -= amount
            bank[dest] += amount

    # Print balance information
    balance_info = ""
    for account in bank:
        balance_info += " " + account + ":" + str(bank[account])
    print("BALANCES" + balance_info ) 

    return



#######
# main
#######
def main():
    # Node Information
    global node_name
    global node_id
    global node_port
    global node_num 
    global other_node_ip

    # Connection Information
    global send_conn
    global receive_conn
    global receive_prepared

    global turn
    global queue
    global terminate
    global seen_typemid


    if len(sys.argv) != 4:
        print("invalid input")
        return -1
    

    # my node name
    node_name = sys.argv[1]
    node_port = int(sys.argv[2])
    readtxt(sys.argv[3])
    node_id = node_name[4]
    # readtxt and set config for other nodes
    print(other_node_ip)
    print(other_node_port)

    print(f"#1 {node_name} is waiting for connection")

    # establish send connection (set send_conn)
    for i in other_node_ip.keys():
        send_conn_thread = threading.Thread(target=establish_send, args=(i, other_node_ip[i], other_node_port[i]))
        send_conn_thread.start()
    
    # establish the receive socket
    node = socket.socket()
    node.bind(('127.0.0.1', node_port))
    node.listen(20)
    while (len(receive_conn) != node_num):
        conn,addr = node.accept()
        receive_conn.append(conn)
        receive_prepared.append(0)

    print(f"#1 {node_name} receive connection established")
    # wait until send connection established already
    while (len(send_conn) != node_num or len(receive_conn) != node_num):
        continue
    #####
    # Connection is done
    #####

    # tackles message receive from each other node
    for i in range(0,node_num):
        receive_thread = threading.Thread(target=receive_message, args=(i,))
        receive_thread.start()

    # wait until receive thread prepared already
    while True:
        sum = 0
        for i in range(0,node_num):
            sum = sum + receive_prepared[i]
        if (sum == node_num):
            break
    

    # send message thread
    for row in sys.stdin:
        msg_content = row.strip('\n')

        # update turn, store cur_turn
        turn_lock.acquire()
        turn += 1
        cur_turn = turn
        turn_lock.release()

        # message id example: "1 520", which means node1, turn 520
        msg_id = node_id + " " + str(cur_turn)

        # update seen_typemid when send
        # Msg Type | node_id lamport timestamp
        typemid = "ask" + "|" + msg_id
        seen_lock.acquire()
        seen_typemid.append(typemid)
        seen_lock.release()


        # update queue
        queue_lock.acquire()
        queue.queue_append([msg_content,msg_id,cur_turn,UNDELIVERABLE,int(node_id),[]])
        queue.feedbacklist_append(queue.queue_find_index(msg_id), [cur_turn,int(node_id)])
        queue.sort_queue()
        # queue.displayqueue()
        queue_lock.release()

        # prepare the message and start the send thread
        askmessage = askMessage( msg_id, msg_content, str(cur_turn),str(1))
        multicast_message(askmessage)



if __name__ == '__main__':
        main()

        

