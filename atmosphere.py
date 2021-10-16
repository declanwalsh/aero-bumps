# -*- coding: utf-8 -*-
"""
Created on Tue Mar  2 14:30:56 2021

@author: Declan Walsh
"""

# ---------------------------------------------------
# IMPORTS
# ---------------------------------------------------

import math
import numpy as np

# ---------------------------------------------------
# CONSTANTS
# ---------------------------------------------------

# ATMOSPHERE CONSTANTS
R_EARTH = 20926476  # Radius of Earth (feet)
H_STRATOSPHERE = 65000  # Max height of stratosphere (feet)
H_TROPOSPHERE = 36089.239  # Max height of troposhere (feet)

GAMMA = 1.4  # ratio of specific heats for air (minor change only with temperature - assumed constant for simplicity)
GAMMA_R = 3.5  # GAMMA/(GAMMA-1)
R_GAS = 1717  # Universal gas constant https://www.engineeringtoolbox.com/individual-universal-gas-constant-d_588.html

# CONVERSION FACTORS
PSF_TO_PSI = 0.006944444  # lb/ft^2 to lb/in^2
PSF_TO_PA = 47.8802589  # lb/ft^2 to N/m^2
FPS_TO_KTS = 0.5924838  # ft/s to kts

# SEA LEVEL ISA PROPERTIES
SL_AIR_DENS = 0.0023769  # sea level air density (slug/ft^3)
SL_A = 1116.45  # sea level speed of sound (ft/s)
SL_P = 2116.23  # sea level pressure (psf)

# ---------------------------------------------------
# ATMOSPHERE FUNCTIONS
# ---------------------------------------------------


def standard_atmosphere(h_geometric, T_offset=0):

    # all units are in rankine, slugs and feet
    # heights can be entered as a numpy array or single value
    # returns pressure in psi (not psf as the internal calculated units)
    # TODO: include T_offset in calculations

    try:
        if (h_geometric.any() > H_STRATOSPHERE):
            print("ERROR - height entered {:.4g} too large (> 65,000 feet limit for methods)".format(h_geometric))
            return None
    except Exception:
        if (h_geometric > H_STRATOSPHERE):
            print("ERROR - height entered {:.4g} too large (> 65,000 feet limit for methods)".format(h_geometric))
            return None

    h_geopotential = (R_EARTH/(R_EARTH + h_geometric))*h_geometric

    # constants for troposphere
    T_0_troposphere = 518.67
    lapse_rate_troposphere = 0.00356616
    P_a_troposphere = 2116.22
    P_b_troposphere = 6.87558563248308e-06
    P_c_troposphere = 5.25591641274834
    rho_a_troposphere = 0.00237691267925741
    rho_b_troposphere = 6.87558563248308e-06
    rho_c_troposphere = 4.25591641274834

    # constants for stratosphere
    T_0_stratosphere = 389.97
    P_a_stratosphere = 472.675801650081
    P_b_stratosphere = -4.80637968933164e-05
    P_c_stratosphere = 36089.239
    rho_a_stratosphere = 0.000706115448911997
    rho_b_stratosphere = -4.80637968933164e-05
    rho_c_stratosphere = 36089.239


    T_tropo = T_0_troposphere - lapse_rate_troposphere * h_geometric
    P_tropo = P_a_troposphere*(1 - P_b_troposphere * h_geometric)**P_c_troposphere
    rho_tropo = rho_a_troposphere*(1 - rho_b_troposphere * h_geometric)**rho_c_troposphere
    la_tropo = h_geometric <= H_TROPOSPHERE

    T_strato = T_0_stratosphere
    P_strato = P_a_stratosphere * math.e**(P_b_stratosphere * (h_geometric - P_c_stratosphere))
    rho_strato = rho_a_stratosphere * math.e**(rho_b_stratosphere * (h_geometric - rho_c_stratosphere))
    la_strato = (h_geometric <= H_STRATOSPHERE) * (h_geometric > H_TROPOSPHERE)

    T = T_tropo * la_tropo + T_strato * la_strato
    P = P_tropo * la_tropo + P_strato * la_strato
    rho = rho_tropo * la_tropo + rho_strato * la_strato

    a = np.sqrt(GAMMA * R_GAS * T)

    atmosphere_dict = {"T": T, "P": P*PSF_TO_PSI, "rho": rho, "a": a}

    return atmosphere_dict

"""
Calculates the altitude of operation from the ambient pressure

TODO - create tests for this function
"""

def altitude_from_height(P, unit):

    # converts pressure in psf
    # all units are in rankine, slugs and feet
    # heights can be entered as a numpy array or single value
    
    if unit.upper() == "PA":
        P = P / PSF_TO_PA
    elif unit.upper() == "PSI":
        P = P / PSF_TO_PA
    elif unit.upper == "PSF":
        P = P
    else:
        print("ERROR - Invalid unit selected in altitude_from_height")
        return None

    P_a_troposphere = 2116.22
    P_b_troposphere = 6.87558563248308e-06
    P_c_troposphere = 5.25591641274834

    P_a_stratosphere = 472.675801650081
    P_b_stratosphere = -4.80637968933164e-05
    P_c_stratosphere = 36089.239

    # standard_atmosphere returns in PSI and must be converted to PSF
    P_troposphere_limit = standard_atmosphere(H_TROPOSPHERE)["P"]/PSF_TO_PSI
    P_stratosphere_limit = standard_atmosphere(H_STRATOSPHERE)["P"]/PSF_TO_PSI
    
    la_tropo = P > P_troposphere_limit
    la_strato = (P > P_stratosphere_limit) * (P <= P_troposphere_limit)

    h_tropo = (1 - (P/P_a_troposphere)**(1/P_c_troposphere))/P_b_troposphere
    h_strato = (np.log(P/P_a_stratosphere))/P_b_stratosphere + - P_c_stratosphere

    h = la_tropo*h_tropo + la_strato*h_strato

    return h

# ---------------------------------------------------
# AIRSPEED CONVERSION FUNCTIONS
# ---------------------------------------------------


"""
Airspeed conversion functions all assume:
    - Altitude in feet
    - Airspeed in ft/second
"""


def M_to_EAS(M, altitude):
    """

    Parameters
    ----------
    M : float
        Mach number
    altitude : float
        Geometric altitude (ft)

    Returns
    -------
    EAS : float
        Equivalent airspeed (ft/s)

    """

    atmos = standard_atmosphere(altitude)

    TAS = M_to_TAS(M, altitude)
    EAS = np.sqrt(atmos["rho"]/SL_AIR_DENS * TAS**2)

    return EAS


def EAS_to_M(EAS, altitude):
    """

    Parameters
    ----------
    EAS : float
        Equivalent airspeed (ft/s)
    altitude : float
        Geometric altitude (ft)

    Returns
    -------
    M : float
        Mach number

    """

    atmos = standard_atmosphere(altitude)

    rho = atmos["rho"]
    a = atmos["a"]

    TAS = EAS * (SL_AIR_DENS/rho)**(0.5)
    M = TAS / a

    return M


def M_to_CAS(M, altitude):
    """

    Parameters
    ----------
    M : float
        Mach number
    altitude : float
        Geometric altitude (ft)

    Returns
    -------
    CAS : float
        Calibrated airspeed (ft/s)

    """

    atmos = standard_atmosphere(altitude)
    P_local = atmos["P"]/PSF_TO_PSI  # local static pressure at altitude (psf)

    # Isentropic flow assumed
    # https://en.wikipedia.org/wiki/Impact_pressure
    q_c = P_local * ((1 + (M**2)*(GAMMA-1)/2)**(GAMMA/(GAMMA-1)) - 1)

    CAS = SL_A * (5 * ((q_c/SL_P + 1)**(2/7) - 1))**(0.5)

    return CAS


def CAS_to_M(CAS, altitude):
    """

    Rearranged formulas in M_TO_CAS

    Parameters
    ----------
    CAS : float
        Calibrated airspeed (ft/s)
    altitude : float
        Geometric altitude (ft)

    Returns
    -------
    M : float
        Mach number

    """

    # Convert back to psf
    atmos = standard_atmosphere(altitude)
    P_local = atmos["P"]/PSF_TO_PSI  # local static pressure at altitude (psf)

    q_c = SL_P * ((((CAS/SL_A)**2)/5 + 1)**(GAMMA_R) - 1)  # dynamic/impact pressure

    # Isentropic flow assumed
    # https://en.wikipedia.org/wiki/Impact_pressure
    M = ((2/(GAMMA-1) * ((q_c/P_local + 1)**(1/GAMMA_R) - 1)))**(0.5)

    return M


def EAS_to_CAS(EAS, altitude):
    """

    Parameters
    ----------
    EAS : float
        Equivalent airspeed (ft/s)
    altitude : float
        Geometric altitude (ft)

    Returns
    -------
    CAS : float
        Calibrated airspeed (ft/s)

    """

    M = EAS_to_M(EAS, altitude)
    CAS = M_to_CAS(M, altitude)

    return CAS


def M_to_TAS(M, altitude):
    """

    Uses local speed of sound from static temperature at altitude to calculate TAS

    Parameters
    ----------
    M : float
        Mach number
    altitude : float
        Geometric altitude (ft)

    Returns
    -------
    TAS : float
        true airspeed (ft/s)

    """

    atmos = standard_atmosphere(altitude)
    a = atmos["a"]
    TAS = M*a  # TAS is in fps

    return TAS


def CAS_to_TAS(CAS, altitude):
    """
    converts CAS to M and then to TAS

    Parameters
    ----------
    CAS : float
        calibrated airspeed (ft/s)
    altitude : float
        geometric altitude (ft)

    Returns
    -------
    TAS : float
        true airspeed (ft/s)

    """

    M = CAS_to_M(CAS, altitude)
    TAS = M_to_TAS(M, altitude)
    TAS = TAS*FPS_TO_KTS

    return TAS


def main():
    print("No main program - refer to separate test file")


if __name__ == "__main__":

    main()
