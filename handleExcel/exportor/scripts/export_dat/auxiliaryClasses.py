# -*- coding: gbk -*-
import struct

class log:
	def __init__(self,prefix,mode = 'a+',stdout = True):
		self.stdout = stdout
		self.fp = open (self.GetAnalyzeFileName(prefix),mode)

	def output(self,str):
		if self.stdout == True:
			self.fp.write(str+'\n')
			self.fp.flush()

	def close(self):
		self.fp.flush()
		self.fp.close()

	def GetAnalyzeFileName(self,prefix):
		curtime=time.time()
		filename=prefix+time.strftime('_%Y%m%d_%H.txt',time.localtime(curtime))
		#filename=prefix + ".csv"
		return filename
	
class WriteValueToFile:	
	def WriteString(self, fp, data):
		#print type(data)
		data = data.decode("gbk").encode("utf-8")
		data_len = len(data)
		value = struct.pack("!H%ds"%data_len, data_len,data)
		fp.write(value)
		
	def WriteUnicode(self, fp,data):
		#print type(data)
		data = data.encode("utf-8")
		data_len = len(data)
		value = struct.pack("!H%ds"%data_len, data_len,data)
		fp.write(value)
		
	def WriteByte(self, fp, data):
		value = struct.pack("B",data)
		fp.write(value)
		
	def WriteShort(self, fp, data):
		value = struct.pack("!H",data)
		fp.write(value)

	def WriteInt(self, fp, data):
		value = struct.pack("!i",data)
		fp.write(value)

	def WriteFloat(self, fp, data):
		value = struct.pack("!f",data)
		fp.write(value)
	def IsNullStr(self, data):
		if isinstance(data, str) and data == "":
			return True
		return False
	