# -*- coding: gbk -*-
import csv
import types
import time
import os
import StringIO
import zlib
import json
import sys
import re
import auxiliaryClasses
import xlrd
import shutil

XLS_DIR=""
DAT_DIR=""

def initPath():
	global XLS_DIR
	global DAT_DIR
	XLS_DIR = sys.argv[1]
	DAT_DIR = sys.argv[2]

def refreshFolder(directory):
	if os.path.exists(directory):
		shutil.rmtree(directory)
	os.makedirs(directory)

class Generator:
	def GenDatFile(self, excel_file):
		src_file= XLS_DIR + excel_file # + ".xls"
		print src_file
		workbook = xlrd.open_workbook(src_file)
		worksheet = workbook.sheet_by_index(0)
		row1 = self.ConvertValue(worksheet.row_values(0))
		row2 = self.ConvertValue(worksheet.row_values(1))
		row3 = self.ConvertValue(worksheet.row_values(2))
		row4 = self.ConvertValue(worksheet.row_values(3))
		row5 = self.ConvertValue(worksheet.row_values(4))
		
		
		self.excludeRepeatedCase(row5)
		
		staitcFileName = row1[0]
		if staitcFileName == '':
			errStr = '!!!!!!!! ', 'File name is nill!', ' !!!!!!!!!!'
			print errStr
			time.sleep(1000)
			raise Exception(errStr)
		#print staitcFileName
		
		lstType = []
		lstName = []
		#lstDesc = []
		file_name = DAT_DIR + staitcFileName + ".dat"
		fp = file(file_name,"wb")

		writeValue = auxiliaryClasses.WriteValueToFile()
		writeValue.WriteString(fp,staitcFileName)
		#WriteString(data_fp, staitcFileName)
		for i in range(len(row2)):
			if row2[i] == "1":
			
				self.excludeBlankData(row4[i], 4) 
				self.excludeBlankData(row5[i], 5) 
			
				typeString = row4[i].lower()
				if typeString == "intarray" or typeString == "intarray2":
					typeString = "string"

				lstType.append(typeString)
				lstName.append(row5[i])
				#lstDesc.append(row3[i])

		fileOffsetBeforeWriteColSize = fp.tell()
		colSize = len(lstName)
		writeValue.WriteByte(fp, colSize)
		rowSize = worksheet.nrows - 5
		#WriteShort(data_fp, rowSize)
		writeValue.WriteShort(fp, rowSize)
		
		additionColumnsSize = 0
		typeList = []
		variablesList = []
		for i in range(0, colSize):
			if self.isSplitCase(lstName[i].lower()):
				typeList = self.extractType(lstType[i], 2)
				variablesList = self.extractVariablesName(lstName[i].lower(), 1)
				if len(typeList) != len(variablesList):
					errStr = '!!!!!!!! ', 'encounter some error here. mark 4.', ' !!!!!!!!!!'
					print errStr
					time.sleep(1000)
					raise Exception(errStr)
				if len(typeList) > 0:
					additionColumnsSize += len(variablesList) - 1 
				typeList[:] = []
				variablesList[:] = []

		fileOffsetAfterWriteMeta = fp.tell()  #get the current offset in order to modify column nums as column may be changed
		newColumnsSize = colSize + additionColumnsSize
		if newColumnsSize > colSize:
			fp.seek(fileOffsetBeforeWriteColSize, 0)
			writeValue.WriteByte(fp, newColumnsSize)
			fp.seek(fileOffsetAfterWriteMeta, 0)
		
		for k in range(5, worksheet.nrows):
			row_data  = worksheet.row_values(k)
			for j in range(len(row2)):
				#print "j",j
				if row2[j] != "1": #split case is tackled below, so do not worry here.
					continue
				typeString = row4[j].lower()
				#if IsNullStr(row_data[j]):
					#CheckLog.output("文件 %s ID:%d FieldName:%s is NULL"%(excel_file, int(row_data[0]), row5[j]))
				self.excludeBlankData(row_data[j], k)
				cellvalue = self.ConverCell(typeString, row_data[j], writeValue)
				if typeString == "int" :
					#print("int", row_data[j])
					writeValue.WriteInt(fp, cellvalue)
				elif typeString == "byte":
					#print("byte", row_data[j])
					writeValue.WriteByte(fp, (int)(cellvalue))
				elif typeString == "short":
					writeValue.WriteShort(fp, (int)(cellvalue))
				elif typeString == "float":
					writeValue.WriteFloat(fp, cellvalue)
				elif typeString == "byte":
					writeValue.WriteByte(fp, cellvalue)
				elif typeString == "string" or typeString == "intarray" or typeString == "intarray2" or typeString == "bytearray":
					#print("string", row_data[j])
					writeValue.WriteUnicode(fp,cellvalue)
					
				#this is the case where typeString is like 'array~channel_type$short~map_id;int~x;int~y'
				#presume all the type in the special case are int, byte  and short.
				elif (typeString.find('array~') == 0) and (typeString.find('$')+1 != len(typeString)):
					if type(cellvalue).__name__ == 'list':
						typeList = self.extractType(typeString, 1)
						#print "typeList = ",typeList
						#print "values = ", cellvalue
						if len(cellvalue) % len(typeList) != 0:
							errStr = '!!!!!!!! ', 'encounter some error here. mark 1.', ' !!!!!!!!!!'
							print errStr
							time.sleep(1000)
							raise Exception(errStr)
						tupleNum = len(cellvalue)/len(typeList)
						writeValue.WriteByte(fp, tupleNum) #write the length of array~, otherwise it will encounter error when resolve.
						for n in range(len(cellvalue)):
							typeName = typeList[n % len(typeList)]
							#print typeName
							if typeName.lower() == "int":
								writeValue.WriteInt(fp, (int)(cellvalue[n]))
							elif typeName.lower() == "byte":
								writeValue.WriteByte(fp, (int)(cellvalue[n])) #original type is char, this should not be right.	 
							elif typeName.lower() == "short":
								writeValue.WriteShort(fp, (int)(cellvalue[n])) #original type is short, this should not be right.
							elif typeName.lower() == "float":
								writeValue.WriteFloat(fp, (float)(cellvalue[n]))
							elif typeName.lower() == "string":
								writeValue.WriteString(fp, (str)(cellvalue[n]))
				elif self.whetherIsShortcut(typeString):
					typeString = self.getValidStringName(row4, j) #use the type info of previous column which is not shortcut.
					if typeString == '':
						print "encounter some error here, mark 2."
						return
					typeList = self.extractType(typeString, 1)
					if len(cellvalue) % len(typeList) != 0:
							print "encounter some error here. mark 1."
							return
					tupleNum = len(cellvalue)/len(typeList)
					writeValue.WriteByte(fp, tupleNum) #write the length of array~, otherwise it will encounter error when resolve.
					for n in range(len(cellvalue)):
						typeName = typeList[n % len(typeList)]
						#print typeName
						if typeName.lower() == "int":
							writeValue.WriteInt(fp, (int)(cellvalue[n]))
						elif typeName.lower() == "byte":
							writeValue.WriteByte(fp, (int)(cellvalue[n])) #original type is char, this should not be right.	 
						elif typeName.lower() == "short":
							writeValue.WriteShort(fp, (int)(cellvalue[n])) #original type is short, this should not be right.
						elif typeName.lower() == "float":
							writeValue.WriteFloat(fp, (float)(cellvalue[n]))
						elif typeName.lower() == "string":
							writeValue.WriteString(fp, (str)(cellvalue[n]))
				elif self.isSplitCase(typeString):  #this case need split typeString to several types.
					typeList = self.extractType(typeString, 2)
					#print "typeList = ", typeList
					#print 'cellvalue = ', cellvalue
					if len(typeList) != len(cellvalue):
						print 'encounter some error here. mark 5'
					for i in range(len(typeList)):
						if typeList[i] == "int":
							writeValue.WriteInt(fp, (int)(cellvalue[i]))
						elif typeList[i] == "byte":
							value = 0
							if cellvalue[i] == '0.0':
								value = 0
							else:
								value = cellvalue[i]
							writeValue.WriteByte(fp, (int)(value)) #original type is char, this should not be right.	 
						elif typeList[i] == "short":
							writeValue.WriteShort(fp, (int)(cellvalue[i]))	 #original type is short, this should not be right.	 
						elif typeString[i] == "float":
							writeValue.WriteFloat(fp, (float)(cellvalue[i]))
		fp.close()
						
						
	def correctLiteralType(self, rawType):
		if rawType == 'int':
			return 'int'
		elif rawType == 'short':
			return 'int'
		elif rawType == 'string' or rawType == "intarray" or rawType == "intarray2" or rawType == "bytearray":
			return 'String'
		elif rawType == 'byte':
			return 'int'
		elif rawType == 'float':
			return 'Number'
		return rawType

	def isSplitCase(self, rawString):
		return (rawString.find(';') > 0) and (rawString.find('$')<0) and (rawString.find('_')<0) 
						
		
	def getValidStringName(self, rowString, currentColumnIndex):
		for i in range(currentColumnIndex)[::-1]:
			if self.whetherIsShortcut(rowString[i].lower()) != True:
				return rowString[i].lower()

	def whetherIsShortcut(self, stringName):
		#print stringName
		return (stringName.find('$')+1 == len(stringName)) and (stringName.find('array~') >= 0)
		
	#Extract all types from string name.
	def extractType(self, stringName, stringType):
		typeList = []
		if stringType == 1: #array~channel_type$short~map_id;int~x;int~y
			#it seems that the first type name always appears after '$' symble. 
			dollorPositon = stringName.find('$')
			typeName = []
			for i in range(dollorPositon + 1, len(stringName)):
				if ((ord(stringName[i]) >= 48) and (ord(stringName[i]) <=57)) or ((ord(stringName[i]) >= 65) and (ord(stringName[i]) <=90))  or ((ord(stringName[i]) >= 97) and (ord(stringName[i]) <=122)):
					typeName.append(stringName[i])
				else:
					typeList.append(''.join(typeName))
					break
			#from the second type name, it seems that the type name always appears after ';' symble.
			#find all the position of semicolon in string name.
			semicolonPositinList = [m.start() for m in re.finditer(';', stringName)]
			#print "semicolonPositinList = ",semicolonPositinList
			for semicolonPositin in semicolonPositinList:
				typeName[:] = [] #clear content of typeName
				for j in range(semicolonPositin + 1, len(stringName)):
					if ((ord(stringName[j]) >= 48) and (ord(stringName[j]) <=57)) or ((ord(stringName[j]) >= 65) and (ord(stringName[j]) <=90)) or ((ord(stringName[j]) >= 97) and (ord(stringName[j]) <=122)):
						typeName.append(stringName[j])
					else:
						typeList.append(''.join(typeName))
						break
		elif stringType == 2: #byte;int;int
			typeName = []
			for i in range(len(stringName)):
				if ((ord(stringName[i]) >= 48) and (ord(stringName[i]) <=57)) or ((ord(stringName[i]) >= 65) and (ord(stringName[i]) <=90))  or ((ord(stringName[i]) >= 97) and (ord(stringName[i]) <=122)):
					typeName.append(stringName[i])
					if i+1 == len(stringName):
						#print ''.join(typeName)
						typeList.append(''.join(typeName))
				elif stringName[i] == ';':
					#print ''.join(typeName)
					typeList.append(''.join(typeName))
					typeName[:] = [] #clear content of typeName
			
		else:
			print 'encounter some error here. mark 3'
			return 
		return typeList 
		
	def extractVariablesName(self, rawString, extractType):
		variablesList = []
		variableName = []
		if extractType == 1: #the separator symble which indicate the variable name is ';'
			for i in range(len(rawString)):
				if ((ord(rawString[i]) >= 48) and (ord(rawString[i]) <=57)) or ((ord(rawString[i]) >= 65) and (ord(rawString[i]) <=90))  or ((ord(rawString[i]) >= 97) and (ord(rawString[i]) <=122)):
					variableName.append(rawString[i])
					if i+1 == len(rawString):
						#print ''.join(variableName)
						variablesList.append(''.join(variableName))
				elif rawString[i] == ';':
					#print ''.join(variableName)
					variablesList.append(''.join(variableName))
					variableName[:] = [] #clear content of typeName
		return variablesList
			
	def ConverCell(self, typename, data, writeValue):
		if typename == "int" or typename == "byte" or typename == "short":
			try:
				return int(data)
			except:
				errStr = '!!!!!!!! ', 'data type error!', ' !!!!!!!!!!'
				print errStr
				time.sleep(1000)
				raise Exception(errStr)
		elif typename == "string" or typename == "intarray" or typename == "intarray2" or typename == "bytearray":
			if writeValue.IsNullStr(data):
				#print typename, "is none"
				return ""	
			if isinstance(data, unicode):
				return data
			if isinstance(data, float):
				if  ( data == int(data)):
					return "%d"%data
				else:
					return "%f"%data
		elif typename == "float":
			return float(data)
		elif typename.find('array~') == 0:
			contentList = re.split(r'[_;]', data)
			return contentList
		elif self.isSplitCase(typename):
			typeList = re.split(r'[;]', typename)
			#print "typeList = ", typeList
			contentList = re.split(r'[_]', str(data))
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
			
	def excludeRepeatedCase(self, rawRow):  # if the excel file has repeated variable name which reside in the fifth row, then raise exception.
		d = dict()
		for i in range(len(rawRow)):
			if rawRow[i] in d:
				errStr = '!!!!!!!! ', 'repeated variable: ', rawRow[i], ' !!!!!!!!!!'
				print errStr
				time.sleep(1000)
				raise Exception(errStr)
			else:
				d[rawRow[i]] = 0
	def excludeBlankData(self, rawData, row):
		if rawData == '':
			errStr = '!!!!!!!! ', 'There is blank data in row ' + str(row), ' !!!!!!!!!!'
			print errStr
			time.sleep(1000)
			raise Exception(errStr)
		return

	def ConvertValue(self, lst):
		ret=[]
		for v in lst:
			data = v
			if isinstance(v, int):
				data = int(v)
			if isinstance(v, float):
				if v == int(v):
					data = int(v)
				else:
					data = float(v)
			if isinstance(v, unicode):
				data = v.encode("gbk")
			data=str(data)
			ret.append(data)
		return ret
	def pause(self):
		raw_input_A = raw_input("Generate successfully! Press any key to exit!")
	
def main():
	generator = Generator()
	for filename in os.listdir(XLS_DIR):
		if ((filename[-3:] != 'xls') and (filename[-4:] != 'xlsx')) or (filename[0] == '~'):
			continue
		generator.GenDatFile(filename)
	#generator.pause()
		
if __name__ == "__main__":
	initPath()
	refreshFolder(DAT_DIR)
	
	main()
