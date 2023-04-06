import socket
import sys
import time
import threading
import csv





########
# class
########
# queue element is [content,mid,final_priority,deliverable,suggestor, [[turn,suggestor],[turn,suggestor]]]
class hold_queue:
    def __init__(self):
        self.queue = []
   
    def displayqueue(self):
        print (self.queue)
    
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
        self.queue.sort(key=lambda x:(-x[2], -x[3], -x[4]))
        # smaller final_priority will be at the end
        # smaller deliverable will be at the end
        # smaller suggestor will be at the end
        
    def feedbacklist_append(self, index, proposed_info):
        (self.queue[index][5]).append(proposed_info)
        
    def feedbacklist_check(self, index):
        return len(self.queue[index][5])

    def feedbacklist_sort(self, index):
        (self.queue[index][5]).sort(key=lambda x:(x[0],x[1]))





###########
# variable
###########

# key is node_name
other_node_ip = dict()    
other_node_port = dict()
send_conn = dict()

# no key
receive_conn = []
receive_prepared = []

# myqueue and my turn
myqueue = hold_queue()
my_turn = 0

# lock
queue_lock = threading.Lock()
myturn_lock = threading.Lock()




###################
# message function
###################
def askMessage(message_content, mid, send_priority):
    string = "ask"+"|" + message_content + "|" + mid + "|" + send_priority +"|"
    return string

def feedbackMessage(proposed_priority, mid, suggestor):
    string = "feedback"+"|"+ proposed_priority + "|" + mid+ "|" + suggestor +"|"
    return string

def decidedMessage(agreed_priority, mid):
    string = "decided"+"|"+ agreed_priority + "|" + mid
    return string


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
            node_name = data_line[0]
            ip = data_line[1]
            port = int(data_line[2])

            other_node_ip[node_name] = ip
            other_node_port[node_name] = port
            
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
                send_conn[port] = con
                print(key+" is established")
            except:
                continue
    print("send_conn established with node_number:"+str(node_num))


#################
# receive_message
#################
def receive_message(i):
    global myqueue
    global myname
    global my_turn

    global receive_conn
    global send_conn


    con = receive_conn[i]
    while True:
        receive_prepared [i] = 1
        data = con.recv(1024).decode('utf-8')
        if (len(data) == 0):
            continue
        datalist = data.split("|")
        msg_type = datalist[0]

        if (msg_type == "ask"):
            msg_content = datalist[1]
            mid = datalist[2]
            original_priority = int(datalist[3])

            # store the information into local queue, 
            # [content,mid,final_priority,deliverable,suggestor,[]]
            myqueue.queue_append([msg_content,mid,original_priority,0,1,[]])
            myqueue.sort_queue()

            # add the my_turn
            myturn_lock.acquire()
            my_turn += 1
            myturn_lock.release()

            # send feedback message
            # feedbackMessage(proposed_priority, mid, suggestor)
            feedbackmessage = feedbackMessage(str(my_turn), mid, myname)
            single_send(mid.split(" ")[0],feedbackmessage)


        if (msg_type == "feedback"):
            continue

            
        
        print("receive "+data)
    
    
#################
# send_message
#################
def multicast_message(fix_row):
    global send_conn
    for key in send_conn:
        (send_conn[key]).send("{0}".format(fix_row).encode("utf-8"))

def single_send(key,fix_row):
    global send_conn
    for key1 in send_conn:
        if (str(key1)==key):
            (send_conn[key1]).send("{0}".format(fix_row).encode("utf-8"))



#######
# main
#######
def main():
    global my_turn
    global myqueue
    global myname

    global other_node_ip
    global node_num 
    global receive_conn
    global send_conn


    if len(sys.argv) != 4:
        print("invalid input")
        return -1
    
    print('logger is waiting to connect.')

    # my node name
    myname = sys.argv[1]

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
        print("the prepared receive thread is:"+str(sum))
        if (sum == node_num):
            break
    
    # send message thread
    # for key in send_conn:
    #     (send_conn[key]).send("{0} - {1} connected \n".format(time.time(),sys.argv[1]).encode("utf-8"))
    for row in sys.stdin:
        fix_row = row.strip('\n')
        mid = myname +" "+ str(time.time())

        myturn_lock.acquire()
        my_turn +=1
        myturn_lock.release()

        askmessage = askMessage( fix_row, mid, str(my_turn))

        print("send "+fix_row)
        multicast_thread = threading.Thread(target=multicast_message, args=(askmessage,))
        multicast_thread.start()

    while True:
        pass


if __name__ == '__main__':
        main()

        

