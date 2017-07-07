#!/usr/bin/env python3
import binascii, socket
from http_request import http_request

def ascii2bin( message ):
	num_bits = len(message) * 8
	format_string = '{0:0' + str(num_bits) + 'b}'
	binary_message = format_string.format(int(binascii.hexlify(bytes(message.encode('ascii'))),16))
	return binary_message

# The number of bits that can be hidden in the request
# The method line cannot be used (-2 spaces)
def capacity(request):
	cnt = request.count(' ') - 2
	return cnt

# Generate GET request with fixed Headers:Values
# only for testing
# n=0 or 1 -> 0 marks the last request
def generate_http_request(n):
	get_headers = {
	'host': '127.0.0.1',
	'connection': 'keep-alive',
	'x-requested-with': 'XMLHttpRequest',
	'upgrade-insecure-requests': '1',
	'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
	'referer': 'http://www.mysite.com/',
	'accept': 'text/html, application/xhtml+xml, application/xml;q=0.9, image/webp, */*;q=0.8',
	'accept-encoding': 'gzip, deflate, sdch',
	'accept-language': 'bg-BG, bg;q=0.8, en;q=0.6, de;q=0.7',
	'accept-charset': 'utf-8, iso-8859-1;q=0.5, *;q=0.1',
	'dnt': '1',
	'cache-control': 'must-revalidate, public, max-age=0'
	}
	request = http_request('http://google.com/test/test.php?id='+str(n),'GET', headers=get_headers).request
	return request

# Hide binary data in a single line(http header)
def hide_in_line( line, binary ):
	if line.count(' ') != len(binary):
		raise "Length Exception"
	try:
		int(binary,2)
	except:
		raise "NonBinary input Exception"

	new_line = list(line)
	space_index = line.find(' ')
	binary_index = 0
	while(True):
		# The first space (the one after ':') is not used to encode data
		# Start from the second space in the header
		space_index = line.find(' ',space_index+1)
		if space_index < 0: break
		if binary[binary_index] == '1':
			# Encode 1s with two spaces
			new_line[space_index] = ' '*2
		binary_index += 1

	# Insert spaces right before \r\n to increase capacity
	cr_index = line.find('\r')
	if binary[binary_index] == '1':
		new_line[cr_index] = ' '*2 + '\r'
	else:
		new_line[cr_index] = ' ' + '\r'

	return ''.join(new_line)

# Hide binary data in http request
def hide_in_request(request, bin_msg):
	r = request.split('\n')[:-1]
	bin_index = 0
	new_request = []

	for i,line in enumerate(r):
		if i == 0: # The first line (method line) is not used to hide data
			new_request.append(line+'\n')
			continue
		if line == '\r': # The end of http headers
			new_request.append('\r\n')
			continue

		new_line = []
		# How many bits can be hidden in the current line(header)
		# Although the first space is not used, to encode data
		# we insert space right before \r\n to make up for this
		# That way it's harder to notice visually
		line_capacity = line.count(' ')

		# Take as many bits as could be hidden in the line
		binary_part = bin_msg[bin_index : bin_index + line_capacity]
		# If the bits left are less than the capacity of the line
		# pad with zeroes until the capacity is reached
		if len(binary_part) != line_capacity:
			delta = line_capacity - len(binary_part)
			binary_part = binary_part + '0'*delta

		new_request.append( hide_in_line(line+'\n', binary_part) )
		
		bin_index = bin_index + line_capacity

	return ''.join(new_request)

# Hide the message in as many http requests as needed
def stego_requests( message ):
	binary_msg = ascii2bin( message )
	bin_index = 0
	stego_req = []
	request = generate_http_request(1)
	
	while(True):
		cap = capacity( request )
		# Take as many bits from the message as could be hidden
		# in the current request
		binary_block = binary_msg[bin_index : bin_index + cap]
		req = hide_in_request(request, binary_block)
		stego_req.append( req )
		bin_index += cap
		if bin_index > len(binary_msg): break

	# Mark the last request with 0
	index = stego_req[-1].find('=') + 1
	s = list(stego_req[-1])
	s[index] = '0'
	stego_req[-1] = ''.join(s)
	
	return stego_req
	
def send( message, ip, port ):
	requests = stego_requests( message )
	
	for r in requests:
		s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		s.connect((ip, port))
		msg = r
		s.send(msg.encode('utf-8'))
		s.recv(8192)
		s.close()
	
def main():
	ip = input('IP address: ')
	port = int(input('Port: '))
	print("Press Ctr+C to exit!")
	while(True):
		msg = input("Message: ")
		send(msg, ip, port)
	
if __name__ == '__main__':
	main()
