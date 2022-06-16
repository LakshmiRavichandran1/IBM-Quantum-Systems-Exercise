# The MIT License (MIT)
# Copyright © 2022 IBM Quantum
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the “Software”), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

# This tool is meant to generate a list of valid arithmetic quantum
# programs of different sizes and forms that could be useful to test
# the input of the proposed IBM Quantum Systems hiring excercise.


import json
import random
import uuid
from argparse import ArgumentParser
from dataclasses import dataclass
from enum import IntEnum
from json import JSONEncoder
from typing import List


class ArithmeticOperation(IntEnum):
    Sum = 1
    Mul = 2
    Div = 3
    InitState = 4


class ControlInstrument(IntEnum):
    Acme = 1
    Madrid = 2


@dataclass
class Operation:
    type: ArithmeticOperation
    value: int


@dataclass
class QuantumProgram:
    id: str
    control_instrument: ControlInstrument
    initial_value: int
    operations: List[Operation]


class MyEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Operation):
            return {"type": o.type.name, "value": o.value}

        if isinstance(o, QuantumProgram):
            o.control_instrument = o.control_instrument.name

        return o.__dict__


def generate_quantum_programs(number_of_operations, number_of_programs):
    quantum_programs = []
    for i in range(number_of_programs):
        arithmetic_opers = []
        for j in range(number_of_operations):
            arithmetic_opers.append(
                Operation(
                    type=ArithmeticOperation(random.randint(1, 3)),
                    value=random.randint(1, 10),
                )
            )
        quantum_programs.append(
            QuantumProgram(
                id=str(uuid.UUID(int=random.getrandbits(128))),
                control_instrument=ControlInstrument(random.randint(1, 2)),
                initial_value=random.randint(0, 10),
                operations=arithmetic_opers,
            )
        )

    return quantum_programs


def to_json(quantum_programs):
    return json.dumps(quantum_programs, cls=MyEncoder)


def main():
    parser = ArgumentParser(
        description="This is a Quantum Program random json generator for the Quantum Systems "
        "hiring test 2022"
    )
    parser.add_argument(
        "-m",
        "--programs",
        metavar="M",
        type=int,
        default=1,
        dest="programs",
        help="number of programs (default: %(default)s)",
    )
    parser.add_argument(
        "-n",
        "--operations",
        metavar="N",
        type=int,
        default=3,
        dest="operations",
        help="number of random arithmetic operations per program (default: %(default)s)",
    )
    parser.add_argument(
        "-s",
        "--seed",
        metavar="S",
        type=int,
        dest="seed",
        help="random seed used for the generation (default: %(default)s)",
    )
    args = parser.parse_args()

    if args.seed:
        random.seed(args.seed)

    quantum_programs = generate_quantum_programs(args.operations, args.programs)
    quantum_programs_json = to_json(quantum_programs)

    print(quantum_programs_json)


if __name__ == "__main__":
    main()
