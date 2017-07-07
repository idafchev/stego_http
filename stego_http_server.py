#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
	
def bin2chr( byte ):
	c = chr(int( byte, 2 ))
	return c

# Read the hidden bits from a single line/header
def read_from_line( line ):
	binary = []
	index = line.find(' ')

	while(True):
		# Hidden data starts from the second space
		index = line.find(' ',index+1)
		if index < 0: break

		# If the next element is also a space => 
		# it's a double space => decode to 1
		if line[index+1] == ' ':
			binary.append('1')
			index += 1
		else:
			binary.append('0')

	return ''.join(binary)

# Read the hidden bits from http request
def read_from_request( request ):
	lines = request.split('\n')
	binary = []

	for i,line in enumerate(lines):
		#if i == 0: continue
		# The server parses the request with \n\n instead of \r\n
		# This is a quick fix that adds \r so the rest of the code works
		if line.find('\r') < 0:
			line = line + '\r'
		bits = read_from_line(line)
		binary.append(bits)

	binary_block = ''.join(binary)
	return binary_block

# Decode the whole hidden message from all requests
def decode_message(stego_requests):
	binary = []
	message = []

	for req in stego_requests:
		binary.append( read_from_request(req) )
	bin_msg = ''.join(binary)

	# Split bin_msg in groups of 8bits and
	# decode them as individual ascii characters
	for i in range(8,len(bin_msg),8):
		message.append( bin2chr(bin_msg[i-8 : i]) )

	print(''.join(message))

hdrs = [] 
class testHTTPServer_RequestHandler(BaseHTTPRequestHandler):

	def do_GET(self):
		# Response 200 OK status code
		self.send_response(200)
 		
		# Headers of the response
		self.send_header('Content-type','text/html')
		self.end_headers()
	 	
		# Response body
		message = "Success!"
		
		# Send response
		self.wfile.write(bytes(message, "utf8"))
		
		headers = self.headers

		if self.path.endswith('1'):
			hdrs.append(str(headers))
			
		elif self.path.endswith('0'):
			hdrs.append(str(headers))
			decode_message(hdrs)
			
			# Empty the list. Assignment to [] didn't work...
			del hdrs[:]
		return
 	
def main():
	print('Starting...')
	server_address = ('0.0.0.0', 80)
	httpd = HTTPServer(server_address, testHTTPServer_RequestHandler)
	print('Server is running...')
	httpd.serve_forever()
	
if __name__ == '__main__':
	main()
