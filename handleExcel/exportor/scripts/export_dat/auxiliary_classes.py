# -*- coding: gbk -*-
import struct
import time


class Log:
	def __init__(self, prefix, mode='a+', stdout=True):
		self.stdout = stdout
		self.fp = open(self.get_analyze_file_name(prefix), mode)

	def output(self, string):
		if self.stdout:
			self.fp.write(string+'\n')
			self.fp.flush()

	def close(self):
		self.fp.flush()
		self.fp.close()

	def get_analyze_file_name(self, prefix):
		curtime = time.time()
		filename = prefix+time.strftime('_%Y%m%d_%H.txt', time.localtime(curtime))
		return filename


class WriteValueToFile:
	def __init__(self):
		pass

	def write_string(self, fp, data):
		data = data.decode("gbk").encode("utf-8")
		data_len = len(data)
		value = struct.pack("!H%ds" % data_len, data_len, data)
		fp.write(value)

	def write_unicode(self, fp, data):
		#print type(data)
		data = data.encode("utf-8")
		data_len = len(data)
		value = struct.pack("!H%ds" % data_len, data_len, data)
		fp.write(value)
		
	def write_byte(self, fp, data):
		value = struct.pack("B", data)
		fp.write(value)
		
	def write_short(self, fp, data):
		value = struct.pack("!H", data)
		fp.write(value)

	def write_int(self, fp, data):
		value = struct.pack("!i", data)
		fp.write(value)

	def write_float(self, fp, data):
		value = struct.pack("!f", data)
		fp.write(value)

	def is_null_str(self, data):
		if isinstance(data, str) and data == "":
			return True
		return False
