#!/usr/bin/env python2.7
#---------------------------------------------------------------------------------------------------------------------

#Name: LTE_enodeb_writeconfig.py
#Use this script to write parameters into basic_config.dat in the same style as the official config file, once official config file is created after setting the flag, write over with basic_config.dat
#Author: Sandra Ng Yi Ling 2017

#---------------------------------------------------------------------------------------------------------------------

#SCRIPT FLOW:
#1. Introduction and import of important libraries
#2. Create dictionary for options and the parameters that they refer to
#3. Read lines from writable config file, search for relevant line with parameter in qn, rewrite the line with new parameter value
#4. Rewrite official config file (the one that the program reads from) with the writable config file

#---------------------------------------------------------------------------------------------------------------------

#NOTES
#Ensure that the official config file is generated independently by LTE_fdd_enodeb before this script is run or else there will be an IOError where the script cannot find the config file to write to

#---------------------------------------------------------------------------------------------------------------------

#1. INTRODUCTION AND LIB IMPORT
import os
print '*****WRITE CONFIG FILE MENU*****\n'

#---------------------------------------------------------------------------------------------------------------------

#2. Dictionaries for allowed inputs / things to refer to
dict_params=dict([('B','bandwidth'),('Ba','band'),('D','dl_earfcn'),('A','n_ant'),('P','n_id_cell'),('MCC','mcc'),('MNC','mnc'),('C','cell_id'),('T','tracking_area_code'),('TX','tx_gain'),('RX','rx_gain'),('De','debug_level')])

#---------------------------------------------------------------------------------------------------------------------

#filenames that won't change
basicconfig='basic_config.dat'
configfilename='/tmp/LTE_fdd_enodeb.cnfg_db'

#---------------------------------------------------------------------------------------------------------------------

#function to find config file, find chosen param and change param
def change_params(param,value):
	find_str=dict_params[param]
	f_basicconfig=open(basicconfig,'r')
	config_lines=f_basicconfig.readlines()
	if param=='Ba':
		index=1 #limit the index to the band line so that the bandwidth is not changed
	else:
		for line in config_lines:
			if line.find(find_str)!=-1:
				index=config_lines.index(line)
	#can take this part out of the loop because should only be changing one line	
	config_lines.pop(index)
	new_line=dict_params[param]+' '+value+'\n' #must be in the same format as the one in the official config
	config_lines.insert(index,new_line)
	f_basicconfig=open(basicconfig,'w')
	for i in config_lines:
		f_basicconfig.write(i)

#---------------------------------------------------------------------------------------------------------------------

#3. FIND BASIC CONFIG FILE - saved in bin, writable, won't disappear (DON'T DELETE!)
#manually copy from config template if you accidentally change/delete the file
#Write params
while True:
	prompt_change='Choose which parameters you want to change in this order:\n-Bandwidth (B)\n-Band (Ba)\n-DL earfcn (D)\n-No. of antennae (A)\n-Physical Cell ID (P)\n-MCC (MCC)\n-MNC (MNC)\n-Global Cell ID (C)\n-Tracking area code (T)\n-Transmitter gain (TX)\n-Receiver gain (RX)\n-Debug level (De)\nIf you are finished with the configuration, enter (F).\n\n'
	ans_change=raw_input(prompt_change)
	if ans_change=='B':
		prompt_bandwidth='Bandwidth? (1.400, 3.000, 5.000, 10.00, 15.00 or 20.00)\n'
		bandwidth=raw_input(prompt_bandwidth)
		change_params(ans_change,bandwidth)
		continue
	elif ans_change=='Ba':
		prompt_band='Band? (3, 7 or 8)\n'
		band=raw_input(prompt_band)
		change_params(ans_change,band)
	elif ans_change=='D':
		prompt_dlearfcn='DL EARFCN?\n'
		dlearfcn=raw_input(prompt_dlearfcn)
		change_params(ans_change,dlearfcn)
		continue
	elif ans_change=='A':
		prompt_ant='Number of antennae?\n'
		ant=raw_input(prompt_ant)
		change_params(ans_change,ant)
		continue
	elif ans_change=='P':
		prompt_pci='Physical Cell ID?\n'
		n_id_cell=raw_input(prompt_pci)
		change_params(ans_change,n_id_cell)
		continue
	elif ans_change=='MCC':
		prompt_mcc='MCC?\n'
		mcc=raw_input(prompt_mcc)
		change_params(ans_change,mcc)
		continue
	elif ans_change=='MNC':
		prompt_mnc='MNC?\n'
		mnc=raw_input(prompt_mnc)
		change_params(ans_change,mnc)
		continue
	elif ans_change=='C':
		prompt_cellid='Global Cell ID?\n'
		cellid=raw_input(prompt_cellid)
		change_params(ans_change,cellid)
		continue
	elif ans_change=='T':
		prompt_tac='Tracking Area Code?\n'
		tac=raw_input(prompt_tac)
		change_params(ans_change,tac)
		continue
	elif ans_change=='TX':
		prompt_txg='Transmitter gain?\n'
		txg=raw_input(prompt_txg)
		change_params(ans_change,txg)
		continue
	elif ans_change=='RX':
		prompt_rxg='Receiver gain?\n'
		rxg=raw_input(prompt_rxg)
		change_params(ans_change,rxg)
		continue
	elif ans_change=='De':
		prompt_de='Debug level? (Usual options: pdcp rrc mme rb, Other options: rlc gw user timer iface msgq radio phy mac)\n'
		debuglevel=raw_input(prompt_de)
		change_params(ans_change,debuglevel)
	elif ans_change=='F':
		break
	else:
		print 'Not a valid parameter!\n'
		continue

#--------------------------------------------------------------------------------------------------------------------

#4. WRITE ENTIRE NEW CONFIG FILE TO OFFICIAL CONFIG FILE
os.chdir('../../../tmp/') #move out to find official config file in tmp folder
f_old=open(configfilename,'r')
old_config_lines=f_old.readlines()
os.chdir('../home/dsta/bin') #come back to bin to read back the config file
f_basicconfig=open(basicconfig,'r')
config_lines=f_basicconfig.readlines()
old_config_lines=config_lines
f_new=open(configfilename,'w')
for i in old_config_lines:
	f_new.write(i)
f_new.close()

