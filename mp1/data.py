

msg_start_time_record = dict()
msg_end_time_record = dict()

def bandwidth_draw():

    return


def processing_time_get_table():
    
    # Read data
    f = open('./metrics/time.log','r')
    lines = f.readlines()
    for line in lines:
        line = line.strip("\n")
        linelist = line.split(",")
        msg_id, msg_time =  linelist[0], linelist[2]
        if "start_time" in line:
            msg_start_time_record[msg_id] = msg_time

        if "end_time" in line:
            node_id = linelist[1].split("_")[0]
            if msg_id not in msg_end_time_record.keys():
                msg_end_time_record[msg_id] = {}
            msg_end_time_record[msg_id][node_id] = msg_time


    # Write table header
    timefile = open('./metrics/process_time.csv', 'w')
    timefile.write("node_id,process_time\n")

    # Write table content
    timefile = open('./metrics/process_time.csv', 'a')
    for node_id in msg_end_time_record.keys():
        start_time = msg_start_time_record[node_id]
        all_end_time = max(msg_end_time_record[node_id].values())
        process_time = float(all_end_time) - float(start_time)
        timefile.write(f"{node_id},{str(process_time)}\n")

    return

def processing_time_draw():

    return



if __name__ == "__main__":

    processing_time_get_table()

