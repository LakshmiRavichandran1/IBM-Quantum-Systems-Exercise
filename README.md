# IBM Quantum Systems software exercise -  submission 

Exercise : https://github.com/atilag/IBM-Quantum-Systems-Exercise

First of all, thank you for reviewing my submission.

In my solution, I do the below:
1. read the input for small or large quatum programs provided in the input.json
2. generate pulse operations for the arithmetic operations in the quantum program 
3. call the control_instrument API based on the type and obtin results. currently it is Acme or Madrid conrol instruments
4. display the results

In the solution, I used python programming language.
I implemented a logic to convert the arithmentic to pulse operations by recusively parsing them.

For improving the performance on processing large quantum programs, I implemented a solution using multi-processing to process the Pulse sequence submitted to each control instrument service paralllely which improves the processing time.

To run the solution, please use generate_pulse_sequence_and_process.py
1. Please ensure the control instruments API services are active
2. Configure the input json in the respectve files
3. Enter the choice of input to be processed - small or large
4. The results are displayed in the terminal

Exception Handling:
------------------
The solution implements exception handling to encounter any problems faced during service calls.
In that case the result of None is considered.


Sample Output:
--------------
User Choice to process 'small' Quantum Programs:

'
Welcome to the exercise ! 
please ensure the control instrument is started and the access urls are properly defined
____________________________________________________________________________________________________________   
As sample, they can be started with commands 
 1. uvicorn acme_instruments_service.main:app --host 127.0.0.1 --port 8000 
 2. uvicorn madrid_instruments_service.main:app --host 127.0.0.1 --port 8080 
____________________________________________________________________________________________________________   
Please enter the choise of processing for generating pulse program for (small or large input) : small
 ______________________________________________________  
********---Program Load --********
{'program_id': 'AcmeProgramId986'}
AcmeProgramId986
********---Run Program --********
195
 ______________________________________________________  
Printing the results of calculation from the Pulse Programs submitted:
____________________________________________________________________________________________________________   
[195]

'


User Choice to process 'large' Quantum Programs:
as the output has more lines to be displayed, I have attached them in sample_output_large.txt
