# encoding=utf8
import struct
import re
import os
import sys
import xlrd
import time

reload(sys)  
sys.setdefaultencoding('utf8')

class ParseXls:
	def __init__(self, xlsFullPathName):
		self.xlsFullPathName = xlsFullPathName
		self.staitcFileName = ''
		self.colSize = 0
		self.rowSize = 0
		self.type = []
		self.name = []
		self.desc = []
		self.structList = []
		self.mapStruct = {}
		self.serializeStructs = ''
		
		workbook = xlrd.open_workbook(self.xlsFullPathName)
		worksheet = workbook.sheet_by_index(0)
		row1 = self.ConvertValue(worksheet.row_values(0))
		row2 = self.ConvertValue(worksheet.row_values(1))
		row3 = self.ConvertValue(worksheet.row_values(2))
		row4 = self.ConvertValue(worksheet.row_values(3))
		row5 = self.ConvertValue(worksheet.row_values(4))

		self.excludeRepeatedCase(row5)

		if row1[0] == '':
			print '!!!!!!!! ', 'File name is nill!', ' !!!!!!!!!!'
			time.sleep(1000)
			raise Exception(errStr)
		self.staitcFileName = self.beautifyName(row1[0])
		
		for i in range(len(row2)):
			if row2[i] == "1":
				strName = row4[i].lower()
				#if strName == "intarray" or strName == "intarray2":
				#	strName = "String"
				self.excludeBlankData(row4[i], 4) 
				self.excludeBlankData(row5[i], 5) 
					
				if self.isSplitCase(strName):
					typeList = strName.split(';')
					variablesList = row5[i].split(';')
					if len(typeList) != len(variablesList):
						print '!!!!!!!!!!!! ', 'encounter error here. mark 1', '!!!!!!!!!!!!!!!'
						time.sleep(1000)
						raise  Exception(errStr)
					for j in range(len(typeList)):
						type = self.trimEndBlank(typeList[j].lower())
						variable = self.trimEndBlank(variablesList[j])
						desc = self.trimEndBlank(unicode(row3[i], 'gbk'))
						
						self.type.append(type)
						self.name.append(self.beautifyFormation(variable))
						self.desc.append(desc)
				else:
					type = self.trimEndBlank(strName.lower())
					variable = self.trimEndBlank(row5[i])
					desc = self.trimEndBlank(unicode(row3[i], 'gbk'))
					
					self.type.append(type)
					self.name.append(self.beautifyFormation(variable))
					self.desc.append(desc)
		self.colSize = len(self.type)
		self.rowSize = worksheet.nrows - 5
		self.extractStructInfo()
		
	
	def repairType(self, rawType):
		if (rawType.lower() == "byte"):
			return "uint8_t"
		elif (rawType.lower() == "int"):
			return "uint32_t"
		elif (rawType.lower() == "string"):
			return "std::string"
		elif (rawType.lower() == "short"):
			return "uint16_t"
		elif (rawType.lower() == "float"):
			return "double"
		elif (rawType.lower() == "intarray") or (rawType.lower() == "bytearray"):
			return "Array"
		elif (rawType.lower() == "intarray2"):
			return "Array = []"
	def isSplitCase(self, rawString):
		return (rawString.find(';') > 0) and (rawString.find('$')<0) 
	def extractStructInfo(self):
		for i in range(len(self.type)):
			if self.type[i].find('array~') >=0:
				structName = self.extractClassName(self.type[i])
				typeList = self.extractTypeName(self.type[i])
				variablesList = self.extractVariablesName(self.type[i])
				
				structInfo = StructInfo()
				structInfo.structName = structName.lower()
				structInfo.typeList = typeList
				structInfo.variablesList = variablesList
				structInfo.desc = self.desc[i].replace('\n','')
				structInfo.relativeVariableName = self.name[i]
				self.mapStruct[self.name[i]] = structInfo.structName
				
				whetherContinue = False
				for structValue in self.structList:
					if structValue.structName == structName.lower():
						whetherContinue = True
						break
				if whetherContinue:
					continue    #if the class has appeared in self.structList, just continue.
				self.structList.append(structInfo)   #store new structInfo for later use 		

				#print "typeList = ", typeList
				#print "variablesList = ", variablesList
				if len(typeList) != len(variablesList):
					print "encounter some error here. mark 1."
					return 
				
				serializeStruct = ''
				serializeStruct += '\tstruct ' + structInfo.structName + "_t{\n"
				for i in range(len(structInfo.typeList)):
					serializeStruct += '\t\t' + self.repairType(structInfo.typeList[i]) + " " + structInfo.variablesList[i] + ";\n"
				serializeStruct += "\t};\n"
				self.serializeStructs += serializeStruct
		
	def extractClassName(self, rawString):
		classNamePositin = rawString.find('~') + 1
		structName = []
		for i in range(classNamePositin, len(rawString)):
			if (ord(rawString[i]) == 95) or ((ord(rawString[i]) >= 48) and (ord(rawString[i]) <=57)) or ((ord(rawString[i]) >= 65) and (ord(rawString[i]) <=90))  or ((ord(rawString[i]) >= 97) and (ord(rawString[i]) <=122)):
				structName.append(rawString[i])
			else:
				break
		lst = [word[0].upper() + word[1:] for word in ''.join(structName).split()]
		stringClassName = " ".join(lst)
		#stringClassName = self.beautifyFormation(stringClassName)
		stringClassName = stringClassName
		return stringClassName
	def extractTypeName(self, rawString):
		tmpList = []
		typeList = []
		#it seems that the first type name always appears after '$' symble. 
		dollorPositon = rawString.find('$')
		typeName = []
		for i in range(dollorPositon + 1, len(rawString)):
			if ((ord(rawString[i]) >= 48) and (ord(rawString[i]) <=57)) or ((ord(rawString[i]) >= 65) and (ord(rawString[i]) <=90))  or ((ord(rawString[i]) >= 97) and (ord(rawString[i]) <=122)):
				typeName.append(rawString[i])
			else:
				tmpList.append(''.join(typeName))
				break
		#from the second type name, it seems that the type name always appears after ';' symble.
		#find all the position of semicolon in string name.
		semicolonPositinList = [m.start() for m in re.finditer(';', rawString)]
		#print "semicolonPositinList = ",semicolonPositinList
		for semicolonPositin in semicolonPositinList:
			typeName[:] = [] #clear content of typeName
			for j in range(semicolonPositin + 1, len(rawString)):
				if ((ord(rawString[j]) >= 48) and (ord(rawString[j]) <=57)) or ((ord(rawString[j]) >= 65) and (ord(rawString[j]) <=90)) or ((ord(rawString[j]) >= 97) and (ord(rawString[j]) <=122)):
					typeName.append(rawString[j])
				else:
					tmpList.append(''.join(typeName))
					break
					
		for rawType in tmpList:
			#typeList.append(self.repairType(rawType.lower()))
			typeList.append(rawType.lower())
		return typeList 
	#typeString has the form 'array~channel_type$short~map_id;int~x;int~y'
	def extractVariablesName(self, rawString):
		variablesList = []
		variableName = []
		wavePositionList = [m.start() for m in re.finditer('~', rawString)]
		for i in range(len(wavePositionList)):
			if i == 0:
				continue #the first ~ symble is just a mark for the form 'array~channel_type$short~map_id;int~x;int~y'
			variableName[:] = []
			for j in range(wavePositionList[i] + 1, len(rawString)):
				if (ord(rawString[j]) == 95) or ((ord(rawString[j]) >= 48) and (ord(rawString[j]) <=57)) or ((ord(rawString[j]) >= 65) and (ord(rawString[j]) <=90)) or ((ord(rawString[j]) >= 97) and (ord(rawString[j]) <=122)):
					variableName.append(rawString[j])
				else:
					break
			#variablesList.append(self.beautifyFormation(''.join(variableName)))
			variablesList.append(''.join(variableName))
		return variablesList
	def beautifyFormation(self, nameStr):
		tmpName = []
		for i in range(len(nameStr)):
			if nameStr[i] >= 'A' and nameStr[i] <= 'Z':
				tmpName.append('_')
				tmpName.append(nameStr[i].lower())
			else:
				tmpName.append(nameStr[i])
		return ''.join(tmpName)
			
		return nameStr
	def getType(self, colIndex):
		return self.type[colIndex]
	def getName(self, colIndex):
		return self.name[colIndex]
	def getDesc(self, colIndex):
		return self.desc[colIndex]
	def getColSize(self):
		return self.colSize
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
	def excludeRepeatedCase(self, rawRow):
		d = dict()
		for i in range(len(rawRow)):
			if rawRow[i] in d:
				print '!!!!!!!!!! repeated variable: ', rawRow[i] , '!!!!!!!!!!!!'
				time.sleep(1000)
				raise Exception('repeated variable error!')
				
			else:
				d[rawRow[i]] = 0
	def excludeBlankData(self, rawData, row):
		if rawData == '':
			errStr = 'There is blank data in row ' + str(row)
			print '!!!!!!!!!!!! ', errStr, ' !!!!!!!!!!!'
			time.sleep(1000)
			raise Exception(errStr)
		return
	def beautifyName(self, rawString):
		'''convert struct name the form of 'SkillLeader' to the form of 'skill_leader'.'''
		for i in range(1, len(rawString)):
			if (ord(rawString[i]) < 65 and ord(rawString[i]) > 90):
				return  #all of letters of rawString are not uppercase, so return outright.
		structName = []
		structName.append(rawString[0].lower())
		for i in range(1, len(rawString)):
			structName.append(rawString[i].lower())	
			if i + 1 == len(rawString):
				return ''.join(structName)
			if ord(rawString[i+1]) >= 65 and ord(rawString[i+1]) <= 90:
				structName.append('_')
				continue	
	def trimEndBlank(self, rawString):
		return rawString.rstrip()
		

class StructInfo:
	def __init__(self):
		self.structName = ''
		self.typeList = []
		self.variablesList = []
		self.desc = []
		self.relativeVariableName = ''
#dat = Dat("/Users/leowu/test/source/StaticErrorCodeInfo.dat")
#parseXls = ParseXls("X:\\clientTools\\tools\\craft_overall.xls")
'''
print "---------------------"
for i in range(len(dat.name)):
	print dat.name[i]
print "---------------------"
for i in range(len(dat.type)):
	print dat.type[i]
print "---------------------"
for i in range(len(dat.desc)):
	print dat.desc[i]
print "---------------------"
print dat.classesSerialize
'''
