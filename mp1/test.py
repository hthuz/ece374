import threading
import sys


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


jk = 0

def multicast_message(a,):
    global myname
    print(myname,jk)


def main():
    global myname
    global jk
    jk = jk+1
    myname = sys.argv[1]
    myqueue = hold_queue()
    myqueue.queue_append(["content1","node1 12i3923",2,0,1,[]])
    myqueue.queue_append(["content2","node2 12i393",3,0,3,[]])
    myqueue.queue_append(["content3","node2 12i3923",2,1,1,[]])
    myqueue.queue_append(["content4","node1 12i393",4,0,3,[]])
    myqueue.displayqueue()
    print("\n\n\n")
    index = myqueue.queue_find_index("node1 12i3923")
    print(index)
    if (index!=-1):
        myqueue.queue_update_element(index,3,1,1)
    myqueue.displayqueue()
    myqueue.sort_queue()
    print("\n\n\n")
    myqueue.displayqueue()
    print("\n\n\n")

    index2 = myqueue.queue_find_index("node1 12i3923")
    myqueue.feedbacklist_append(index2,[3,1])
    myqueue.feedbacklist_append(index2,[3,3])
    myqueue.feedbacklist_append(index2,[1,7])

    if(myqueue.feedbacklist_check(index2) ==3):
        myqueue.feedbacklist_sort(index2)
    
    myqueue.displayqueue()

    a =1
    multicast_thread = threading.Thread(target=multicast_message, args=(a,))
    multicast_thread.start()


if __name__ == '__main__':
        main()
