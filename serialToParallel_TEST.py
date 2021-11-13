import numpy as np
import numpy.random as ra
import matplotlib.pyplot as plt

import serialToParallel as sp

def print_l(i1, i2, o, offset):
    for v in range(len(o)-offset):
        print(i1[v], " on ", i2[v], " is ", o[v+offset])


def main():

    time = np.linspace(0,50000*3.1415,1024*1024)
    input1 = np.int8(np.cos(time)*100)
    input2 = np.int8(np.sin(time)*100)
    output = np.zeros(len(time), dtype=np.int16)

    stp = sp.serial_to_parallel(12000000, "COM4", 2)
    stp.assign_stream_in([0], "input1")
    stp.input_data(input1, "input1")
    stp.assign_stream_in([1], "input2")
    stp.input_data(input2, "input2")

    stp.assign_stream_out([0, 1], "output")
    stp.output_data(output, "output")

    stp.run()

    plt.plot((np.int16(input1[:-2])) * np.int16((input2[:-2])), label="orig")
    plt.plot((output[2:]), label="RX")

    plt.legend()
    plt.show()

main()
