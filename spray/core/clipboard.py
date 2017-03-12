# -*- coding:utf-8 -*-
import time
import pyperclip
import pronunciation
import os
import utility
import multiprocessing

interval = 2.5    # interval seconds for scanning clipboard
times = 3   # the times of repeating word pronunciation
max_length = 600    # the maximum length of word usage.
timeout = 6     # wait no more than four seconds for show pronunciation.


def watcher():
	word = ''
	i = 0
	while True:
		result = pyperclip.paste().strip().lower()
		if len(result) >= max_length:
			continue
		if result.isalpha() and len(result) != 0 and word != result:
			word = result
			i = 0
		if word != '':
			if i >= times:
				if result == word:
					os.system("echo '' | pbcopy")
				i = 0
				word = ''
				continue
			i += 1

			p = multiprocessing.Process(target=pronunciation.show, args=(word,))
			p.start()
			# Wait timeout seconds or until process finishes
			p.join(timeout)
			# If thread is still active
			if p.is_alive():
				print "running... let's kill it..."
				# Terminate
				p.terminate()
				p.join()

		time.sleep(interval)
	utility.show_notification('Captain Info', 'Sorry, some error may happened! Please check the error message!')


# whether the src is valid string, the code or the Chinese should be exclusive.
def is_valid_string(src):
	invalid_characters = {'[': True, ']': True, '@': True, '#': True, '^': True, '&': True, '&&': True, '||': True, '*': True, "==": True, "===": True, '\\': True, '/': True, '`': True}
	for ch in src:
		if ch in invalid_characters:
			return False
	return True


if __name__ == "__main__":
	watcher()
