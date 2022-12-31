import numpy as np

def azel_to_thetaphi(el, az):
    global theta, phi

    cos_theta = np.cos(el) * np.cos(az)
    tan_phi   = np.tan(el) / np.sin(az)
    theta     = np.arccos(cos_theta) * 180.0/np.pi
    phi       = np.arctan2(np.tan(el), np.sin(az)) 
    phi = (phi + 2 * np.pi) % (2 * np.pi) * 180.0/np.pi
    
    return theta, phi
  
def thetaphi_to_azel(theta, phi):
    global az, el

    sin_el = np.sin(phi) * np.sin(theta)
    tan_az = np.cos(phi) * np.tan(theta)
    el = np.arcsin(sin_el) * 180.0/np.pi
    az = np.arctan(tan_az) * 180.0/np.pi
      
    return az, el

thetaphi_to_azel(12.0*np.pi/180, 0.0*np.pi/180)
azel_to_thetaphi(0.31*np.pi/180, 13.20*np.pi/180)

el = 30.1*np.pi/180
az = 4.36*np.pi/180

theta = np.arccos(np.cos(el)*np.cos(az))*180.0/np.pi
phi = ((np.arctan2(np.tan(el), np.sin(az))) + 2 * np.pi) % (2 * np.pi) * 180.0/np.pi