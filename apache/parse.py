"""Analysis tools for the Apache logs to determine if stuff from apache logs"""

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

def _mobile( line, url ):
	"""Determine if the request made to path (url) was done using a mobile device"""

	parts = re.match( _regex , line)

	if not parts:
		return

	parts = parts.groups()

	if url in parts[2]:
			print parts[1] + ',' + parts[6]
        	# print line

## https://github.com/selwin/python-user-agents

def parse( parser, scope, path = '../../apache-data/'):
	"""Generic parser module, takes parser function, possible scope/limits for parsin and path as parameters"""
	for f in os.listdir( path ):
		map( lambda line : parser( line, scope) , open( path + f, 'r') )

if __name__ == '__main__':
	parse( _mobile, 'savecomment' )




