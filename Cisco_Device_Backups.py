#!/usr/bin/python2.7
####################################################
#     Device Backup Script for Cisco Devices       #
####################################################
# Required Modules #
import ftplib
import datetime
import sys
import paramiko
from time import sleep

########################################
# Credentials and save_path initiation #
########################################
# Device credentials (common on all devices) 
# Sample info, change accordingly
uname = 'Cisco'
pswd = 'cisco123'
# FTP access details
ftp_server_ip = '10.10.10.51'
ftp_root = '/Network_Devices_Backup/'
ftp_uname = 'Cisco' 
ftp_pswd = 'cisco%40123' #Use HEX code for symbols in the pswd
ftp_pswd_simple = 'cisco@123' #Simple password without HEX code
# TFTP access details
tftp_server_ip = '10.10.10.51'
tftp_root = '/Network_Devices_Backup/'

####################################################
#               Device Classes                     #
# Edit only when applies to whole device class     #
####################################################

#################################################################
# SSH Enabled devices without the need to enter enable password #
#################################################################


def device_class1(ip, uname, pswd, sleep_dur):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(ip, port=22, username=uname, password=pswd)
        print '***Connected to ' + ip + '\t*******'
        stdin, stdout, stderr = ssh.exec_command('copy run ftp://' + ftp_uname + ':' + ftp_pswd + '@' + ftp_server_ip
                                                 + ftp_root + string_date + '/')
        stdin.write('\n\n\n')
        sleep(sleep_dur)
        stdin.flush()
        stdout.flush()
        stderr.flush()
        ssh.close()
    except:
        print 'cannot connect to ' + ip
    return

###################################################################
# SSH enabled devices with file transfer mode as tftp with enable #
###################################################################


def device_class2(ip, uname, pswd, filename):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(ip, port=22, username=uname, password=pswd)
        print '***Connected to ' + ip + '\t*******'
        channel = ssh.invoke_shell()
        channel.send('en\n')
        sleep(3)
        channel.send(pswd + '\n')
        sleep(3)
        channel.send('copy run tftp://' + tftp_server_ip + tftp_root + string_date + '/' + filename + '\n\n\n\n')
        sleep(10)
        ssh.close()
    except:
        print 'cannot connect to ' + ip
    return

##########################################################
# SSH enabled WLC devices with file transfer mode as ftp #
##########################################################


def device_class3(ip, uname, pswd, filename):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(ip, port=22, username=uname, password=pswd)
        print '***Connected to ' + ip + '\t*******'
        channel = ssh.invoke_shell()
        sleep(3)
        channel.sendall(uname + '\n')
        sleep(3)
        channel.sendall(pswd + '\n')
        sleep(3)
        channel.sendall('transfer upload datatype config\n')
        sleep(1)
        channel.sendall('transfer upload mode ftp\n')
        sleep(1)
        channel.sendall('transfer upload serverip ' + ftp_server_ip + '\n')
        sleep(1)
        channel.sendall('transfer upload filename ' + filename + '\n')
        sleep(1)
        channel.sendall('transfer upload path ' + ftp_root + string_date + '/' + '\n')
        sleep(1)
        channel.sendall('transfer upload username ' + ftp_uname + '\n')
        sleep(1)
        channel.sendall('transfer upload password ' + ftp_pswd_simple + '\n')
        sleep(1)
        channel.sendall('transfer upload start\n')
        sleep(1)
        channel.sendall('y')
        sleep(40)
    except:
        print 'cannot connect to ' + ip
    ssh.close()
    return


###############################################################################
# Date captured to create backup folder name on FTP Server
string_date = str(datetime.date.today())
# Create Backup Folder on FTP server
try:
    ftp = ftplib.FTP(ftp_server)
    ftp.login(ftp_uname,ftp_pswd_simple)
except Exception, e:
    print e
    print ('Cannot access FTP server. Cannot proceed further.\n')
    sys.exit()
else:
    ftp.cwd(ftp_root)
    ftp_filelist= []
    ftp.retrlines('NLST',ftp_filelist.append)
    if string_date not in ftp_filelist:
        ftp.mkd(string_date)


###############################################################################
# Add your devices here
# D1:10.10.10.11_Router1
device_class1('10.10.10.11', uname, pswd, 3) # the last variable is the sleep duration, adjust accordingly
# D2:10.10.10.13_Switch1
device_class1('10.10.10.13', uname, pswd, 3)
# D3:10.10.20.15_Firewall
device_class2('10.10.20.15', uname, pswd, 'Firewall-confg')
# D4:10.10.10.26_WLC
device_class3('10.10.10.26', uname, pswd, 'WLC-confg')
