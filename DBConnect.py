import cx_Oracle
import configparser

class DBConnect(object):
    op = ""

    def __init__(self, user, pwd, host='localhost', port_no=1521, service_nm='DB', enc='UTF-8',
                 mode=cx_Oracle.SYSDBA):
        self.__user = user
        self.__password = pwd
        self.__encoding = enc
        self.__dsn = cx_Oracle.makedsn(host=host, port=port_no, service_name=service_nm)
        self.__mode = mode
        self.__conn = self.get_conn()

    def get_conn(self):
        try:
            if self.__mode:
                conn = cx_Oracle.connect(user=self.__user, password=self.__password, dsn=self.__dsn,
                                         encoding=self.__encoding, mode=self.__mode)
            else:
                conn = cx_Oracle.connect(user=self.__user, password=self.__password, dsn=self.__dsn,
                                         encoding=self.__encoding)

            return conn

        except (cx_Oracle.OperationalError, cx_Oracle.DatabaseError, cx_Oracle.InterfaceError) as error:
            print(f"{self.__user}-{error}")
            return None

    def get_open_mode(self):
        db_status = 0
        if self.__conn:
            cur = self.__conn.cursor()
            cur.execute(r'select open_mode from v$database')
            db_data = cur.fetchall()[0][0]
            if db_data.strip() == 'READ WRITE':
                db_status = 1
                return db_status
        else:
            return db_status

    def get_manager_status(self):
        output = []
        if self.__conn:
            cur = self.__conn.cursor()
            cur.execute(r'''select "USER_CONCURRENT_QUEUE_NAME","RUNNING_PROCESSES","MAX_PROCESSES" FROM fnd_concurrent_queues_vl where USER_CONCURRENT_QUEUE_NAME in ('Conflict Resolution Manager' ,'Internal Manager','Standard Manager','Output Post Processor')''')
            db_data = cur.fetchall()
            db_dict = dict()
            for item in db_data:
                db_dict[item[0]] = False
                if (item[0] == 'Conflict Resolution Manager' or item[0] == 'Internal Manager') and (item[1] == item[2]) and (item[2]==1) and (item[2]>0):
                    db_dict[item[0]] = True
                elif (item[0] == 'Output Post Processor') and (item[1] == item[2]) and (item[2] <= 6) and (item[2]>0):
                    db_dict[item[0]] = True
                elif (item[0] == 'Standard Manager') and (item[1] == item[2]) and (item[2] <=30) and (item[2]>0):
                    db_dict[item[0]] = True
            output.append(db_dict)
        return output

    def get_workflow_mailer_status(self):
        if self.__conn:
            cur = self.__conn.cursor()
            query = '''select component_status from fnd_svc_components where component_id = (select component_id from fnd_svc_components where component_name = 'Workflow Notification Mailer')'''
            cur.execute(query)
            db_data = cur.fetchall()
            return db_data[0][0]
        else:
            print('connection error')
            return None

    def get_disk_space(self):
        pass



    def close(self):
        if self.__conn:
            self.__conn.close()


#if __name__ == '__main__':
def get_report():
    op = ''
    config = configparser.ConfigParser()
    config.read('db_config.txt')
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
        
            op = op+f"{config[section]['service_name']}"+"|name:"+f"{config[section]['service_name']}"+"|status:active"

        else:

            op = op+f"{config[section]['service_name']}"+"|name:"+f"{config[section]['service_name']}"+"|status:inactive"


        for db_item in db_obj.get_manager_status():
            for m_item in ['Conflict Resolution Manager', 'Internal Manager', 'Output Post Processor',
                           'Standard Manager']:
                if not db_item[m_item]:
                    if "Conflict Resolution Manager" == f"{m_item}" :
                        op=op+"|"+"CRM"+":inactive"
                    if "Internal Manager" == f"{m_item}" :
                        op=op+"|"+"IM"+":inactive"
                    if "Output Post Processor" == f"{m_item}" :
                        op=op+"|"+"OPP"+":inactive"
                    if "Standard Manager" == f"{m_item}" :
                        op=op+"|"+"SM"+":inactive"

                else:
                    if "Conflict Resolution Manager" == f"{m_item}":
                        op=op+"|"+"CRM"+":active"
                    if "Internal Manager" == f"{m_item}":
                        op=op+"|"+"IM"+":active"
                    if "Output Post Processor" == f"{m_item}":
                        op=op+"|"+"OPP"+":active"
                    if "Standard Manager" == f"{m_item}":
                        op=op+"|"+"SM"+":active"
		
        op = op+"\\n"
        db_obj.close()
        del (db_obj)
    print("function : ",((op).rstrip("\\n")))
    return ((op).rstrip("\\n"))

def get_details(name):
    config = configparser.ConfigParser()
    config.read('db_config.txt')
    p = ""
    for section in config.sections():
        if config[section]['service_name'] == name:
                approle = config[section];
                p = ("\"App\":\""+(((str(approle).split(":")[1]).rstrip(">")).split("-")[0]) +"\""+",\"Role\":\""+(((str(approle).split(":")[1]).rstrip(">")).split("-")[1])+"\","+"\"Hostname\":\""+config[section]['host_name'] + "\"")
    return p

def c_job():
    st = str(get_report())
    ''' st for taking the databases status as a sigle string
        "db separeted by \n services separated by pipe symbol , fields separated by : and apps data separated by :::"
    '''
    #st = "D3531O|status:active|CRM:inactive|IM:inactive|OPP:inactive|SM:inactivee|FS:85%|WF:E_inactive\nD3527O|status:active|CRM:inactive|IM:active|OPP:active|SM:active|FS:85%|WF:E_active\nD1567T|status:active|CRM:inactive|IM:inactive|OPP:inactive|SM:inactive|Workflow:active"

    config = configparser.ConfigParser()
    config.read('db_config.txt')

    # print(get_details("D1567T"))

    # db logs string splint into lines each line expose the one db and its running status
    inst = ((st.split("\\n")))
    print("Line 185 :" ,inst)
    # object jsn and op for storing operational output of given string
    jsn = op = ''

    # Follow are Loops split the each db log into tokens(each token represents the each service in header db)
    for line in inst:

        # if condition for to find the apps node and db node (if block for apps and else block for database)

        if line.find(":::") > 0:
            AppNode = line.split(":::")
            # print (AppNode[0])
            # print (AppNode[1])

        # Folloeing else block for database tokens
        else:
            tokens = (line.split("|"))
            k = 0
            i = jsn = ""

            ''' Following loop for finding the fields of attributes and performing
              mutiple string operations for generating json data to reporter.json
              '''

            for i in tokens:
                # if condition to find the header and append the json format data
                if k == 0:
                    # print (i.strip())
                    k += 1
                    jsn += "\"" + i + "\":{" + get_details(i) + ","
                    print(i)
                # else for find the sevices and append the json format data
                else:
                    for l in i.split(":"):
                        jsn += "\"" + l + "\":"
                    jsn = jsn.rstrip(":") + ","
            op += (jsn.rstrip(",") + "},")
    print(op)

    # Create the json file and push the proccesed data
    import json

    st = json.loads("{" + op.rstrip(",") + "}")

    j_object = json.dumps(st, indent=4)

    with open("/home/antilles/project/dashboard/static/data.json", "w") as out:
        out.write(j_object)
import schedule, time
if __name__ == '__main__':
    schedule.every(1/10).minutes.do(c_job)

    while 1:
        schedule.run_pending()
        time.sleep(1/10)

