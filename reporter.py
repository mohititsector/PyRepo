import schedule
import time
import configparser
from DBConnect import DBConnect
op = ''
#if __name__ == '__main__':

def get_status():
    config = configparser.ConfigParser()
    config.read('db_config')
    '''
    for section in config.sections():
        db_obj = None
        
        try:
            db_obj = DBConnect(user=config[section]['username'], pwd=config[section]['password'],
                               host=config[section]['host_name'], port_no=int(config[section]['port']),
                               service_nm=config[section]['service_name'], enc=config[section]['encoding'],
                               mode=int(config[section]['mode']))
        
        except KeyError:
            db_obj = DBConnect(user=config[section]['username'], pwd=config[section]['password'],
                               host=config[section]['host_name'], port_no=int(config[section]['port']),
                               service_nm=config[section]['service_name'], enc=config[section]['encoding'],
                               mode=None)

        if db_obj.get_open_mode():
             print(f"Database {config[section]['service_name']} on server {config[section]['host_name']} is up and running")
			
             op = op + "|"+"Database : {config[section]['service_name']} Status : Running"
			
        else:
            print(f"Database {config[section]['service_name']} on server {config[section]['host_name']} is down ")
			
            op = op + "|"+"Database : {config[section]['service_name']} Status : Running"

        for db_item in db_obj.get_manager_status():
            for m_item in ['Conflict Resolution Manager', 'Internal Manager', 'Output Post Processor', 'Standard Manager']:
                if not db_item[m_item]:
                    print(f" {m_item} is NOK")
                    op = op + "|"+" {m_item} is Not Running "
                else:
                    print(f" {m_item} is OK")
                    op = op + "|"+" {m_item} is Running "

        wf_status = db_obj.get_workflow_mailer_status()
        print(wf_status)
        db_obj.close()
        del (db_obj)
        '''
    op = "D3531O|Status : Running|Conflict Resolution Manager : Running|Internal Manager : Not Running|Output Post Processor : Not Running|Standard Manager : Not Running \n D3527O|Status : Running|Conflict Resolution Manager : Running|Internal Manager : Running|Output Post Processor : Running|Standard Manager : Running:::AppNode1:Running|AppNode2:Running|AppNode3:Not Running \n D1567T|Status : Running|Conflict Resolution Manager : Running |Internal Manager : Running |Output Post Processor : Running |Standard Manager : Running \n D1571O|Status : Running|Conflict Resolution Manager : Running |Internal Manager : Running |Output Post Processor : Running |Standard Manager : Running \n D3511P|Status : Running|Conflict Resolution Manager : Running |Internal Manager : Running |Output Post Processor : Running |Standard Manager : Running |Workflow : RUNNING"
    return op
        

def c_job():
    ''' st for taking the databases status as a sigle string
        "db separeted by \n services separated by pipe symbol , fields separated by : and apps data separated by :::"
    '''
    #st = "D3531O|Status : Running|Conflict Resolution Manager : Running|Internal Manager : Not Running|Output Post Processor : Not Running|Standard Manager : Not Running \n D3527O|Status : Running|Conflict Resolution Manager : Running|Internal Manager : Running|Output Post Processor : Running|Standard Manager : Running:::AppNode1:Running|AppNode2:Running|AppNode3:Not Running \n D1567T|Status : Running|Conflict Resolution Manager : Running |Internal Manager : Running |Output Post Processor : Running |Standard Manager : Running \n D1571O|Status : Running|Conflict Resolution Manager : Running |Internal Manager : Running |Output Post Processor : Running |Standard Manager : Running \n D3511P|Status : Running|Conflict Resolution Manager : Running |Internal Manager : Running |Output Post Processor : Running |Standard Manager : Running |Workflow : RUNNING"

    st = get_status()

    # db logs string splint into lines each line expose the one db and its running status
    inst = ((st.split("\n")))    

    # object jsn and op for storing operational output of given string
    jsn = op = ''

    #Follow are Loops split the each db log into tokens(each token represents the each service in header db)
    for line in inst:

        # if condition for to find the apps node and db node (if block for apps and else block for database)
        # AppNode for future enhancement
        if line.find(":::") > 0:
            AppNode = line.split(":::")
            #print (AppNode[0])
            #print (AppNode[1])

        # Following else block for database tokens
        else:
            tokens = (line.split("|"))
            k = 0
            i=jsn = ""

            ''' Following loop for finding the fields of attributes and performing
              mutiple string operations for generating json data to reporter.json
              '''

            for i in tokens :
                # if condition to find the header and append the json format data
                if k == 0 :
                    #print (i.strip())
                    k += 1
                    jsn += "\""+i+"\":{"

                # else for find the sevices and append the json format data
                else :    
                    for l in i.split(":"):
                        jsn += "\""+l+"\":"
                    jsn = jsn.rstrip(":")+","
            op += (jsn.rstrip(",")+"},")


    # Create the json file and push the proccesed data
    import json
    st = json.loads("{"+op.rstrip(",")+"}")
         
    j_object = json.dumps(st, indent = 4)
     
    with open("reporter.json", "w") as out: 
            out.write(j_object) 
    print(j_object)
    
    
schedule.every(1/30).minutes.do(c_job)

while 1:
    schedule.run_pending()
    time.sleep(1/30)