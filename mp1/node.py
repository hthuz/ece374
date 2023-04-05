import socket
import sys
import time
import threading
import csv


global other_node_ip
global other_node_port
global receive_conn
global send_conn

# key is node_name
other_node_ip = dict()    
other_node_port = dict()
send_conn = dict()


# receive_conn don't care about the map relations
receive_conn = []


def readtxt(filename):
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


def establish_send(node_num):
    while (len(send_conn) != node_num):
        for key in other_node_port:
            try:
                port = other_node_port[key]
                addr = other_node_ip[key]
                con = socket.socket()
                con.connect((addr, port))
                send_conn[key] = con
                print(key+" is established")
            except:
                continue
    print("send_conn established with node_number:"+str(node_num))



def receive_message(con):
    while True:
        try:
            data = con.recv(1024).decode('utf-8')
            if (len(data) == 0):
                continue
            # con.send("ack".encode('utf-8'))   # to avoid packet splicing 
            print(data)
        except:
            continue
    
    

def multicast_message(fix_row):
    for key in send_conn:
        print("send to:"+key)
        (send_conn[key]).send("{0}".format(fix_row).encode("utf-8"))
        (send_conn[key]).recv(1024).decode("utf-8")
    

# Description: main function
# input: argv[1] is the nodename, argv[2] is the ip, argv[3] is the port
# output: print the generator time and the message you input
# side effect: send the message to the server, the logger
def main():

    if len(sys.argv) != 4:
        print("invalid input")
        return -1
    
    print('logger is waiting to connect.')

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

    # wait until send connection established already
    while (len(send_conn)!=node_num):
        continue


    # receive message thread
    for i in range(0,node_num):
        print (i)
        conn = receive_conn[i]
        receive_thread = threading.Thread(target=receive_message, args=(conn,))
        receive_thread.start()

    # send message thread
    for key in send_conn:
        (send_conn[key]).send("{0} - {1} connected \n".format(time.time(),sys.argv[1] ).encode("utf-8"))
        # (send_conn[key]).recv(1024).decode("utf-8")
    for row in sys.stdin:
        print ("come here1")
    #     fix_row = row.strip('\n')
    #     print (fix_row)
    #     multicast_thread = threading.Thread(target=multicast_message, args=(fix_row,))
    #     multicast_thread.start()

    while True:
        pass


if __name__ == '__main__':
        main()

        

