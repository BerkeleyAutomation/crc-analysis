import os
import re

_regex = '([(\d\.)]+) - - \[(.*?)\] "(.*?)" (\d+) (\d+) "(.*?)" "(.*?)"'
## 0 => IP
## 1 => date
## 2 => URL
## 3 =>
## 4 =>
## 5 => referer
## 6 => type

def _line( line ):

	parts = re.match( _regex , line)

	if not parts:
		return

	parts = parts.groups()

	if 'savecomment' in parts[2]:
			print parts[1] + ',' + parts[6]
        	# print line

## https://github.com/selwin/python-user-agents

def parse( path = '../../apache-data/'):
	for f in os.listdir( path ):
		map( _line , open( path + f, 'r') )

if __name__ == '__main__':
	parse()




