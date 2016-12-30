# -*- coding: gbk -*-
import csv
import types
import os
import json
import sys
sys.path.append("..")
import xlrd
import re
import shutil

XLS_DIR=""
CSV_DIR=""

def initPath():
	global XLS_DIR
	global CSV_DIR
	XLS_DIR = checkPath(sys.argv[1])
	CSV_DIR = checkPath(sys.argv[2])

def checkPath(path):
        if os.name == 'nt': #windows os
            ok = path.endswith('\\')
            if ~ok:
                return path + '\\'
            return path
        else:              #unix or linux
            ok = path.endswith('/')
            if ~ok:
                return path + '/'
            return path

def refreshFolder(directory):
	if os.path.exists(directory):
		shutil.rmtree(directory)
	os.makedirs(directory)	

class ConvertExcelToCsv:
	def ConvertValue(self, lst, nThRow):
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
	 
	 
	def excludeWrongCase(self, rawRow):
		d = dict()
		for i in range(len(rawRow)):
			if rawRow[i] in d:
				print 'repeated variable: ', rawRow[i]
				raise Exception('repeated variable name!')
			else:
				d[rawRow[i]] = 0
		
	def csv_from_excel(self, excel_file, ignore_line, out_path):
		print excel_file
		src_file= XLS_DIR + excel_file # + ".xls"
		workbook = xlrd.open_workbook(src_file)
		worksheet = workbook.sheet_by_index(0)
		row1 = self.ConvertValue(worksheet.row_values(0), 0)
		row5 = self.ConvertValue(worksheet.row_values(4), 0)
		self.excludeWrongCase(row5)
		
		staitcFileName = row1[0]
		#your_csv_file.write(codecs.BOM_UTF8)
		if staitcFileName == '':
			print excel_file
			raise Exception('file name is nill!')
		csv_file_name = out_path+''.join([staitcFileName,'.csv'])
		your_csv_file = open(csv_file_name, 'wb')
		wr = csv.writer(your_csv_file, quoting=csv.QUOTE_NONE)
		
		line=0
		firstListContent = ''
		typeList = []
		for rownum in xrange(worksheet.nrows):
			line=line+1
			if line <= ignore_line:
				continue
			ret =self.ConvertValue(worksheet.row_values(rownum), rownum)
			if line == 4:
				firstListContent = ret
				typeList = ret
			elif line == 5:
				#your_csv_file.write('	'.join(ret))    #write the second line first, then the second.
				#your_csv_file.write('	'.join('\n'))
				targetVariableName = []
				variablesName = ret
				for i, type in enumerate(typeList):
					if self.isSplitCase(type) == True:
						tmpList = self.extractTypeName(variablesName[i])
						for j, varName in enumerate(tmpList):
							tmpList[j] = self.beautifyFormation(varName)
						targetVariableName.extend(tmpList)
					else:
						name = variablesName[i]
						targetVariableName.append(self.beautifyFormation(name))	
				self.writeToObject(your_csv_file, targetVariableName)
			else:
				targetVal = []
				valList = ret
				for i, type in enumerate(typeList):
					if self.isSplitCase(type) == True:
						targetVal.extend(self.extractContent(type, valList[i]))
					else:
						targetVal.append(valList[i])	
				self.writeToObject(your_csv_file, targetVal)

		your_csv_file.close()

	def isSplitCase(self, rawString):
		return (rawString.find(';') > 0) and (rawString.find('$')<0)

	def writeToObject(self, fp, rawList):
		for val in rawList:
			fp.write('	' + str(val))
		fp.write('\n')
		
	def beautifyFormation(self, nameStr):
		tmpName = []
		for i in range(len(nameStr)):
			if nameStr[i] >= 'A' and nameStr[i] <= 'Z':
				tmpName.append('_')
				tmpName.append(nameStr[i].lower())
			else:
				tmpName.append(nameStr[i])
		return ''.join(tmpName) 
	
	def extractTypeName(self, rawString):
		typeList = []
		typeName = []
		for i in range(len(rawString)):
			if (((rawString[i]) == '_') or (ord(rawString[i]) >= 48) and (ord(rawString[i]) <=57)) or ((ord(rawString[i]) >= 65) and (ord(rawString[i]) <=90))  or ((ord(rawString[i]) >= 97) and (ord(rawString[i]) <=122)):
				typeName.append(rawString[i])
				if i+1 == len(rawString):
					#print ''.join(typeName)
					typeList.append(''.join(typeName))
			elif rawString[i] == ';':
				#print ''.join(typeName)
				typeList.append(''.join(typeName))
				typeName[:] = [] #clear content of typeName
		return typeList
		
	def extractContent(self, rawType, rawData):
		typeList = re.split(r'[;]', rawType)
		#print "typeList = ", typeList
		contentList = re.split(r'[_]', str(rawData))
		#print "contentList = ", contentList
		originalContentLength = len(contentList)
		shortNum = len(typeList) - len(contentList)
		#print "shortNum = ", shortNum
		if shortNum > 0:
			for i in range(shortNum):
				index = originalContentLength + i
				if typeList[index].lower() == "string":				
					contentList.append('')
				else:
					contentList.append(0)
		return contentList
		
	def pause(self):
		raw_input_A = raw_input("Generate successfully! Press any key to exit!")
 
if __name__ == "__main__":
    print '--------------Convert excel to csv---------------'
    IGNORE_LINE=3  # these lines will be ignored
    initPath()
    refreshFolder(CSV_DIR)
	
    convert = ConvertExcelToCsv()
    for filename in os.listdir(XLS_DIR):
	#csv_from_excel(unicode(filename, 'gbk'), unicode(outputName, 'gbk'), IGNORE_LINE, CSV_DIR)
	if ((filename[-3:] != 'xls') and (filename[-4:] != 'xlsx')) or (filename[0] == '~'):
	    continue
	convert.csv_from_excel(filename, IGNORE_LINE, CSV_DIR)
    #pause()

