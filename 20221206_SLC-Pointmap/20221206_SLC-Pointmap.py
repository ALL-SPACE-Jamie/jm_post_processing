import json
import numpy as np
import matplotlib.pyplot as plt; plt.close()

data = json.load(open("beampointing.json", "r"))

outData = []

thetaMap = np.linspace(0,80,num=5)
phiMap = np.linspace(0,360-90,num=5)
beamMap = np.array([1])

plt.figure()

# loop
for phi in phiMap:
    for theta in thetaMap:
        for beam in beamMap:
            if not (theta == 0 and phi !=0):
                # Lens 1
                pointDict = {}
                pointDict["beam"] = beam
                pointDict["beam_id"] = beam-1
                pointDict["config_version"] = 5
                pointDict["lens_1_disabled"] = 'false'
                pointDict["lens_2_disabled"] = 'true'
                pointDict["lens_3_disabled"] = 'true'
                pointDict["phi"] = phi
                pointDict["theta"] = theta
                outData.append(pointDict)
    
                # Lens 2
                pointDict = {}
                pointDict["beam"] = beam
                pointDict["beam_id"] = beam-1
                pointDict["config_version"] = 5
                pointDict["lens_1_disabled"] = 'true'
                pointDict["lens_2_disabled"] = 'false'
                pointDict["lens_3_disabled"] = 'true'
                pointDict["phi"] = phi
                pointDict["theta"] = theta
                outData.append(pointDict)
    
                # Lens 3
                pointDict = {}
                pointDict["beam"] = beam
                pointDict["beam_id"] = beam-1
                pointDict["config_version"] = 5
                pointDict["lens_1_disabled"] = 'true'
                pointDict["lens_2_disabled"] = 'true'
                pointDict["lens_3_disabled"] = 'false'
                pointDict["phi"] = phi
                pointDict["theta"] = theta
                outData.append(pointDict)
    
                # Full TLM
                pointDict = {}
                pointDict["beam"] = beam
                pointDict["beam_id"] = beam-1
                pointDict["config_version"] = 5
                pointDict["lens_1_disabled"] = 'false'
                pointDict["lens_2_disabled"] = 'false'
                pointDict["lens_3_disabled"] = 'false'
                pointDict["phi"] = phi
                pointDict["theta"] = theta
                outData.append(pointDict)
                
                plt.plot(theta, phi, "ko-")
                plt.xlabel("theta"); plt.ylabel("phi"); plt.grid("on")
            
with open("20221202_beamPointing_theta0-70-stp-10_phi0-315-stp45_beam1_L1L2L3FT.txt", "w") as output:
    output.write(str(outData))

json_string = json.dumps(outData)
with open("20221202_beamPointing_theta0-70-stp-10_phi0-315-stp45_beam1_L1L2L3FT.json", "w") as outfile:
    outfile.write(json_string)
    
# Test for git

            

            
    
    
        
