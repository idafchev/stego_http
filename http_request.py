#!/usr/bin/env python3
import urllib.parse

class http_request:
	def __init__(self, uri, method, body='', headers={}):
		parsed_uri = urllib.parse.urlparse(uri)
		self.protocol = parsed_uri[0]
		self.host = parsed_uri[1]
		self.path = parsed_uri[2]
		self.query = parsed_uri[4]
		self.method = method
		self.body = body
		
		# default values for headers:
		self.headers = {
		'host': self.host,
		'user-agent':'http_exfil',
		'accept-encoding':'gzip,deflate',
		'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		'accept-language': 'bg,en-US;q=0.7,en;q=0.3',
		'connection': 'keep-alive'
		}
		self.set_headers(headers)
		
		# Construct the request as ascii text
		self.generate()
		
	def set_headers(self, headers):
		if len(self.body) > 0:
			# If there is a body, add these headers with their default values
			self.headers['content-length'] = str( len(self.body) )
			self.headers['content-type'] = 'text/html'
		if headers:
			# Add the passed headers and overwrite the existing ones
			for h in headers.keys():
				self.headers[h.lower()] = headers[h.lower()]
				
	def generate(self):
		# Construct the request as ascii text
		if self.query: self.query = '?' + self.query
		request = self.method + ' ' + self.path + self.query + ' HTTP/1.1\r\n'
		for h in self.headers.keys():
			request += h + ': ' + self.headers[h] + '\r\n'
		request += '\r\n'
		if self.body:
			request += self.body
		self.request = request

