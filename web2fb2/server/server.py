#!/usr/bin/env python
import SimpleXMLRPCServer
import SocketServer
import base64

import tidy

def do_tidy(data):
	options = dict(tidy_mark=0,  force_output=1, input_encoding = 'utf8', char_encoding = 'utf8')
	out_data =  str(tidy.parseString(data.encode('utf8'), **options))
	print len(out_data)
	return out_data


class AsyncXMLRPCServer(SocketServer.ThreadingMixIn, SimpleXMLRPCServer.SimpleXMLRPCServer): pass

class BasicAuthXMLRPCRequestHandler(SimpleXMLRPCServer.SimpleXMLRPCRequestHandler):
	def do_POST(self):
		real_auth = 'admin:password'
		auth = self.headers.get('authorization', None)
		if not auth:
			self.send_response(401)
			self.end_headers()
			return
			
		auth = auth.replace("Basic ","")
		decoded_auth = base64.decodestring(auth)
		if not decoded_auth == real_auth:
			self.send_response(401)
			self.end_headers()
			return

		return SimpleXMLRPCServer.SimpleXMLRPCRequestHandler.do_POST(self)

server = AsyncXMLRPCServer(('62.205.172.4', 8000), BasicAuthXMLRPCRequestHandler)

server.register_function(do_tidy)
 
# run!
server.serve_forever()