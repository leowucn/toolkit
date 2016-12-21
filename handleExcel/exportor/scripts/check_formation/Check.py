# encoding=utf-8
import struct
import re
import os
import sys
import xlrd
import time

reload(sys)  
sys.setdefaultencoding('utf-8')

class Check:
	def __init__(self, xlsFullPathName):

		workbook = xlrd.open_workbook(xlsFullPathName)
		worksheet = workbook.sheet_by_index(0)
		row1 = self.ConvertValue(worksheet.row_values(0))
		row2 = self.ConvertValue(worksheet.row_values(1))
		row3 = self.ConvertValue(worksheet.row_values(2))
		row4 = self.ConvertValue(worksheet.row_values(3))
		row5 = self.ConvertValue(worksheet.row_values(4))

		print xlsFullPathName
		self.excludeRepeatedCase(row5)

		if row1[0] == '': 
			errStr = '!!!!!!!! ', 'File name is blank!', ' !!!!!!!!!!'
			print errStr
		
		for k in range(2, worksheet.nrows):
			row_data  = worksheet.row_values(k)
			for j in range(len(row4)):
				if row_data[j] == '':
					errStr = '!!!!!!!! ' + "Blank data, row: " + str(k+1) + ", column: " + str(j+1) + ' !!!!!!!!!!'
					print errStr
		
				typeString = row4[j].lower()
				cellvalue = self.ConverCell(typeString, row_data[j], writeValue)
		self.excludeRepeatedCase(row5)
		
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
		
		
	def excludeRepeatedCase(self, rawRow):
		d = dict()
		for i in range(len(rawRow)):
			if rawRow[i] in d:
				print '!!!!!!!!!! repeated variable: ', rawRow[i] , '!!!!!!!!!!!!'
				
			else:
				d[rawRow[i]] = 0

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
		

check = Check(sys.argv[1]);