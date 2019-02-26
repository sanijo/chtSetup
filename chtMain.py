#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 21 13:17:19 2019

@author: sanijo
"""

import chtFunctions as cht 
import os           
    
def main():

    cwd = os.getcwd()
    
    path = '/home/sanijo/OpenFOAM/sanijo-4.1/run/CHT_DENII'
    
    solidRegions, fluidRegions = cht.getRegions(path)
    
    regions = solidRegions + fluidRegions
       
    print("Solid region(s): " + str(solidRegions))
    print("Fluid region(s): " + str(fluidRegions))
     
    cht.createFolders(path,regions)
    
    cht.fluentMeshToFoam(path, regions)
    
    cht.createInterface(path, regions)
    
    cht.set0Solid(path, solidRegions)
    cht.set0Fluid(path, fluidRegions)

    os.chdir(cwd)
    
if __name__ == "__main__":
    main()

