#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 21 13:17:19 2019

@author: sanijo
"""

import chtFunctions as cht 
import tkinter as tk
from tkinter import filedialog
import os          
    
def main():
    
    #Prompt user for script path
    root = tk.Tk()
    root.withdraw()
    script_path = filedialog.askdirectory()
    os.chdir(script_path)
#    cwd = os.getcwd()
    
    #Prompt user for case path
#    root = tk.Tk()
#    root.withdraw()
#    path = filedialog.askdirectory()
    
    #Specify path directly
    path = '/home/sanijo/OpenFOAM/sanijo-4.1/run/Ferrari/bornaCht'
    
    solidRegions, fluidRegions = cht.getRegions(path)
    
    regions = solidRegions + fluidRegions
       
    print("Solid region(s): " + str(solidRegions))
    print("Fluid region(s): " + str(fluidRegions))
     
    cht.createFolders(path,regions)
    
#    cht.fluentMeshToFoam(path, regions, check_mesh=True)
    
    cht.createInterface(path, regions, 'design')
    
    cht.set0Solid(path, solidRegions)
    cht.set0Fluid(path, fluidRegions)
    
    print('\nDone!')

    os.chdir(script_path)
    
if __name__ == "__main__":
    main()

