#!/usr/bin/env python2.7
#---------------------------------------------------------------------------------------------------------------------

#Name: LTE_main.py
#LTE band scanning, decoding and eNodeB configuration for eNodeB emulation
#Author: Sandra Ng Yi Ling 2017

#--------------------------------------------------------------------------------------------------------------------

#NOTES
#Only use USRP B210 to run this because srsLTE only works with USRP
#Run this from bin_folder_sandra
#suitable for python 2.7 only - libmich is only supported in py2.7
#tested in ubuntu 16.04 LTS environment - os.system commands are linux based commands
#not backwards compatible or cross-platform compatible

#---------------------------------------------------------------------------------------------------------------------

#SCRIPT FLOW:
#1. Create working folder for this scan
#2. Display freq bands supported in location, relevant freqs and earfcns
#3. Set scanning params
#4. Open srsLTE cell_search to look for cells
#5. List out cells found for user reference
#6. Choose to decode channel, record or quit
#7. Start decoding MIBs and SIBs
	#7a. Creating file and writing params, piping MIB output into file
	#7b. Decode SIB in the form of a hex message, now able to decode directly using libmich and write to file
#8. Filter out decoded MIBs and SIBs into main params file
#9. Open OPENLTE ENB emulator to generate config file / check if config file is there
#10. Generate new parameters using other script
#11. Run OPENLTE ENB emulator using new params

#---------------------------------------------------------------------------------------------------------------------

#OPEN-SOURCE SOFTWARE / DEPENDENCIES:
# - openLTE - LTE band scanner and eNodeB emulator
# - srsLTE - LTE band scanner, UE emulator and eNodeB emulator - have to give the appropriate permissions for the executables or else you have to run this within the directory of the executables /srsLTE/build/srslte/examples/
# - libmich - Python 2.7 library for decoding ASN.1 encoded messages
#*ensure that these can run independently first before running this script i.e. ensure that the dependencies for these open-source software are installed first before this script can be run

#---------------------------------------------------------------------------------------------------------------------

#IMPORT IMPORTANT LIBRARIES AND MODULES
import os
import sys
import datetime
import time
from libmich.asn1.processor import *

#INTRODUCTION AND LOGGING SCRIPT TIME
print 'This script scans LTE bands and saves the scan.\nIt is also able to decode the MIBs and SIBs of selected LTE channels and configures the eNB that you want to emulate.\n'

start_time=datetime.datetime.now()

#---------------------------------------------------------------------------------------------------------------------

#1. CREATE WORKING FOLDER FOR THIS SCAN
while True:
	print '*****SCANNING MODE*****\n'
	prompt_new='New scan (N) or is there an existing directory available? (E)\n'
	ans_new=raw_input(prompt_new)
	if ans_new=='N':
		while True:
			prompt0='Input name of working directory for this scan? (No spaces allowed, use underscores.)\n'
			path=raw_input(prompt0)
			if os.path.exists(path) is False:
				#makes directory with permissions granted
				os.mkdir(path, 0755)
				print 'Folder created!\n'
				break
			else:
				print 'Folder already exists!\n'
				continue
		break
	elif ans_new=='E':
		while True:
			prompt_dir='Name of folder?\n'
			path=raw_input(prompt_dir)
			if os.path.exists(path) is True:
				print 'Now working in selected folder.\n'
				break
			else:
				print 'Folder does not exist: either create a new directory or enter a correct folder name.\n'
				continue
		break
	else:
		print 'Not a valid option!\n'
		continue

#---------------------------------------------------------------------------------------------------------------------

#2. DISPLAY FREQ BANDS SUPPORTED IN LOCATION, RELEVANT FREQS AND EARFCNS 
SG_LTE_frequency_bands=[3,7,8]
string=', '.join(str(i) for i in SG_LTE_frequency_bands)
print 'LTE frequency bands supported in your location: ' + string + '\n'
dict_bands=dict([('3','1207-1943'),('7','2775-3425'),('8','3457-3793')])
dict_freq=dict([('3','1805-1880'),('7', '2620-2690'),('8','925-960')])
#lookup
while True:
	prompt_lookup='Do you want to look up the dl_earfcn_list? (Y) or (N)\n'
	answer_lookup=raw_input(prompt_lookup)
	if answer_lookup=='Y':
		while True:
			prompt_band='Which band? (3, 7, 8)\n'
			answer_band=raw_input(prompt_band)
			if (int(answer_band) in SG_LTE_frequency_bands) is True:
				print ('Start EARFCN - End EARFCN: '+ dict_bands[answer_band])
				print ('Start freq - End freq (MHz): '+ dict_freq[answer_band])
				break
			else:
				print 'Not within the bands supported!\n'
				continue
		break
	elif answer_lookup=='N':
		break
	else:
		print 'Not a valid option!\n'
		continue

#---------------------------------------------------------------------------------------------------------------------

#3. SET SCANNING PARAMS
while True:
	prompt1='Which band do you want to scan?\n'
	band_no=raw_input(prompt1)
	if (int(band_no) in SG_LTE_frequency_bands) is False:
		print 'Not within the bands supported!\n'
		continue
	else:
		break
#limit band
while True:
	prompt2='Begin scanning from which EARFCN? (if want to scan the whole band, input the start earfcn)\n'
	prompt3='End scan at which EARFCN? (if want to scan the whole band, input the end earfcn)\n'
	x=raw_input(prompt2)
	y=raw_input(prompt3)
#simple sanity check
	if int(y)<int(x):
		print 'Endpoint must be larger than start point!\n'
		continue	
	else:
		break
#creating scanning file and printing params to file
date_time_of_scan=datetime.datetime.now().strftime('%m%d-%H%M')

open_file_cmd= path + '/'+ 'scan-' + date_time_of_scan + '.dat'
f = open(open_file_cmd,'w+')
params='Opening srsLTE Cell Search with default RF args and gain 70dB, importing parameters: ' + 'band: ' + band_no + ', ' + 'start_earfcn: ' + x + ', ' + 'end_earfcn: ' + y + '\n'
f.write(params)
print params
time.sleep(1)

#---------------------------------------------------------------------------------------------------------------------

#4.OPEN SRSLTE CELL_SEARCH TO LOOK FOR CELLS
cmd_scan_band='cell_search ' + '-b ' + band_no + ' -s ' + x + ' -e ' + y + '|' + 'tee -a ' + open_file_cmd
os.system(cmd_scan_band)
f.close()

#---------------------------------------------------------------------------------------------------------------------

#5. LIST OUT CELLS FOR USER REFERENCE
print '\nHere is the list of cells found:\n'
f1=open(open_file_cmd,'r')
find_str1='PSS power' #Phrase that appears on discovered LTE Cells
lines=f1.readlines()
cells=[]
for line in lines:
	if line.find(find_str1)!=-1:
		print line
		cells.append(line)
if cells==[]:
	print 'No cells found!\n'
f1.close()

#---------------------------------------------------------------------------------------------------------------------

#6. CHOOSE TO DECODE CHANNEL, RECORD OR QUIT (includes link to openLTE to record)
while True:
	prompt_decode='Do you want to decode the channel in real time (D), record a file from selected channel (R) or quit here (Q)?\n'
	ans_decode=raw_input(prompt_decode)
	if ans_decode=='D':
		print '\n*****REAL-TIME DECODING MODE*****\n'
		break
	elif ans_decode=='R':
		#open new terminal to connect to localhost
		os.system('gnome-terminal')
		#OPEN scanner
		print '\n*****RECORDING MODE*****\n'
		print 'Opening OPENLTE File Recorder...\n'
		time.sleep(1)
		os.system('gnome-terminal')
		os.system('LTE_file_recorder')
		print 'Finished recording!'
		while True:
			prompt_7='Do you want to decode the recorded file? Y/N\n'
			ans_7=raw_input(prompt_7)
			if ans_7=='Y':
				print 'Starting OPENLTE File Scanner...\n'
				time.sleep(1)
				prompt_decoded_file_name='What is the full path of the bin file?\n'
				ans_decoded_file_name=raw_input(prompt_decoded_file_name)
				openlte_scan_cmd='LTE_fdd_dl_file_scan.py -d gr_complex ' + '"' + ans_decoded_file_name + '"' #need to output the decoded MIB somewhere!!!
				os.system(openlte_scan_cmd)
				#use usrp to record -- use fs=15.36
				print 'MIB decoded! Continuing with program...\n'
				break
			elif ans_7=='N':
				print 'Continuing with program...\n'
				break
			else:
				print 'Not a valid option!\n'
				continue
		break
	elif ans_decode=='Q':
		end_time=datetime.datetime.now()
		print '\nCompleted within {}'.format(end_time - start_time)
		print 'Shutting down LTE_main.py...\n'
		time.sleep(1)		
		sys.exit()
	else:
		print 'Not a valid option!\n'
		continue

#---------------------------------------------------------------------------------------------------------------------

#7. START DECODING MIBs and SIBs
while True:
	prompt4='Input (M) for manual input of earfcn/freq to be decoded or (Q) to quit program.\n'
	opt=raw_input(prompt4)	
	if opt=='M':
		while True:
			#7a. CREATING FILE AND WRITING PARAMS, PIPING MIB OUTPUT INTO FILE			
			prompt5='Input frequency to decode. For MHz, input the exponent as e6\n'
			freq=raw_input(prompt5)
			print '\nWARNING: Press CTRL-C to continue once MIB is decoded.\n'
			#NEED TO QUIT IMMEDIATELY AFTER MIB IS DECODED BECAUSE USELESS DATA WILL BE RECORDED
			time.sleep(2)
			print 'Start MIB scanning...\n'
			time.sleep(1)
			open_mib_file_cmd= path + '/'+ 'scan-' + date_time_of_scan + '-mib-' +freq+ '.dat'
			original=sys.stdout
			f2 = open(open_mib_file_cmd,'w+')
			sentence='Scanning MIBs for frequencies found in scan-'+date_time_of_scan+'.dat\n'+'For frequency: ' + freq +'\n\n'
			f2.write(sentence)
			sys.stdout=original
			scanning_cmd='pdsch_ue '+'-f '+ freq + ' | ' + 'grep -v -m 17 "MIB"' + ' | '+'tee -a ' + open_mib_file_cmd 
			os.system(scanning_cmd)
			f2.close()
			print '\nNow scanning SIBs.\n\nWARNING: Press CTRL-C to continue once SIB is decoded.\n'
			#NEED TO QUIT IMMEDIATELY AFTER SIB IS DECODED
			time.sleep(2)
			print 'Start SIB scanning...\n'
			time.sleep(1)
			#7b. DECODE SIB IN FORM OF A HEX MESSAGE
			open_sib_file_cmd= path + '/'+ 'scan-' + date_time_of_scan + '-sib-' +freq+ '.dat'
			original=sys.stdout
			f3 = open(open_sib_file_cmd,'w+')
			sentence='Scanning SIBs for frequencies found in scan-'+date_time_of_scan+'.dat\n'+'For frequency: ' + freq +'\n\n'
			f3.write(sentence)			
			sys.stdout=original
			scanning_cmd_sib='cell_measurement '+'-f '+ freq + ' | ' + 'grep -v -m 12 "RSSI"' + ' | ' + 'tee -a ' + open_sib_file_cmd
			os.system(scanning_cmd_sib)
			f3.close()
			#8 FILTER OUT MIBS AND SIBS INTO MAIN PARAMS
			f4=open(open_mib_file_cmd,'r')
			f5=open(open_sib_file_cmd,'r')
			open_mainfile_cmd= path + '/'+ 'scan-' + date_time_of_scan + '-mainparams-' +freq+ '.dat'
			f6=open(open_mainfile_cmd,'w+')
			sentence_2='Parameters for cell: '+freq+ ' MHz, from band '+band_no+'\n\n'+'MIB:\n\n'
			f6.write(sentence_2)
			find_str_cellid='Cell ID:'
			find_str_nof_ports='Nof ports:'
			find_str_cp='CP:'
			find_str_PRB='PRB:'
			find_str_PHICH='PHICH'
			find_str_SFN='SFN:'
			lines_mib=f4.readlines()
			list_phrases=[find_str_cellid,find_str_nof_ports,find_str_cp,find_str_PRB,find_str_PHICH,find_str_SFN]
			for line1 in lines_mib:
				for i in list_phrases:
					if line1.find(i)!=-1:
						f6.write(line1)
			f6.write('\nSIB:\n\n')
			find_str_sib='Payload' #Phrase that appears on SIB params
			lines_sib=f5.readlines()
			for line2 in lines_sib:
				if line2.find(find_str_sib)!=-1:
					f6.write(line2)
			f6.close()
			print '\n\nFiles created in working folder '+path+': scan, MIB, SIB and mainparams\n'
			f4.close()
			f5.close()
			f6.close()
			#use ASN.1 library libmich to decode SIB message
			print 'LIBMICH: Now decoding SIB hex stream...\n'
			prompt_SIB='Input C to continue or input Q to quit if no SIB payload has been printed:\n'
			ans_SIB=raw_input(prompt_SIB)
			if ans_SIB=='Q':
				end_time=datetime.datetime.now()
				print '\nCompleted within {}'.format(end_time - start_time)
				print 'Shutting down LTE_main.py...\n'
				time.sleep(1)		
				sys.exit()
			elif ans_SIB=='C':
				#extract the line again but don't output and extract the hexstream only
				f8=open(open_mainfile_cmd,'r')
				find_str_sib1='Payload' #Phrase that appears on SIB params
				lines_sib_2=f8.readlines()
				for line3 in lines_sib_2:
					if line3.find(find_str_sib1)!=-1:
						pass
				print 'Extracting hexstream payload...\n'
				time.sleep(1)
				start=line3.find('[')+1
				end=line3.find(']')
				new_line=line3[start:end]			
				#remove spaces from hex stream
				print 'Converting hex stream into readable format...\n'
				time.sleep(1)		
				chars=[]
				for c in new_line:
					chars.append(c)
				chars=[x for x in chars if x !=' ']
				new_SIB=''.join(i for i in chars)
				print 'Now decoding...\n'
				time.sleep(1)
				GLOBAL.clear()
				load_module('RRCLTE') #load lte module
				#next 3 lines are just the SIB encoded format defined by 3GPP
				ASN1.ASN1Obj.CODEC=PER
				PER.VARIANT='U' #unaligned
				pdu=GLOBAL.TYPE['BCCH-DL-SCH-Message'] #SIB found in this channel
				buf=new_SIB.decode('hex')
				pdu.decode(buf)
				pdu()
				f7=open(open_mainfile_cmd,'a')
				print '\nWriting decoded SIB to main params file...\n'
				original=sys.stdout
				sys.stdout=f7
				show(pdu)
				sys.stdout=original
				f7.close()
				print 'SIB data written to main params file successfully. Press Enter to continue.'
				raw_input()
				GLOBAL.clear()
			else:
				print 'Not a valid option!\n'
				continue
			while True:
				prompt6='Continue scanning (C), emulate a cell (E) or quit (Q)?\n'
				ans=raw_input(prompt6)
				if ans=='C':
					break
				elif ans=='Q':
					end_time=datetime.datetime.now()
					print '\nCompleted within {}'.format(end_time - start_time)
					print 'Shutting down LTE_main.py...\n'
					time.sleep(1)		
					sys.exit()
				elif ans=='E':
					#9 OPEN OPENLTE ENB EMULATOR AND GENERATE CNFG FILE
					print 'Opening OPENLTE LTE_fdd_enodeb... Generate the config file and shutdown first!\n'
					time.sleep(1)					
					os.system('gnome-terminal')
					os.system('LTE_fdd_enodeb')
					print 'Config file created! Write desired parameters to config file:\n'
					time.sleep(1)			
					#10. WRITE NEW PARAMS INTO ENB EMULATOR - run the configuration script
					os.system('LTE_enodeb_writeconfig.py')
					#11. REOPEN OPENLTE ENB EMULATOR
					print 'Reopening OPENLTE LTE_fdd_enodeb with new params...\n'
					time.sleep(1)					
					os.system('gnome-terminal') #control port
					os.system('gnome-terminal') #debug interface
					os.system('LTE_fdd_enodeb')
					#log end time and close
					end_time=datetime.datetime.now()
					print '\nCompleted within {}'.format(end_time - start_time)
					print 'Shutting down LTE_main.py...\n'
					time.sleep(1)		
					sys.exit()
				else:
					print 'Not a valid option!\n'
					continue
			continue			
		break
	elif opt=='Q':
		end_time=datetime.datetime.now()
		print '\nCompleted within {}'.format(end_time - start_time)
		print 'Shutting down LTE_main.py...\n'
		time.sleep(1)		
		sys.exit()
	else:
		print 'Not a valid option!\n'
		continue
	break

#---------------------------------------------------------------------------------------------------------------------

