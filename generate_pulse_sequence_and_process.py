import json
import multiprocessing as mp
from argparse import ArgumentParser
from ast import Constant
from asyncio import sleep
from base64 import encode
from dataclasses import dataclass
from enum import IntEnum
from json import JSONEncoder
from queue import Empty
from statistics import variance
from typing import List

import requests
from pconst import const

from generate_quantum_programs import (ArithmeticOperation,
                                       Operation, QuantumProgram)



# QuantumProgramInput builds the QuantumProgram class from the string input received from input json file
class QuantumProgramInput(QuantumProgram):
 
    @staticmethod
    def from_string(json_dct):
        id = json_dct['id']
        control_instrument = json_dct['control_instrument']
        initial_value = json_dct['initial_value']
        operations_json = json_dct['operations']
 
        operations = []
        for x in operations_json:
            operation_item = OperationInput.from_json(x)
            operations.append(operation_item)
 
        return QuantumProgram(id,control_instrument,initial_value,operations)

#OperationProgramInput builds the embedded Operation class from the string input
class OperationInput(Operation):
 
    @staticmethod
    def from_json(json_dct):
      return Operation(dict_ARITHMETIC_OPERATION[json_dct['type']],
                   json_dct['value']) 

# constant value declaration
const.VALUE = "VALUE"

#Service class for Acme Control Instrument
class AcmeService():
    PROGRAM_LOAD_URL = 'http://127.0.0.1:8000/load_program'
    HEADER = {"Content-Type": "application/json"}
    PROGRAM_RUN_URL = 'http://127.0.0.1:8000/run_program/'

    NAME = "acme"
 
    dict_ACME ={
    ArithmeticOperation.Sum : ["Acme_pulse_1", "Acme_pulse_2", const.VALUE],
    ArithmeticOperation.Mul : ["Acme_pulse_2", "Acme_pulse_1", "Acme_pulse_1", const.VALUE],
    ArithmeticOperation.Div : ["Acme_pulse_2", "Acme_pulse_2", const.VALUE],
    ArithmeticOperation.InitState : ["Acme_initial_state_pulse", const.VALUE]
    }
 
#Service class for Madrid Control Instrument
class MadridService():
    PROGRAM_LOAD_URL = 'http://127.0.0.1:8080/program/load'
    HEADER = {"Content-Type": "application/json"}
    PROGRAM_RUN_URL = 'http://127.0.0.1:8080/program/run/'
    
    NAME = "madrid"

    dict_MADRID ={
    ArithmeticOperation.Sum : [const.VALUE, "Madrid_pulse_1"],
    ArithmeticOperation.Mul : [const.VALUE, "Madrid_pulse_2", "Madrid_pulse_2"],
    ArithmeticOperation.Div : [const.VALUE, "Madrid_pulse_2", "Madrid_pulse_1"],
    ArithmeticOperation.InitState : [const.VALUE, "Madrid_initial_state_pulse"]
    }

#Service class for holding the details for service call to be made based on the control instrument to be invoked
class QService():
    program_load_url: str
    header: str
    program_run_url: str
    control_dict = {}
 
    def __init__(self, program_load_url, header, program_run_url, control_dict):
        self.program_load_url = program_load_url
        self.header = header
        self.program_run_url = program_run_url
        self.control_dict = control_dict

#class to contain the values of Pulse operations before invoking the control instrument
class PulseProgram():
 
    program_code: list
    result: str
 
    def __init__(self, program_code, result):
        self.program_code = program_code
        self.result = result
 
#dictionry of values for the types of Pulse operations
dict_ARITHMETIC_OPERATION = dict([('Sum', ArithmeticOperation.Sum),
                                  ('Mul', ArithmeticOperation.Mul),
                                  ('Div', ArithmeticOperation.Div),
                                  ('InitState', ArithmeticOperation.InitState)])


# function to expand Arithmetic Operation to Pulse sequence  
def expand_operation(operation, value, dict_operation):
    dict_array = dict_operation[operation]
    return replace_const_value(dict_array, value)
 
def replace_const_value(dict_array, value):
    l = list(map(lambda x : int(value) if(x == const.VALUE) else x, dict_array))
    return l
 
#function which receives input Quantum Program, converts it to Pulse sequence
def expand_as_pulse_program(lhs_array, operations_array, quantum_program, from_service):
    if(len(operations_array) == 0):
        return lhs_array
    else:
        if(len(lhs_array) == 0):
            lhs_array = []
            expanded_initial_state = expand_operation(ArithmeticOperation.InitState, quantum_program.initial_value,from_service.control_dict)
            lhs_array.extend(expanded_initial_state)
            return expand_as_pulse_program(lhs_array, operations_array, quantum_program, from_service)
        else:
            current_operation = operations_array[0]
            expanded_string_array = expand_operation(current_operation.type, current_operation.value,from_service.control_dict)
            lhs_array.extend(expanded_string_array)
            operations_array.remove(current_operation)
            return expand_as_pulse_program(lhs_array, operations_array, quantum_program, from_service)
 
#  wrapper function which to expand Arithmetic Operation to Pulse sequences 
def prepare_operation_set(data, queue):
 
    quantum_program = QuantumProgramInput.from_string(data)
 
    if( quantum_program.control_instrument.lower().startswith(AcmeService.NAME)):
        from_service = QService(AcmeService.PROGRAM_LOAD_URL, AcmeService.HEADER, AcmeService.PROGRAM_RUN_URL, AcmeService.dict_ACME)
    else:
        from_service = QService(MadridService.PROGRAM_LOAD_URL, MadridService.HEADER, MadridService.PROGRAM_RUN_URL, MadridService.dict_MADRID)
 
    lhs_array = []
    lhs_array = expand_as_pulse_program(lhs_array, quantum_program.operations, quantum_program,from_service) #########LR

    result = prepare_data_set_and_call_service(lhs_array, from_service)

    queue.put(result)  #LR
       
 # function to call Control Instrument service
def prepare_data_set_and_call_service(lhs_array, service):

    try: 
        data_set = {"program_code": lhs_array}
    
        response = requests.post(f"{service.program_load_url}", json.dumps(data_set), headers=service.header)
        data = response.json()
    
        program_id = data['program_id']
        print(' ______________________________________________________  ') 
        print("********---Program Load --********")
        print(data)
        print(program_id)
       

        print("********---Run Program --********")
        x = requests.get(service.program_run_url+program_id)

        print(x.json()['result'])
        print(' ______________________________________________________  ') 


        return x.json()['result']
    except Exception:
        print("Exception on calling service controlled externally to the program")
        return "None"


if __name__ == "__main__":

    print("Welcome to the exercise ! ")
    print("please ensure the control instrument is started and the access urls are properly defined")

    print('____________________________________________________________________________________________________________   ') 

    print("As sample, they can be started with commands \n 1. uvicorn acme_instruments_service.main:app --host 127.0.0.1 --port 8000 \n 2. uvicorn madrid_instruments_service.main:app --host 127.0.0.1 --port 8080 ")

    print('____________________________________________________________________________________________________________   ') 

    #obtain user choice to process small or large type of input
    user_choice_program_type = input("Please enter the choise of processing for generating pulse program for (small or large input) : ")
    
    if user_choice_program_type == "small":
        input_file = 'quantum_program_input.json'
    elif user_choice_program_type == "large":
        input_file = 'large_quantum_program_input.json'
    else:
        print("Incorrect user choice")

    #based on user choice, start processing to convert arithmetic operations to pulse operations
    queue = mp.Queue()
    results = []
    if user_choice_program_type == "small":
        data = json.load(open(input_file))
        prepare_operation_set(data,queue)
        results = [queue.get()]
        
    elif user_choice_program_type == "large":
        data = json.load(open(input_file))
        processes = [mp.Process(target=prepare_operation_set, args=(x, queue)) for x in data]
 
        for p in processes:
            p.start()
 
        for p in processes:
            p.join()
 
        results = [queue.get() for p in processes]

    #print the results
    print("Printing the results of calculation from the Pulse Programs submitted:")
    print('____________________________________________________________________________________________________________   ') 
    print(results)
