# -*- coding: utf-8 -*-
"""
@autor: Yev
"""

from socket import *
import logging, array, operator, datetime
import pandas as pd
import array

class OperationsCalculator() :

	"""
	Class reponsible for handling calculations of operations

	"""
	def __init__(self, calc_vec) : 
		#calc_vec is a list of 
		# Initialization of object calculates the vector of answers related ot the input list of calculations
		self.calc_vec = calc_vec
		self.ans_list = []
		self.ordered_df = pd.DataFrame(index = range(0, len(self.calc_vec)), columns = ["operation", "answer"])

		self.eval_vec()


	def get_compound_expr(self, expr) :
		# function gets the expressions from the overall arithmetic expression that involve multiplication and division
	    expr1 = [a for a in expr if a is not " "] # get rid of spaces
	    compr_exprs = []
	    for i, a in enumerate(expr1) :
	        if a in ["/", "*"] :
	            expr_comp_end = '' #everything after the div/mul sign
	            for j in expr1[i:] :
	                if j not in ["+", "-"] :
	                    expr_comp_end += j
	                else :
	                    break
	                    
	            expr_comp_start = ''  # everything before the div/mul sign
	            for j in reversed(list(range(0, i))) :
	                    if expr1[j] not in ["+", "-"] :
	                        expr_comp_start += expr1[j]
	                    else :
	                        break
	            compr_expr = expr_comp_start[::-1] + expr_comp_end
	            if compr_expr not in compr_exprs or expr1.count(compr_expr)>1:
	                compr_exprs.append(compr_expr)
	        
	    return(compr_exprs)
        

	def eval_div_mul(self, expr) :
		# function evaluates expressions involving multiplication and division
	    # used in conjunction with get_compund_expr()
	    ans_t = 0
	    curr_dig = ''
	    for i, a in enumerate(expr) :
	        if ans_t == 0 :
	            if a.isdigit() :
	                curr_dig += a
	            elif a == "*":
	                ans_t = int(curr_dig)
	                curr_dig= ''
	                curr_sign = "*"
	            else: 
	                ans_t = int(curr_dig)
	                curr_dig= ''
	                curr_sign = "/"
	            
	        else :

	            if a.isdigit():
	                curr_dig += a
	                det_sign = 0
	            elif a.isdigit()== False and curr_sign == "*":
	                ans_t = ans_t*int(curr_dig)
	                curr_dig = ''
	                det_sign = 1
	            elif a.isdigit()== False and curr_sign == "/":
	                ans_t = ans_t/int(curr_dig)
	                curr_dig = ''
	                det_sign = 1
	            else :
	                print("error")
	                break
	                 
	            if det_sign == 1:
	                if a == "*":
	                    curr_sign = "*"
	                else: 
	                    curr_sign = "/" 
	            
	            
	            if i+1 == len(expr) and curr_sign == "*":
	                ans_t = ans_t*int(curr_dig)
	                
	            elif i+1 == len(expr) and curr_sign == "/":
	                ans_t = ans_t/int(curr_dig)
	                
	            else :
	                pass

	    return(ans_t)

	def simplify_expr(self, expr) :
		# converts any expression into a sequence of sums and minuses
	    expr1 = ''.join([a for a in expr if a is not " "])
	    compound_expr = self.get_compound_expr(expr1)
	    new_expr = ''
	    #print(compound_expr)
	    if len(compound_expr) > 0 :
		    for i, c_expr in enumerate(compound_expr) :
		        ans = self.eval_div_mul(c_expr)
		        if i== 0 :
		            new_expr = expr1.replace(c_expr, str(ans))
		        else :
		            new_expr = new_expr.replace(c_expr, str(ans))
	    else :
		    new_expr = expr1
	    
	    return(new_expr)

	def string_2_expr(self, expr) :
		#method separates expressions into numbers and operations
	    op_list = []
	    num_list = []
	    curr_dig = ''
	    exp_no_space = [a for a in expr if a is not " "]
	    for jj, i in enumerate(exp_no_space) :
	        if i.isdigit() == True or i == ".":
	            curr_dig += i 
	        
	        else :
	            if curr_dig != '' :
	                num_list.append(curr_dig)
	                
	            op_list.append(i)
	            curr_dig = ''
	            
	        if jj+1 == len(exp_no_space) :
	            num_list.append(curr_dig)
	            
	    return([num_list, op_list])

	def my_eval_expr(self, expr) : 
		# function evaluates arithmetic string expression passed to it
	    via_lists = self.string_2_expr(self.simplify_expr(expr)) 
	    num_list = via_lists[0]
	    ops_list = via_lists[1]
	    k = 0
	    ans_t = 0
	    for i, num in enumerate(num_list) :
	        if i == 0 :
	            if ops_list[k] == "-" :
	                ans_t = float(num) - float(num_list[i+1])
	            else :
	                ans_t = float(num) + float(num_list[i+1])
	            k+=1
	        elif i==len(num_list)-1 :
	            if ops_list[-1] == "-" :
	                ans_t = ans_t - float(num)
	            else :
	                ans_t = ans_t + float(num)
	        elif i>1 :
	            if ops_list[k] == "-" :
	                ans_t = ans_t - float(num)
	            else :
	                ans_t = ans_t + float(num)
	            k+=1
	    return(ans_t)

	def eval_vec(self) :
		
		for i, op in enumerate(self.calc_vec) :
			ans = self.my_eval_expr(op)
			self.ans_list.append(ans)

		#self.ordered_df = pd.DataFrame(index = range(0, len(self.calc_vec)), columns = ["operation", "answer"])
		self.ordered_df["operation"] = self.calc_vec
		self.ordered_df["answer"] = self.ans_list



class Distributer() :

	"""
	Class outlines the distribution scheme among children processes for speeded up calculations
	"""

	def __init__(self,  ops_list, n_child=2) :
		self.n = n_child # the number of children procsses 
		self.ops_list = ops_list
		self.child_dict = {}

		#initialize the information dictionary to be passed on to children
		# here each child takes care of a portion of the file 
		for i in list(range(0, self.n)) :
			self.child_dict[i] = []

		self.uniform_dist()

	def uniform_dist(self) :
		#method designates equal loading amongst children for calculations
		per_child = int(len(self.ops_list)/self.n)
		#logging.info("first_batch %s" % per_child)
		ops_recorded = 0 # checker for that we assign all the ops
		for i in range(1, self.n+1) :
			these_ops = self.ops_list[(i-1)*per_child:per_child*i]
			logging.info("batch length %s" % len(these_ops))

			self.child_dict[i] = these_ops
			ops_recorded += len(these_ops)
		logging.info("Total ops needed %s" % len(self.ops_list))
		if ops_recorded != self.ops_list :
			logging.info("Not all operations were assigned to a child...%s" % datetime.datetime.now())
		else :
			logging.info("All operations were assigned to a child...%s" % datetime.datetime.now())


	def all_in_1(self) :
		# all the load is handled by 1 child
		self.child_dict[1] = self.ops_list



class SocketServer() :

	"""
	Class outlines the server where the file is stored and relevant procedures for servering the
	operations.txt file for calculations
	"""
	__gate = socket(AF_INET, SOCK_STREAM)

	def __init__ (self, host,  port=80) :
		#Here we initialize the server
		logging.info("Initializing socket server")
		self.my_port = port
		self.my_host = host
		

		self.__gate.bind((self.my_host, self.my_port))

		self.__msg_recvd_size = 0


		self.live_conn = 0 # boolean for existing connection
		self.listener()

		if self.live_conn == 1 :
			self.timed_receiver(30)
		#	self.live_conn = 0

		#self.files_on_server = [] #variables grabs directory of file

	def listener(self) :
		# listens and accepts new connections
		print("Server listening for connections")
		logging.info("Server listening for connections...%s" % datetime.datetime.now())
		self.__gate.listen(5)
		while True :
			
			(self.__clientsocket, address) = self.__gate.accept()
			
		self.live_conn = 1


	def timed_receiver(self, timeout = 10) :
		#Method waits a specific amount of time for receiving the file
		msg_list = []
		msg = ''
		begin = time.time()
		msgs_recvd = 0
		while True :
			# lets see if we got at least some of the msg
			if msg_list and time.time() - begin > timeout :
				logging.info("No longer receiving stuff... %s " % datetime.datetime.now())
				print("stop receiving")
				break
			elif time.time() - begin >timeout*2:
				#if no data at all wait longer
				logging.info("Haven't received anything at all... %s " % datetime.datetime.now())
				break

			try :
				msg = self.__gateway.recv(4096)
				if msg :
					msg_list.append(msg)
					msgs_recvd += 1
					print("Received message # %s " % msgs_recvd)
					logging.info("Received message # %s " % msgs_recvd)
					begin = time.time()
				else :
					time.sleep(0.1) #throttle
			except Exception as e:
				logging.info("Exception while receiving... %s ...%s" % (e, datetime.datetime.now()))
				pass

		self.__msg_recvd = ''.join(msg_list)

		temp = self.__msg_recvd[1:] # clearing the size of the message from the operations list
		operations = temp
		ops_list = []
		for i, op in enumerate(operations) :
			ops_list.append(op[:-1])

		self.ops_list = ops_list
        # And finally close connection
		self.__clientsocket.close()

		logging.info("Client socket closed...", datetime.datetime.now())




   
