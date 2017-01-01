# -*- coding: gbk -*-
import time
import os
import sys
import re
import auxiliary_classes
import xlrd
import shutil

XLS_DIR = ""
DAT_DIR = ""


def init_path():
	global XLS_DIR
	global DAT_DIR
	XLS_DIR = check_path(sys.argv[1])
	DAT_DIR = check_path(sys.argv[2])


def check_path(path):
		# windows os
		if os.name == 'nt':
			ok = path.endswith('\\')
			if ~ok:
				return path + '\\'
			return path
		# unix or linux
		ok = path.endswith('/')
		if ~ok:
			return path + '/'
		return path


def refresh_folder(directory):
	if os.path.exists(directory):
		shutil.rmtree(directory)
	os.makedirs(directory)


class Generator:
	def __init__(self):
		pass

	def gen_dat_file(self, excel_file):
		print excel_file
		src_file = XLS_DIR + excel_file
		workbook = xlrd.open_workbook(src_file)
		worksheet = workbook.sheet_by_index(0)
		row1 = self.convert_value(worksheet.row_values(0))
		row2 = self.convert_value(worksheet.row_values(1))
		row3 = self.convert_value(worksheet.row_values(2))
		row4 = self.convert_value(worksheet.row_values(3))
		row5 = self.convert_value(worksheet.row_values(4))
		
		self.exclude_repeated_case(row5)
		
		staitc_file_name = row1[0]
		if staitc_file_name == '':
			err_str = '!!!!!!!! ', 'File name is nill!', ' !!!!!!!!!!'
			print err_str
			time.sleep(1000)
			raise Exception(err_str)

		lst_type = []
		lst_name = []
		# lstDesc = []
		file_name = DAT_DIR + staitc_file_name + ".dat"
		fp = file(file_name, "wb")

		write_value = auxiliary_classes.WriteValueToFile()
		write_value.write_string(fp, staitc_file_name)
		# write_string(data_fp, staitc_file_name)
		for i in range(len(row2)):
			if row2[i] == "1":
			
				self.exclude_blank_data(row4[i], 4)
				self.exclude_blank_data(row5[i], 5)
			
				type_string = row4[i].lower()
				if type_string == "intarray" or type_string == "intarray2":
					type_string = "string"

				lst_type.append(type_string)
				lst_name.append(row5[i])
				# lstDesc.append(row3[i])

		file_offset_before_write_col_size = fp.tell()
		col_size = len(lst_name)
		write_value.write_byte(fp, col_size)
		row_size = worksheet.nrows - 5
		# write_short(data_fp, row_size)
		write_value.write_short(fp, row_size)
		
		addition_columns_size = 0
		type_list = []
		variables_list = []
		for i in range(0, col_size):
			if self.is_split_case(lst_name[i].lower()):
				type_list = self.extract_type(lst_type[i], 2)
				variables_list = self.extract_variables_name(lst_name[i].lower(), 1)
				if len(type_list) != len(variables_list):
					err_str = '!!!!!!!! ', 'encounter some error here. mark 4.', ' !!!!!!!!!!'
					print err_str
					time.sleep(1000)
					raise Exception(err_str)
				if len(type_list) > 0:
					addition_columns_size += len(variables_list) - 1
				type_list[:] = []
				variables_list[:] = []

		file_offset_after_write_meta = fp.tell()  # get the current offset in order to modify column nums as column may be changed
		new_columns_size = col_size + addition_columns_size
		if new_columns_size > col_size:
			fp.seek(file_offset_before_write_col_size, 0)
			write_value.write_byte(fp, new_columns_size)
			fp.seek(file_offset_after_write_meta, 0)
		
		for k in range(5, worksheet.nrows):
			row_data = worksheet.row_values(k)
			for j in range(len(row2)):
				if row2[j] != "1": # split case is tackled below, so do not worry here.
					continue
				type_string = row4[j].lower()
				self.exclude_blank_data(row_data[j], k)
				cell_value = self.conver_cell(type_string, row_data[j])
				if type_string == "int" :
					#print("int", row_data[j])
					write_value.write_int(fp, cell_value)
				elif type_string == "byte":
					#print("byte", row_data[j])
					write_value.write_byte(fp, int(cell_value))
				elif type_string == "short":
					write_value.write_short(fp, int(cell_value))
				elif type_string == "float":
					write_value.write_float(fp, cell_value)
				elif type_string == "byte":
					write_value.write_byte(fp, cell_value)
				elif type_string == "string" or type_string == "intarray" or type_string == "intarray2" or type_string == "bytearray":
					#print("string", row_data[j])
					write_value.write_unicode(fp, cell_value)
					
				# this is the case where type_string is like 'array~channel_type$short~map_id;int~x;int~y'
				# presume all the type in the special case are int, byte  and short.
				elif (type_string.find('array~') == 0) and (type_string.find('$')+1 != len(type_string)):
					if type(cell_value).__name__ == 'list':
						type_list = self.extract_type(type_string, 1)
						# print "type_list = ",type_list
						# print "values = ", cell_value
						if len(cell_value) % len(type_list) != 0:
							err_str = '!!!!!!!! ', 'encounter some error here. mark 1.', ' !!!!!!!!!!'
							print err_str
							time.sleep(1000)
							raise Exception(err_str)
						tuple_num = len(cell_value) / len(type_list)
						write_value.write_byte(fp, tuple_num) # write the length of array~, otherwise it will encounter error when resolve.
						for n in range(len(cell_value)):
							type_name = type_list[n % len(type_list)]
							# print type_name
							if type_name.lower() == "int":
								write_value.write_int(fp, int(cell_value[n]))
							elif type_name.lower() == "byte":
								write_value.write_byte(fp, int(cell_value[n]))  # original type is char, this should not be right.
							elif type_name.lower() == "short":
								write_value.write_short(fp, int(cell_value[n]))   # original type is short, this should not be right.
							elif type_name.lower() == "float":
								write_value.write_float(fp, float(cell_value[n]))
							elif type_name.lower() == "string":
								write_value.write_string(fp, str(cell_value[n]))
				elif self.whether_is_shortcut(type_string):
					type_string = self.get_valid_string_name(row4, j)  # use the type info of previous column which is not shortcut.
					if type_string == '':
						print "encounter some error here, mark 2."
						return
					type_list = self.extract_type(type_string, 1)
					if len(cell_value) % len(type_list) != 0:
							print "encounter some error here. mark 1."
							return
					tuple_num = len(cell_value) / len(type_list)
					write_value.write_byte(fp, tuple_num)   # write the length of array~, otherwise it will encounter error when resolve.
					for n in range(len(cell_value)):
						type_name = type_list[n % len(type_list)]
						#print type_name
						if type_name.lower() == "int":
							write_value.write_int(fp, int(cell_value[n]))
						elif type_name.lower() == "byte":
							write_value.write_byte(fp, int(cell_value[n]))  # original type is char, this should not be right.
						elif type_name.lower() == "short":
							write_value.write_short(fp, int(cell_value[n]))   # original type is short, this should not be right.
						elif type_name.lower() == "float":
							write_value.write_float(fp, float(cell_value[n]))
						elif type_name.lower() == "string":
							write_value.write_string(fp, str(cell_value[n]))
				elif self.is_split_case(type_string):     # this case need split type_string to several types.
					type_list = self.extract_type(type_string, 2)
					#print "type_list = ", type_list
					#print 'cell_value = ', cell_value
					if len(type_list) != len(cell_value):
						print 'encounter some error here. mark 5'
					for i in range(len(type_list)):
						if type_list[i] == "int":
							write_value.write_int(fp, int(cell_value[i]))
						elif type_list[i] == "byte":
							value = 0
							if cell_value[i] == '0.0':
								value = 0
							else:
								value = cell_value[i]
							write_value.write_byte(fp, int(value))    # original type is char, this should not be right.
						elif type_list[i] == "short":
							write_value.write_short(fp, int(cell_value[i]))	 # original type is short, this should not be right.
						elif type_string[i] == "float":
							write_value.write_float(fp, float(cell_value[i]))
		fp.close()
						
	def correct_literal_type(self, raw_type):
		if raw_type == 'int':
			return 'int'
		elif raw_type == 'short':
			return 'int'
		elif raw_type == 'string' or raw_type == "intarray" or raw_type == "intarray2" or raw_type == "bytearray":
			return 'String'
		elif raw_type == 'byte':
			return 'int'
		elif raw_type == 'float':
			return 'Number'
		return raw_type

	def is_split_case(self, raw_string):
		return (raw_string.find(';') > 0) and (raw_string.find('$') < 0) and (raw_string.find('_') < 0)
						
	def get_valid_string_name(self, row_string, current_column_index):
		for i in range(current_column_index)[::-1]:
			if not self.whether_is_shortcut(row_string[i].lower()):
				return row_string[i].lower()

	def whether_is_shortcut(self, string_name):
		# print string_name
		return (string_name.find('$') + 1 == len(string_name)) and (string_name.find('array~') >= 0)
		
	# Extract all types from string name.
	def extract_type(self, string_name, string_type):
		type_ist = []
		if string_type == 1: # array~channel_type$short~map_id;int~x;int~y
			# it seems that the first type name always appears after '$' symble.
			dollor_positon = string_name.find('$')
			type_name = []
			for i in range(dollor_positon + 1, len(string_name)):
				if ((ord(string_name[i]) >= 48) and (ord(string_name[i]) <=57)) or ((ord(string_name[i]) >= 65) and (ord(string_name[i]) <=90))  or ((ord(string_name[i]) >= 97) and (ord(string_name[i]) <=122)):
					type_name.append(string_name[i])
				else:
					type_ist.append(''.join(type_name))
					break
			#from the second type name, it seems that the type name always appears after ';' symble.
			#find all the position of semicolon in string name.
			semicolonPositinList = [m.start() for m in re.finditer(';', string_name)]
			#print "semicolonPositinList = ",semicolonPositinList
			for semicolonPositin in semicolonPositinList:
				type_name[:] = [] #clear content of type_name
				for j in range(semicolonPositin + 1, len(string_name)):
					if ((ord(string_name[j]) >= 48) and (ord(string_name[j]) <=57)) or ((ord(string_name[j]) >= 65) and (ord(string_name[j]) <=90)) or ((ord(string_name[j]) >= 97) and (ord(string_name[j]) <=122)):
						type_name.append(string_name[j])
					else:
						type_ist.append(''.join(type_name))
						break
		elif string_type == 2: #byte;int;int
			type_name = []
			for i in range(len(string_name)):
				if ((ord(string_name[i]) >= 48) and (ord(string_name[i]) <=57)) or ((ord(string_name[i]) >= 65) and (ord(string_name[i]) <=90))  or ((ord(string_name[i]) >= 97) and (ord(string_name[i]) <=122)):
					type_name.append(string_name[i])
					if i+1 == len(string_name):
						#print ''.join(type_name)
						type_ist.append(''.join(type_name))
				elif string_name[i] == ';':
					#print ''.join(type_name)
					type_ist.append(''.join(type_name))
					type_name[:] = [] #clear content of type_name
		else:
			print 'encounter some error here. mark 3'
			return 
		return type_ist
		
	def extract_variables_name(self, raw_string, extract_type):
		variables_list = []
		variable_name = []
		if extract_type == 1: #the separator symble which indicate the variable name is ';'
			for i in range(len(raw_string)):
				if ((ord(raw_string[i]) >= 48) and (ord(raw_string[i]) <= 57)) or ((ord(raw_string[i]) >= 65) and (ord(raw_string[i]) <=90))  or ((ord(raw_string[i]) >= 97) and (ord(raw_string[i]) <=122)):
					variable_name.append(raw_string[i])
					if i+1 == len(raw_string):
						#print ''.join(variable_name)
						variables_list.append(''.join(variable_name))
				elif raw_string[i] == ';':
					#print ''.join(variable_name)
					variables_list.append(''.join(variable_name))
					variable_name[:] = [] #clear content of typeName
		return variables_list
			
	def conver_cell(self, typename, data):
		if typename == "int" or typename == "byte" or typename == "short":
			try:
				return int(data)
			except:
				err_str = '!!!!!!!! ', 'data type error!', ' !!!!!!!!!!'
				print err_str
				time.sleep(1000)
				raise Exception(err_str)
		elif typename == "string" or typename == "intarray" or typename == "intarray2" or typename == "bytearray":
			if isinstance(data, unicode):
				return data
			if isinstance(data, float):
				if data == int(data):
					return "%d" % data
				else:
					return "%f" % data
		elif typename == "float":
			return float(data)
		elif typename.find('array~') == 0:
			content_list = re.split(r'[_;]', data)
			return content_list
		elif self.is_split_case(typename):
			type_list = re.split(r'[;]', typename)
			#print "type_list = ", type_list
			content_list = re.split(r'[_]', str(data))
			#print "content_list = ", content_list
			originalContentLength = len(content_list)
			shortNum = len(type_list) - len(content_list)
			#print "shortNum = ", shortNum
			if shortNum > 0:
				for i in range(shortNum):
					index = originalContentLength + i
					if type_list[index].lower() == "string":
						content_list.append('')
					else:
						content_list.append(0)
			return content_list
			
	def exclude_repeated_case(self, raw_row):  # if the excel file has repeated variable name which reside in the fifth row, then raise exception.
		d = dict()
		for i in range(len(raw_row)):
			if raw_row[i] in d:
				err_str = '!!!!!!!! ', 'repeated variable: ', raw_row[i], ' !!!!!!!!!!'
				print err_str
				time.sleep(1000)
				raise Exception(err_str)
			else:
				d[raw_row[i]] = 0

	def exclude_blank_data(self, raw_data, row):
		if raw_data == '':
			errStr = '!!!!!!!! ', 'There is blank data in row ' + str(row), ' !!!!!!!!!!'
			print errStr
			time.sleep(1000)
			raise Exception(errStr)
		return

	def convert_value(self, lst):
		ret = []
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
			data = str(data)
			ret.append(data)
		return ret


def main():
	generator = Generator()
	for filename in os.listdir(XLS_DIR):
		if ((filename[-3:] != 'xls') and (filename[-4:] != 'xlsx')) or (filename[0] == '~'):
			continue
		generator.gen_dat_file(filename)

if __name__ == "__main__":
	print '--------------Convert excel to dat---------------'
	init_path()
	refresh_folder(DAT_DIR)
	main()
