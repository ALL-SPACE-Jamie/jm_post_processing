import numpy as np

port_nos = [1,4,5]
port_gain_offsets = [0.1, 0.2, -0.5]
port_phase_offsets = [-1, 2, 4]
frequencies = [27.5, 28.0, 28.5, 29.0]
probe_orientations = [45, -45]

gain = 21.2
phase = 96.1

arrays = {}

for i in range(len(probe_orientations)):
    
    array = np.zeros((len(frequencies), len(port_nos)*2))
    for j in range(len(frequencies)):
        for k in range(len(port_nos)):
            array[j, 2*k] = gain + port_gain_offsets[k]
            array[j, 2*k+1] = phase + port_phase_offsets[k]
            
    arrays[str(i)] = array*1.0
    


frequencies = np.array(frequencies)
frequencies2 = np.resize(frequencies,(len(frequencies),1))
array = np.hstack([frequencies2*0.0+probe_orientations[0], frequencies2, arrays[str(0)]])
array2 = np.hstack([frequencies2*0.0+probe_orientations[0], frequencies2, arrays[str(1)]])


port_headers = []
port_headers.append('probe_orientation')
port_headers.append('Freq [GHz]')
for i in range(len(port_nos)):
    port_headers.append('port' + str(port_nos[i]) + '_f')
    port_headers.append('port' + str(port_nos[i]) + '_Ph')
    
port_headers = np.array(port_headers)
port_headers_2 = np.resize(port_headers, (1, len(port_headers)))

array = np.vstack([port_headers_2, array])
    

        
