# -*- coding: gbk -*-
import csv
import types
import os
import json
import sys
sys.path.append("..")
import xlrd

XLS_DIR=""
CSV_DIR=""

def initPath():
	global XLS_DIR
	global CSV_DIR
	XLS_DIR = sys.argv[1]
	CSV_DIR = sys.argv[2]

def ConvertValue(lst, nThRow):
	ret=[]
	for v in lst:
		data = v
	
		if isinstance(v, int):
			data = int(v)
		elif isinstance(v, float):
			if v == int(v):
				data = int(v)
			else:
				data = str(v)
				#data = float(v)
		elif isinstance(v, unicode):
			v = v.replace("\r\n"," ")
			v = v.replace("\n"," ")
			v = v.strip()
			#print v
			#print "xxxxx"
			#data = v
			data = v.encode("gbk")
			#print data
		else:		
			if v.strip() == "":
				#print("有空数据")
				#print "lst = ", lst
				if nThRow != 0:
					raise  Exception("有空数据:F_ID为:%d"%lst[0])
				
		data=str(data)
		ret.append(data)
	return ret
 
 
def excludeRepeatedCase(rawRow):
	d = dict()
	for i in range(len(rawRow)):
		if rawRow[i] in d:
			print 'repeated variable: ', rawRow[i]
			raise Exception('repeated variable name!')
		else:
			d[rawRow[i]] = 0
	
 
IGNORE_LINE=3  # these lines will be ignored
def csv_from_excel(excel_file,ignore_line, out_path):
	src_file= XLS_DIR + excel_file # + ".xls"
	if os.path.isfile(src_file) == False:
		raise  Exception("file does not exist!")
	print src_file
	workbook = xlrd.open_workbook(src_file)
	#all_worksheets = workbook.sheet_names()
	#for worksheet_name in all_worksheets:
		#if worksheet_name != "Sheet1":
			#continue
	checkArray = {}
	
	worksheet = workbook.sheet_by_index(0)
	row1 = ConvertValue(worksheet.row_values(0), 0)
	row5 = ConvertValue(worksheet.row_values(4), 0)
	excludeRepeatedCase(row5)
	
	staitcFileName = row1[0]
	if staitcFileName == '':
		print excel_file
		raise Exception('file name is nill!')
	#your_csv_file.write(codecs.BOM_UTF8)
	csv_file_name = out_path+''.join([staitcFileName,'.csv'])
	your_csv_file = open(csv_file_name, 'wb')
	wr = csv.writer(your_csv_file, quoting=csv.QUOTE_NONE)
	line=0
	firstListContent = ''
	for rownum in xrange(worksheet.nrows):
		line=line+1
		if line <= ignore_line:
			continue
		ret = ConvertValue(worksheet.row_values(rownum), rownum)
		if line == 4:
			firstListContent = ret 
		elif line == 5:
			your_csv_file.write('	'.join(ret))    #write the second line first, then the second.
			your_csv_file.write('	'.join('\n'))
			
			your_csv_file.write('	'.join(firstListContent))
			your_csv_file.write('	'.join('\n'))
		else:
			your_csv_file.write('	'.join(ret)) 
			your_csv_file.write('	'.join('\n'))
		
			
		'''
		your_csv_file.write("	".join(ret))
		if ret[0] != '':
			#wr.writerow(ret)
			wr.writerow(ret[0])
			if ret[0] in checkArray:
				raise  Exception("repeat F_ID %s"%ret[0])
			else:
				checkArray[ret[0]] = True
		
		#wr.writerow([unicode(entry).encode("gbk") for entry in worksheet.row_values(rownum)])
		'''
	your_csv_file.close()
	
def pause():
	raw_input_A = raw_input("Generate successfully! Press any key to exit!")
 
if __name__ == "__main__":
	#currentDir = os.getcwd()
	#for filename in os.listdir(currentDir + "\source"):
		#csv_from_excel(unicode('道具表.xls', 'gbk'), unicode('道具表', 'gbk'), IGNORE_LINE, OUT_DIR)
		#outputName = os.path.splitext(os.path.basename(filename))[0]
		#csv_from_excel(unicode(filename, 'gbk'), unicode(outputName, 'gbk'), IGNORE_LINE, OUT_DIR)
	initPath()
	csv_from_excel(unicode("角色总表.xls", 'gbk'), IGNORE_LINE, CSV_DIR)
	#pause()

