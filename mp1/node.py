import socket
import sys
import time
import threading
import csv
import struct




########
# class
########
# queue element is [content,mid,final_priority,deliverable,sender, [[turn,suggestor],[turn,suggestor]]]
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
    
    def queue_find_index(self,mid):
        index = -1
        for i in range(len(self.queue)):
            if (self.queue[i])[1] == mid:
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
        while (len(self.queue)>0 and self.queue[0][3] == 1):
            popdata = self.queue[0]
            self.queue.remove(self.queue[0])
            # print ("deliver:")
            print (popdata)
            



###########
# variable
###########

# key is node_id, whose type is tring. my_node_id's type is also string
other_node_ip = dict()    
other_node_port = dict()
send_conn = dict()

# no key
receive_conn = []
receive_prepared = []

# myqueue and my turn
myqueue = hold_queue()
my_turn = 0
myterminate = 0

# lock
queue_lock = threading.Lock()
myturn_lock = threading.Lock()




###################
# message function
###################
def askMessage(message_content, mid, send_priority):
    string = "ask"+"|" + message_content + "|" + mid + "|" + send_priority +"|" 
    return string.ljust(128,' ')

def feedbackMessage(proposed_priority, mid, suggestor):
    string = "feedback"+"|"+ proposed_priority + "|" + mid+ "|" + suggestor +"|"
    return string.ljust(128,' ')

def decidedMessage(agreed_priority, suggested_id, mid):
    string = "decided"+"|"+agreed_priority+"|"+suggested_id + "|" + mid+"|"
    return string.ljust(128,' ')


##########
# readtxt
##########
def readtxt(filename):
    global other_node_ip
    global other_node_port
    f=open(filename, 'r', encoding='utf-8')
    for line in f:
        data_line = line.strip("\n").split()
        if len(data_line) == 1:
            node_number = int(data_line[0])
        else:
            node_id = (data_line[0])[4]
            ip = data_line[1]
            port = int(data_line[2])

            other_node_ip[node_id] = ip
            other_node_port[node_id] = port
            
    return node_number


#################
# establish_send
#################
def establish_send(node_num):
    global other_node_ip
    global other_node_port
    global send_conn

    while (len(send_conn) != node_num):
        for key in other_node_port:
            try:
                port = other_node_port[key]
                addr = other_node_ip[key]
                con = socket.socket()
                con.connect((addr, port))
                send_conn[key] = con
                # print(key+" is established")
            except:
                continue
    # print("send_conn established with node_number:"+str(node_num))


###########################
# receive_message_thread
###########################
def receive_message(i):
    global myqueue
    global my_nodeid
    global my_turn
    global node_num

    global receive_conn
    global send_conn


    con = receive_conn[i]
    while not myterminate:
        receive_prepared [i] = 1
        data = con.recv(128).decode('utf-8')
        if (len(data)!=128):
            data += con.recv(128-len(data)).decode('utf-8')
            
        datalist = data.split("|")
        msg_type = datalist[0]
        # print(data.strip(" "))

        if (msg_type == "ask"):
            msg_content = datalist[1]
            mid = datalist[2]
            original_priority = int(datalist[3])

            # update queue
            # [content,mid,final_priority,deliverable,sender,[]]
            queue_lock.acquire()
            myqueue.queue_append([msg_content,mid,original_priority,0,int(mid[0]),[]])
            myqueue.sort_queue()
            # myqueue.displayqueue()
            queue_lock.release()

            # add the my_turn
            myturn_lock.acquire()
            my_turn += 1
            cur_turn = my_turn
            myturn_lock.release()

            # send feedback message
            # feedbackMessage(proposed_priority, mid, suggestor)
            feedbackmessage = feedbackMessage(str(cur_turn), mid, my_nodeid)
            target_node = mid.split(" ")[0]
            single_send(target_node, feedbackmessage)


        if (msg_type == "feedback"):
            #feedbackMessage(proposed_priority, mid, suggestor)
            proposed_priority = datalist[1]
            mid = datalist[2]
            suggestor = int(datalist[3])

            # update queue
            # [content,mid,final_priority,deliverable,sender,[]]
            queue_lock.acquire()
            index = myqueue.queue_find_index(mid)
            if index == -1: 
                print(" cannot find the messages")
                return -1
            myqueue.feedbacklist_append(index, [int(proposed_priority),int(suggestor)])
            if (myqueue.feedbacklist_check(index) == node_num+1):
                # multicast
                myqueue.feedbacklist_sort(index)
                agreed_priority = myqueue.feedbacklist_agreed_priority(index)
                suggested_id = myqueue.feedbacklist_suggested_id(index)
                mid = mid
                decidedmessage = decidedMessage(str(agreed_priority), str(suggested_id), mid)
                multicast_message(decidedmessage)

                # update queue value
                myqueue.queue_update_element(index,agreed_priority,1,suggested_id)
                myqueue.sort_queue()
                myqueue.check_and_remove()

            # myqueue.displayqueue()
            queue_lock.release()

        if (msg_type == "decided"):

            priority = int(datalist[1])
            mid = datalist[3]
            suggestor_id = int(datalist[2])
            # update priority and suggested_id
            queue_lock.acquire()
            index = myqueue.queue_find_index(mid)
            if (index == -1):
                print ("fail")
                return -1
            myqueue.queue_update_element(index,priority,1,suggestor_id)
            myqueue.sort_queue()  # must sort immediatly
            # myqueue.displayqueue()
            # check if deliverable, remove from queue
            myqueue.check_and_remove()
            queue_lock.release()

            
        
        # print("receive "+data)
    
    
###########################
# send_message thread
############################
def multicast_message(fix_row):
    global send_conn
    for key in send_conn:
        (send_conn[key]).send("{0}".format(fix_row).encode("utf-8"))


def single_send(key,fix_row):  # key is a string
    global send_conn
    (send_conn[key]).send("{0}".format(fix_row).encode("utf-8"))




#######
# main
#######
def main():
    global my_turn
    global myqueue
    global my_nodeid
    global myterminate

    global other_node_ip
    global node_num 
    global receive_conn
    global send_conn


    if len(sys.argv) != 4:
        print("invalid input")
        return -1
    
    print('logger is waiting to connect.')

    # my node name
    name = sys.argv[1]
    my_nodeid = name[4]

    # readtxt
    node_num = readtxt(sys.argv[3])
    print(node_num,len(send_conn),other_node_ip)

    # establish send connection
    send_conn_thread = threading.Thread(target=establish_send, args=(node_num,))
    send_conn_thread.start()
    
    # establish the receive socket
    mynode = socket.socket()
    mynode.bind(('127.0.0.1', int(sys.argv[2])))
    mynode.listen(20)
    while (len(receive_conn)!=node_num):
        s,addr = mynode.accept()
        receive_conn.append(s)
        receive_prepared.append(0)

    # wait until send connection established already
    while (len(send_conn)!=node_num or len(receive_conn)!=node_num):
        continue


    # receive message thread
    for i in range(0,node_num):
        receive_thread = threading.Thread(target=receive_message, args=(i,))
        receive_thread.start()

    # wait until receive thread prepared already
    while True:
        sum = 0
        for i in range(0,node_num):
            sum = sum + receive_prepared[i]
        # print("the prepared receive thread is:"+str(sum))
        if (sum == node_num):
            break
    

    # send message thread
    for row in sys.stdin:
        fix_row = row.strip('\n')
        time.sleep(0.0001)
        mid = my_nodeid +" "+ str(time.time())

        # update turn, store cur_turn
        myturn_lock.acquire()
        my_turn +=1
        cur_turn = my_turn
        myturn_lock.release()

        # update queue
        queue_lock.acquire()
        myqueue.queue_append([fix_row,mid,cur_turn,0,int(my_nodeid),[]])
        myqueue.feedbacklist_append(myqueue.queue_find_index(mid), [cur_turn,int(my_nodeid)])
        myqueue.sort_queue()
        # myqueue.displayqueue()
        queue_lock.release()

        # prepare the message and start the send thread
        askmessage = askMessage( fix_row, mid, str(cur_turn))
        multicast_message(askmessage)



if __name__ == '__main__':
        main()

        

