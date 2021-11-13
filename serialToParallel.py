import serial
import numpy as np
import time

class serial_to_parallel:

    #The challenge is to work out how to assign the number of bytes correctly
    # Ultimately creating a tree structure to assign each TDM stream to - a
    # list of tuples where the first is the stream, the second is a byte shift

    def __init__(self, baud, port, no_bytes):
        self.baud = baud
        self.port = port
        self.no_bytes = no_bytes
        self.arrangement_in = [-1] * no_bytes
        self.arrangement_out = [-1] * no_bytes
        self.target_list_in = {}
        self.target_list_out = {}
        self.ser = serial.Serial(port, baud, timeout=1)

    def assign_stream(self, bytes, target, arrangement):
        for shift in range(len(bytes)):
            if (arrangement[bytes[shift]] == -1):
                arrangement[bytes[shift]] = (shift, target)
            else:
                print("ERROR: Bytes are already assigned")

    def assign_stream_in(self, bytes, target):
        self.assign_stream(bytes, target, self.arrangement_in)

    def assign_stream_out(self, bytes, target):
        self.assign_stream(bytes, target, self.arrangement_out)

    def get_stride(self, target):
        t = type(target[0])
        output = 0
        if (t == np.int8 or t == np.uint8):
            output = 1
        elif (t == np.int16 or t == np.uint16):
            output = 2
        elif (t == np.int32 or t == np.uint32):
            output = 4
        elif (t == np.int64 or t == np.uint64):
            output = 8
        else:
            print("ERROR: Unrecognised type")
        return output

    def conv(self, target, data_from_fpga, y, shift):
        """Extremely simple function to return data_from_fpga
            as the correct type.
           Slices the data, and converts it.
        """
        t = type(target[0])
        print(t)
        print(self.no_bytes)
        return t(data_from_fpga[y::self.no_bytes]) << t(8*shift)

    def is_valid_type(self, target):
        type_in = type(target[0])
        if (type_in == np.int64 or type_in == np.int32
            or type_in == np.int16 or type_in== np.int8 or
            type_in == np.uint64 or type_in == np.uint32
            or type_in == np.uint16 or type_in == np.uint8):
            output = 1
        else:
            output = 0
        return output

    def input_data(self, stream, index):
        if (type(stream) != np.ndarray):
            print("ERROR: input must be numpy array")
        else:
            if (not self.is_valid_type(stream)):
                print("ERROR: input must be array of type ints")
            else:
                self.target_list_in[index] = stream

    def output_data(self, stream, index):
        if (type(stream) != np.ndarray):
            print("ERROR: output must be numpy array")
        else:
            if (not self.is_valid_type(stream)):
                print("ERROR: output must be array of type ints")
            else:
                self.target_list_out[index] = stream

    def run(self):
        ##Work out the size of our data
        max_len = 0;
        for stream in list(self.target_list_in.values()):
            print(stream)
            if (len(stream) > max_len):
                max_len = len(stream)
        data_list = bytearray(max_len * self.no_bytes)
        print(len(data_list))

        #Create a byte object to store our data
        for i in range(len(self.arrangement_in)):
                byte = self.arrangement_in[i] #Fetch what to do from the arrangement
                if (byte != -1):
                    target = self.target_list_in[byte[1]] #Then get the stream info
                    stride = self.get_stride(target)
                    until = len(target) * self.no_bytes
                    data_list[i:until+i:self.no_bytes] = target.tobytes()[byte[0]::stride]

        dataFlush = self.ser.readline()

        data_from_fpga = np.zeros(max_len * self.no_bytes, dtype=np.uint8)
        for ii in range(np.int32((max_len*self.no_bytes) / (8*1024))):
            self.ser.write(data_list[ii*8*1024:(ii+1)*8*1024])
            data_raw = self.ser.read(8*1024)
            data_from_fpga[ii*8*1024:(ii+1)*8*1024] = np.frombuffer(data_raw, dtype=np.uint8)

        #Write our data to various arrays
        for y in range(len(self.arrangement_out)):
                byte = self.arrangement_out[y] #Fetch what to do from the arrangement
                if (byte != -1):
                    target = self.target_list_out[byte[1]] #Then get the stream info
                    #print(np.logical_or(target, self.conv(target, data_from_fpga, y, byte[0])))
                    target += self.conv(target, data_from_fpga, y, byte[0])

    def show(self):
        print("Input assignment (shift, target)")
        print(self.arrangement_in, "\n")
        print("Output assignment (shift, target)")
        print(self.arrangement_out, "\n")
        print("Input Targets")
        for target in list(self.target_list_in.keys()):
            print( id(self.target_list_in[target]), " is ",  target)
        print("Output Targets")
        for target in list(self.target_list_out.keys()):
            print( id(self.target_list_out[target]), " is ",  target)
        print(" ")
