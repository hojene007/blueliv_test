
# -*- coding: utf-8 -*-
"""
@autor: Yev
"""

from socket import *
import os
import datetime
import logging
import sys, time

class SocketClient() :

	"""
	Class outlines the client where the file is stored and relevant procedures for 
	calculating the operations in operations.txt
	"""
	__gateway = socket(AF_INET, SOCK_STREAM)

	def __init__ (self,  file, host='', port=8888) :
		#Here we initialize the client
		with open(file, 'r') as myfile:
			temp_file=myfile.read()

		self.port = port
		self.host = host

		#Private variables
		self.__my_file = temp_file.encode()
		self.__file_size = sys.getsizeof(self.__my_file)
		self.__msg_recvd = ''
		self.__msg_recvd_size = 0
		
		# Some crucial variables
		self.client_log = ''
		self.output_file = ''
		self.ops_list = [] #not sure if this is needed

		self.connect()
		#logging.info("Connected to server... %s" % datetime.datetime.now())
		self.sender()




	def connect(self) :
		# connect to a service and make sure it works
		try :
			print("Attempting to connect...")
			self.__gateway.connect((self.host, self.port))
			print("Connected to sockets on host %s and port %s." % (self.host, self.port))
			logging.info("Connected to sockets on host %s and port %s...%s" % (self.host, self.port, datetime.datetime.now()))
		except Exception as e :
			print("Connection failed... %s" % e)
			logging.info("Connection failed... %s ... %s" % (e, datetime.datetime.now()))




	def sender(self) :
		# sender sends the entire list of operations to the service 
		chunks = []
		bytes_sent = 0
		print(self.__my_file[0:5])
		while bytes_sent < self.__file_size :
			#make sure we get the entire message
			sent = self.__gateway.send(self.__my_file[bytes_sent:])
			if sent == 0 :
				raise RuntimeError("socket connection broken... cannot send")
				logging.info("socket connection broken... cannot send...%s" % datetime.datetime.now())

			bytes_sent += sent

			logging.info("Total bytes sent... %s out of %s...%s" % (bytes_sent, self.__file_size, datetime.datetime.now()))
			
		print("Message sent.")
		logging.info("Total bytes sent... %s. out of %s. Message delivered...." % (bytes_sent, self.__file_size, datetime.datetime.now()))


	def timed_receiver(self, timeout = 10) :
		#Method waits a specific amount of time for receiving the file
		msg_list = []
		msg = ''
		begin = time.time()
		while True :
			# lets see if we got at least some of the msg
			if msg_list and time.time() - begin > timeout :
				break
			elif time.time() - begin >timeout*2:
				#if no data at all wait longer
				break

			try :
				msg = self.__gateway.recv(4096)
				if msg :
					msg_list.append(msg)
					begin = time.time()
				else :
					time.sleep(0.1) #throttle
			except Exception as e:
				logging.info("Exception while receiving... %s ...%s" % (e, datetime.datetime.now()))
				pass

		self.__msg_recvd = ''.join(msg_list)

		self.output_file = open("op_solutions.txt", "w")
		self.output_file.write(self.__msg_recvd)
		self.output_file.close()
		logging.info("Text file 'op_solutions.txt' containing response is created...%s" % datetime.datetime.now())

	    # And finally close connection
		self.__gateway.close()
		logging.info("Gateway closed... %s" % datetime.datetime.now())

	    #Store log file in a text file
		logging.basicConfig(filename='client_log.txt', level=logging.INFO)
		print("Response received, connection closed...happy days")






