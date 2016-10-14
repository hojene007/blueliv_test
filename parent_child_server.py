# -*- coding: utf-8 -*-
"""
@autor: Yev
"""


from server import *
from client import *
import logging, os, datetime
from multiprocessing import Pipe, Process
import multiprocessing
import pandas as pd
import sys

def convert_to_readable(b_string) :
	# Method converts received from sockets output to readable format
	out_str	= b_string.replace('"', '')
	out_str1 = out_str.replace("[", "")
	out_str2 = out_str1.replace("]", "")
	out_str2_1 = out_str2.replace('n', "")
	out_str2_2 = out_str2_1.replace('\ ', " ")
	out_str2_3 = out_str2_2.replace(') ', ")\n")
	out_str3 = out_str2_3.replace("b", "\n") 
	out_str4 = out_str3.replace(") ", ")\n")

	return(out_str4)


def child_process(child_conn, calc_vec) : 
	
	# This is the child process structure 

	calc_obj = OperationsCalculator(calc_vec)
	results = calc_obj.ordered_df #turn this to bytes
	rec = results.to_records(index = False)
	rec2 = str(rec)
	df_in_bytes = str.encode(rec2)
	size_records = sys.getsizeof(df_in_bytes)

	#print(df_in_bytes)
	#temp = b"bla blah"
	child_conn.send(df_in_bytes)
	child_conn.close()



def parent_process(n_children, expr_list) :

	#This is the parent process that spawns and kills children
	# when necesary

	"""
	This can be used for testing the parent child stuff - only some of the operations 
	are taken and the socket functionality can be ignored

	tester = list(open('operations.txt'))
	expr_list = []
	for i, expr in enumerate(tester):
	    if i< 20 :
	        expr1 = expr[:-1]
	        expr_list.append(expr1)
	    else :
	        break
	"""
	result_string = ''

	calc_vec_on_server = expr_list
	distribution = Distributer(calc_vec_on_server, n_children)
	parent_receivers = [] # store the parent ends of the process to later collect results 
	child_senders = []
	children_list = []

	for i in range(1, n_children+1) :
		# the number of children can vary
		parent_conn, child_conn = Pipe() 
		parent_receivers.append(parent_conn)
		logging.info("Launching child #%s" % i)

		ops_list = distribution.child_dict[i]
		a_child = Process(target=child_process, args=(child_conn, ops_list))

		a_child.start()
		print("starting child #%s" % i)
		child_senders.append(child_conn)
		children_list.append(a_child)
		# let the children work at it and store the connecting pipes to later get info and close them

	print("There have been %s children processes" % len(child_senders))

	for i in range(1, n_children+1) :
		info_temp = parent_receivers[i-1]
		#print((info_temp.recv()))
		result_string = result_string+str(info_temp.recv())
		
		logging.info("Capturing data... %s" % (datetime.datetime.now()))
		children_list[i-1].join()
		logging.info("child #%s destroyed" % i)

		out_str = convert_to_readable(result_string)

	return(out_str)



if __name__ == '__main__':

	# Launch server
	mySocketServer = SocketServer(host ='localhost', port = 2323)
	#then from external we get the client to send information to the server
	# assuming the info is sent we will get the class variable ops_list which has
	# all the calculations to be carried out through the parent children relationship
	n_childs = 2

	calc_vec = mySocketServer.ops_list

	multiprocessing.set_start_method('spawn')       

	

	# Send to parent 
	eq_and_res = parent_process(n_childs, calc_vec) 

	# Record results in a file
	results_file = open("results.txt", "w")
	results_file.write(eq_and_res)
	results_file.close()
	
	
	logging.basicConfig(filename='test_app.txt', level=logging.INFO)

