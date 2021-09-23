#################################################################################################
#################################################################################################
                                                                           ######################
######################  Author         : Pinninti Sateesh Kumar            ######################
######################  Name           : stats.py                          ######################
######################  Description    : To get the server load statistics ######################
######################  Config         : Create cron at REBOOT             ######################
######################                                                      
#################################################################################################
#################################################################################################

import os,sys,subprocess
import time
import requests

def monitor():
    # To get the root mount point disk utility
    usage = subprocess.Popen(["df -h /"],shell=True,stdout=subprocess.PIPE)
    stdout,stderr =  usage.communicate()

    # To get the apache webserver service information
    service = subprocess.Popen(["service httpd24-httpd status"],shell=True,stdout=subprocess.PIPE)
    st,stderr =  service.communicate()

    sstatus = ''
    
    # Find the apache webserver is running or not from service information data
    for line in st.splitlines():
            if "Active: active (running)" in line:
                    sstatus = "[ INFO ] : Apache web server is Running on DRDO application node [ tdf.drdo.gov.in ]"
            elif "Active: inactive (dead)" in line:
                    sstatus = "[ ERROR ] : Apache web server is NotRunning on DRDO application node [ tdf.drdo.gov.in ]"

    print("*"*150)

    counter = 0
    
    # Checking disk health
    for token in stdout.split():
            if "%" in token :
                    if counter ==  1:
                            if 80 < int(token.strip("%")):
                                    disk_info="[ CRITICAL ] : Current /root mount point is reached maximum level "+token
                                    note = "[ NOTE ] : It will impact to load the site [ tdf.drdo.gov.in ]"
                            elif 40 < int(token.strip("%")):
                                    disk_info="[ WARNNING ] : Current /root mount point is reached threshold level "+token
                                    note = "[ NOTE ] : It will impact to load the site [ tdf.drdo.gov.in ]"
                            else:
                                    disk_info="[ INFO ] : Current /root reached "+token
                                    note = "Healthy"
                    counter += 1
    print(sstatus+disk_info)
    print("*"*150)
    os.system("echo " +"_____________________________________________________________________________________________"+ " > /root/myspace/report.txt")
    os.system("echo " + sstatus + " >> /root/myspace/report.txt")
    os.system("echo " + disk_info + " >> /root/myspace/report.txt")
    os.system("echo " +note + " >> /root/myspace/report.txt")
    os.system("echo " +"______________________________________________________________________________________________"+ " >> report.txt")
    #os.system("mailx -S smtp='relay.nic.in' -r 'no-replay@gov.in' -s 'DRDO WebServer Health Check' -v 'satish@redmattertech.com','bhagat@redmattertech.com','rohit@redmattertech.com','avani@redmattertech.com' < /root/myspace/report.txt"
    
    #Mailx is a OS Linbrary to send an email through linux raw command.
    os.system("mailx -S smtp='relay.nic.in' -r 'no-replay@example.in' -s 'DRDO WebServer Health Check' -v 'satish@mail.com','bhagat@mail.com','rohit@mail.com','avani@mail.com' < /root/myspace/report.txt")

while 1:
    #schedule.run_pending()
    time.sleep(300)
    monitor()

