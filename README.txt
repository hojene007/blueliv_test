
******************


README


******************





There are two main modules included - the server.py and the client.py. Two scripts are also included. 





******************

Client module

******************

- Initialized with the file, host adress, port
- connect() method is responsible for connecting to the socket
- sender() method is responsible for sending the file throught the socket
- timed_receiver() method takes the arguement of how many second we wait until we stop waiting for bytes to come in
	this is implemented because we don't know the size of the incoming file (in general)

******************

Server module

******************

The server module contains 3 classes: SocketServer, Distributer, OperationsCalculator. 

SocketServer

	- the socket server class is responsible for receiving the file and serving it up for calculations
	- initialized with host adress and port
	- listener() method is responsible for listening out for new connections (up to 5 possible)
	- timed_receiver() - similar to that of the client but instead of saving the file turns the operations
		into a (list) class variable to be used by the distributer

Distributer
	- class responsible to dividing up the list of operations from the SocketServer object for the children
		to later work on. This is needed for when we want more than 1 child processes to actively solve
		the arithmetic operations
	- initialized with the list of operations and number of children variables

	- currently employs equal spread of operations amongst children

OperationsCalculator

	- class responsible for converting from string to arithmetic operations the given to it list of operations
		this is used insead of the eval() function
	- initialized with a vector of calculations in string format as given in the operations.txt file (but after they've
		been converted to string)
	- the methods in these class are sub-functions necesary to get the string in the right format and 
		perform the calculations with regard for arithmetic rules. EVAL() IS NOT USED!

******************

Scripts

******************

parent_child_server.py script refers to the launching of the server and the definition of parent /child methods. 
In the parent method we distribute the work amongst the children. In the child method we perform the calculations 
on the server. Parent process uses the Distributer object. The SocketServer object is initialized in the '__main__' method
to receive the operations. There is also a commented block which allows for testing of the pipes functionality separately.
The child method uses the OperationsCalculator object. There is also a helper function here to put the results given by
the calculations in a readable format, which is saved as a text file. 

client_script.py script refers to using the ClientSocket object to be initialized, connect to the server and send information.

Logging is used throughout the application. 
 