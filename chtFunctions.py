#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 21 13:17:19 2019

@author: sanijo

Works with specific enviroment
"""

from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
import  os, subprocess             

def getRegions(path):
    """Function which takes case path as parameter and returns solid and fluid zones list.
       Changed:     p_error(self,p) in ParsedParameterFile.py:
           def p_error(self,p):
               if self.inBinary:
                   raise BinaryParserError("Problem reading binary", p) # .type, p.lineno
               else:
                   self.yacc.errok()"""

    curr_files = os.listdir(path+'/constant')  
    
    solid = []
    fluid = []
    try:
        if 'regionProperties' in curr_files:
            f = ParsedParameterFile(path+'/constant/regionProperties', boundaryDict=True)
            solid = f[1]
            fluid = f[3]
        return solid, fluid
    except:
        print('File mising or ParsedParameterFile.py have not been changed. (check documentation)')
        
def addRegions(path, solids_list, fluids_list):
    """Function which takes case path  and fluids/solids lists as parameters and appends 
       solid and fluid zones to  new list. Missing ; at the end of file!
       Changed:     p_error(self,p) in ParsedParameterFile.py:
           def p_error(self,p):
               if self.inBinary:
                   raise BinaryParserError("Problem reading binary", p) # .type, p.lineno
               else:
                   self.yacc.errok()"""

    curr_files = os.listdir(path+'/constant')  

    try:
        if 'regionProperties' in curr_files:
            f = ParsedParameterFile(path+'/constant/regionProperties', boundaryDict=True)
            f[1] = []
            f[3] = []
            for solid in solids_list:
                f[1].append(solid)
            for fluid in fluids_list:
                f[3].append(fluid)
            f.writeFile()
    except:
        print('File mising or ParsedParameterFile.py have not been changed. (check documentation)')

def createFolders(path, regions):
    """Function that creates empty folders inside 0, constant and system based on region names.
       Input: -path to case folder
              -list of regions (getRegions())"""
    
    basic_folders = ['0', 'constant', 'system']
    
    for folder in basic_folders:
        os.chdir(path+'/'+folder)
        for name in regions:
            os.makedirs(name, exist_ok=True)
            
def fluentMeshToFoam(path, regions, check_mesh=False, silent=False):
    """"Function for conversion Fluent mesh to foam.
        Mesh files must be inside case folder, not in any other folder!
        If you want to see OpenFOAM output in terminal erase: stdout=open(os.devnull, 'wb').        
        Input: -case path
               -regions: list (getRegions(path))
               -silent=False (True or False)
               -check_mesh=False (True or False)"""
               
    try:
        if check_mesh==False:
            if silent==False:
                for region in regions:
                    name = region+'.msh'
                    os.chdir(path)
                    subprocess.call(['fluent3DMeshToFoam', name])
                    os.chdir(path+'/constant')
                    subprocess.call(['mv', 'polyMesh', region])
            elif silent==True:
                for region in regions:
                    name = region+'.msh'
                    os.chdir(path)
                    subprocess.call(['fluent3DMeshToFoam', name], stdout=open(os.devnull, 'wb'))
                    os.chdir(path+'/constant')
                    subprocess.call(['mv', 'polyMesh', region], stdout=open(os.devnull, 'wb'))
            else:
                print ('Wrong input for parameter silent!')
        elif check_mesh==True:
            if silent==False:
                for region in regions:
                    name = region+'.msh'
                    os.chdir(path)
                    subprocess.call(['fluent3DMeshToFoam', name])
                    subprocess.call(['checkMesh'])
                    os.chdir(path+'/constant')
                    subprocess.call(['mv', 'polyMesh', region])
            elif silent==True:
                for region in regions:
                    name = region+'.msh'
                    os.chdir(path)
                    subprocess.call(['fluent3DMeshToFoam', name], stdout=open(os.devnull, 'wb'))
                    subprocess.call(['checkMesh'], stdout=open(os.devnull, 'wb'))
                    os.chdir(path+'/constant')
                    subprocess.call(['mv', 'polyMesh', region], stdout=open(os.devnull, 'wb'))
            else:
                print ('Wrong input for parameter silent!')
        else:
            print('Wrong input for parameter check_mesh!')
    except:
        print('fluentMeshToFoam failed!')

def getNumberOfFaces(key, f):
    """Sum up faces number"""
    
    sum = 0
    for i in range(len(f)):
        if isinstance(f[i], str):
            if key in f[i]:
                sum += f[i+1]['nFaces']  
    return sum
     
def getStartFace(key, f):
    """Get start face"""
        
    startFace = 0
    for i in range(len(f)):
        if isinstance(f[i], str):
            if key in f[i]:
                startFace = f[i+1]['startFace']
                break
    return startFace
        
def createInterface(path, regions, keyword):
    """Function which determines name and type of boundary surface inside 
       polyMesh/boundary. If the name of the boundary surface contains "interface"
       expression, function changes it's type to mappedWall, and adds sampleMode, 
       sampleRegion and samplePatch.
       Naming of the interface patches should look like this: fluid_housing_interface-
       housing_fluid_interface. Zones should have names coresponding to the ones in
       patch names (e.g. housing, fluid).
       Input: -path to case directory
              -regions array"""
              
##This is just for testing ParsedParameterFile   ...need to comment all the other stuff 
#    for region in regions:        
#        os.chdir(path+'/constant/'+region+'/polyMesh')
#        print('\nCurrently in folder '+region+'\n')
#        boundary_file = os.getcwd()+'/boundary'
#        print(boundary_file)
#
#        f = ParsedParameterFile(boundary_file, boundaryDict=True, treatBinaryAsASCII=True)
#        print(f)

    try:   
        for region in regions:        
            os.chdir(path+'/constant/'+region+'/polyMesh')
            print('\nCurrently in folder '+region+'\n')
            boundary_file = os.getcwd()+'/boundary'

            f = ParsedParameterFile(boundary_file, boundaryDict=True, treatBinaryAsASCII=True)              

            for i in range(len(f)):
                if isinstance(f[i], str):
                    if 'inlet' in f[i]:
                        if keyword in f[i]:
                            split = f[i].split('-')
                            key = str(split[0]) 
                            nFaces = getNumberOfFaces(key, f)
                            startFace = getStartFace(key, f)
                            keys = ['nFaces', 'startFace']
                            values = [nFaces, startFace]
                            for key, value in (zip(keys, values)):
                                f[i] = str(split[0])
                                f[i+1][key] = value 
                        if keyword not in f[i]:
                            keys = ['type', 'inGroups']
                            values = ['patch', '1(patch)']
                            for key, value in (zip(keys, values)):
                                f[i+1][key] = value
                    if 'outlet' in f[i]:
                        if keyword in f[i]:
                            split = f[i].split('-')
                            key = str(split[0]) 
                            nFaces = getNumberOfFaces(key, f)
                            startFace = getStartFace(key, f)
                            keys = ['nFaces', 'startFace']
                            values = [nFaces, startFace]
                            for key, value in (zip(keys, values)):
                                f[i] = str(split[0])
                                f[i+1][key] = value 
                        if keyword not in f[i]:
                            keys = ['type', 'inGroups']
                            values = ['patch', '1(patch)']
                            for key, value in (zip(keys, values)):
                                f[i+1][key] = value
                    if 'interface' in f[i]:
                        if keyword in f[i]:
                            split = f[i].split('_')
                            samplePatch = str(split[1])+'_'+str(split[0])+'_interface'
                            region = str(split[1])
                            key = str(split[0]) + '_' + str(split[1])
                            nFaces = getNumberOfFaces(key, f)
                            startFace = getStartFace(key, f)
                            keys = ['type', 'inGroups', 'nFaces', 'startFace', 'sampleMode', 'sampleRegion', 'samplePatch']
                            values = ['mappedWall', '1(mappedWall)', nFaces, startFace, 'nearestPatchFace', split[1], samplePatch]
                            for key, value in (zip(keys, values)):
                                f[i] = str(split[0])+'_'+str(split[1])+'_interface'
                                f[i+1][key] = value  
                        else:
                            split = f[i].split('_')
                            samplePatch = str(split[1])+'_'+str(split[0])+'_'+str(split[2])
                            region = str(split[1])
                            keys = ['type', 'inGroups', 'sampleMode', 'sampleRegion', 'samplePatch']
                            values = ['mappedWall', '1(mappedWall)', 'nearestPatchFace', region, samplePatch]
                            for key, value in (zip(keys, values)):
                                f[i+1][key] = value  
                    if 'symmetry' in f[i]:
                        if keyword in f[i]:
                            split = f[i].split('_')
                            key = str(split[0]) + '_symmetry'
                            nFaces = getNumberOfFaces(key, f)
                            startFace = getStartFace(key, f)
                            keys = ['type', 'inGroups', 'nFaces', 'startFace']
                            values = ['symmetry', '1(symmetry)', nFaces, startFace]
                            for key, value in (zip(keys, values)):
                                f[i] = str(split[0])+'_symmetry'
                                f[i+1][key] = value   
                        else:
                            keys = ['type', 'inGroups']
                            values = ['symmetry', '1(symmetry)']
                            for key, value in (zip(keys, values)):
                                f[i+1][key] = value
                    if 'adiabatic' in f[i]:
                        if keyword in f[i]:
                            split = f[i].split('_')
                            key = str(split[0]) + '_adiabatic'
                            nFaces = getNumberOfFaces(key, f)
                            startFace = getStartFace(key, f)
                            keys = ['nFaces', 'startFace']
                            values = [nFaces, startFace]
                            for key, value in (zip(keys, values)):
                                f[i] = str(split[0])+'_adiabatic'
                                f[i+1][key] = value 
 
            #Cleanup of duplicates           
            for i in range(len(f)-2):
                if isinstance(f[i], str):
                    if f[i+2] == f[i]:
                        f[i+3]['nFaces'] = f[i+1]['nFaces']                
            container = []
            for i in range(len(f)): 
                if f[i] not in container:
                    container.append(f[i])
                else:
                    f[i] = ''  
                
#            print(f)
            
            f.writeFile()  
            print(region + ' boundary done!\n')
    except:
        print('Missing some folders, or wrong list input!') 
        
#################################-solid 0-#####################################
def getPatchInfo(path, region):
    """Function which determines name and type of boundary surface inside 
       polyMesh/boundary.
       Input: -path to case directory"""
    
    os.chdir(path+'/constant/'+region+'/polyMesh')
    boundary_file = os.getcwd()+'/boundary'
    f = ParsedParameterFile(boundary_file, boundaryDict=True)
    patches = []
    types = []
    patch_info = {}
    i = -1
    for n in f:
        i += 1
        if type(n) is str:
            patches.append(n)
        if isinstance(n, dict):
            types.append(f[i]['type'])
    for key, val in (zip(patches, types)):
        patch_info[key]=val
#    print('\nBoundary surfaces in ' + str(region) + ' polyMesh are: ' + str(patches))
#    print('Boundary surface types are: ' + str(types) + '\n')
    
    return patch_info  

def setPsolid(path, region, patch_info):
    """Setup p file for solid"""
   
    os.chdir(path+'/0/'+region)
    file = path+'/0/'+region+'/p'
    f = ParsedParameterFile(file)
    
    print('\nSetting p (solid) file..')
    
    f['boundaryField']['".*"'] = {'type': 'calculated','value': 'uniform 0'}
    
    for key, value in patch_info.items():
        if 'symmetry' in key:
            f['boundaryField']['".*_symmetry"'] = {'type': 'symmetry'}
    
    f.writeFile()
    
def setTsolid(path, region, patch_info):
    """Setup T file for solid"""
    
    os.chdir(path+'/0/'+region)
    file = path+'/0/'+region+'/T'
    f = ParsedParameterFile(file)
    
    print('\nSetting T (solid) file..')
    
    switch = str(input('\nRegion '+region+' have isotropic (1) or anisotropic (2) properties? '))
    
    for key, value in patch_info.items():
        if 'adiabatic' in key:
            if '".*_adiabatic"' not in f['boundaryField']:
                f['boundaryField']['".*_adiabatic"'] = {'type': 'zeroGradient'}
        if 'interface' in key:
            if '".*_interface"' not in f['boundaryField']:
                if switch == '1':
                    f['boundaryField']['".*_interface"'] = {'type': 'compressible::turbulentTemperatureCoupledBaffleMixed',
                     'value': 'uniform 293.15', 'kappaMethod': 'solidThermo', 'kappaName': 'none', 'Tnbr': 'T'}
                if switch == '2':
                    f['boundaryField']['".*_interface"'] = {'type': 'compressible::turbulentTemperatureCoupledBaffleMixed',
                     'value': 'uniform 293.15', 'kappaMethod': 'directionalSolidThermo', 'kappaName': 'none', 'Tnbr': 'T'}
        if 'symmetry' in key:
            if '".*_symmetry"' not in f['boundaryField']:
                f['boundaryField']['".*_symmetry"'] = {'type': 'symmetry'}
        if 'heat_in' in key:
            if '".*_heat_in"' not in f['boundaryField']:
                heat = str(input('\nq [heat flux] value for patch '+str(key)+': '))
                f['boundaryField']['".*_heat_in"'] = {'type': 'externalWallHeatFluxTemperature', 'kappaMethod': 'solidThermo',
                  'q uniform ': heat, 'value': 'uniform 293.15', 'kappaName': 'none'}
    
    f.writeFile()
   
def set0Solid(path, solidRegions):
    """Setup 0 solid files from templates"""
  
    filesSolid = ['p', 'T']
    os.chdir(path)
    for region in solidRegions:
        for file in filesSolid:
            subprocess.call(['cp', '-r', path+'/templates/'+file, path+'/0/'+region])
        
    for region in solidRegions:
       patchInfo = getPatchInfo(path, region)
       setPsolid(path, region, patchInfo)
       setTsolid(path, region, patchInfo)
        
###################################-fluid0-####################################

def setPfluid(path, region, patch_info):
    """Setup p file for fluid"""
   
    os.chdir(path+'/0/'+region)
    file = path+'/0/'+region+'/p'
    f = ParsedParameterFile(file)
    
    print('\nSetting p (fluid) file..')
    
    f['boundaryField']['".*"'] = {'type': 'calculated','value': 'uniform 0'}
    
    for key, value in patch_info.items():
        if 'symmetry' in key:
            f['boundaryField']['".*_symmetry"'] = {'type': 'symmetry'}
    
    f.writeFile()
    
def setTfluid(path, region, patch_info):
    """Setup T file for fluid"""
   
    os.chdir(path+'/0/'+region)
    file = path+'/0/'+region+'/T'
    f = ParsedParameterFile(file)
    
    print('\nSetting T (fluid) file..')
    
    for key, value in patch_info.items():
        if 'adiabatic' in key:
            if '".*_adiabatic"' not in f['boundaryField']:
                f['boundaryField']['".*_adiabatic"'] = {'type': 'zeroGradient'}
        if 'interface' in key:
            if '".*_interface"' not in f['boundaryField']:
                f['boundaryField']['".*_interface"'] = {'type': 'compressible::turbulentTemperatureCoupledBaffleMixed',
                 'value': 'uniform 293.15', 'kappaMethod': 'fluidThermo', 'Tnbr': 'T'}
        if 'symmetry' in key:
            if '".*_symmetry"' not in f['boundaryField']:
                f['boundaryField']['".*_symmetry"'] = {'type': 'symmetry'}
        if 'inlet' in key:
            f['boundaryField'][key] = {'type': 'fixedValue', 'value': 'uniform 293.15'}
        if 'outlet' in key:
            f['boundaryField'][key] = {'type': 'zeroGradient'}
        if 'heat_in' in key:
            heat = str(input('\nq [heat flux] value for patch '+str(key)+': '))
            f['boundaryField'][key] = {'type': 'externalWallHeatFluxTemperature', 'kappaMethod': 'fluidThermo',
              'q': heat, 'value': 'uniform 293.15', 'kappaName': 'none'}
    
    f.writeFile()
    
def setUfluid(path, region, patch_info):
    """Setup U file for fluid"""
   
    os.chdir(path+'/0/'+region)
    file = path+'/0/'+region+'/U'
    f = ParsedParameterFile(file)
    
    print('\nSetting U (fluid) file..')
    
    switch = str(input('\nflowRateInletVelocity (write fr) or fixedValue (wite fv)?'))
    
    for key, value in patch_info.items():
        if 'adiabatic' in key:
            if '".*_adiabatic"' not in f['boundaryField']:
                f['boundaryField']['".*_adiabatic"'] = {'type': 'noSlip'}
#                f['boundaryField']['".*_adiabatic"'] = {'type': 'fixedValue', 'value': 'uniform (0 0 0)'}
        if 'interface' in key:
            if '".*_interface"' not in f['boundaryField']:
                f['boundaryField']['".*_interface"'] = {'type': 'fixedValue', 'value': 'uniform (0 0 0)'}
        if 'symmetry' in key:
            if '".*_symmetry"' not in f['boundaryField']:
                f['boundaryField']['".*_symmetry"'] = {'type': 'symmetry'}
        if 'inlet' in key:
            if switch == 'fv':
                x = str(input('\nVelocity x component [m/s] value for patch '+str(key)+': '))
                y = str(input('\nVelocity y component [m/s] value for patch '+str(key)+': '))
                z = str(input('\nVelocity z component [m/s] value for patch '+str(key)+': '))
                vector = 'uniform ('+str(x)+' '+str(y)+' '+str(z)+')'
                f['boundaryField'][key] = {'type': 'fixedValue', 'value': vector}
            if switch == 'fr':
                x = str(input('\nVolume flow rate [m3/s] on patch '+str(key)+': '))
                f['boundaryField'][key] = {'type': 'flowRateInletVelocity', 'volumetricFlowRate':'constant '+x,
                 'extrapolateProfile': 'false', 'value': 'uniform (0 0 0)'}                
        if 'outlet' in key:
            f['boundaryField'][key] = {'type': 'inletOutlet', 'value': 'uniform (0 0 0)', 'inletValue': 'uniform (0 0 0)'}
        if 'heat_in' in key:
            f['boundaryField'][key] = {'type': 'fixedValue', 'value': 'uniform (0 0 0)'}
    
    f.writeFile()
    
def setPrgh(path, region, patch_info):
    """Setup p_rgh (fluid) file for fluid"""
   
    os.chdir(path+'/0/'+region)
    file = path+'/0/'+region+'/p_rgh'
    f = ParsedParameterFile(file)
    
    print('\nSetting p_rgh file..')
    
    for key, value in patch_info.items():
        if 'adiabatic' in key:
            if '".*_adiabatic"' not in f['boundaryField']:
                f['boundaryField']['".*_adiabatic"'] = {'type': 'fixedFluxPressure'} #type': 'zeroGradient', 'value': 'uniform 101325'
        if 'interface' in key:
            if '".*_interface"' not in f['boundaryField']:
                f['boundaryField']['".*_interface"'] = {'type': 'fixedFluxPressure'} #type': 'zeroGradient', 'value': 'uniform 101325'
        if 'symmetry' in key:
            if '".*_symmetry"' not in f['boundaryField']:
                f['boundaryField']['".*_symmetry"'] = {'type': 'symmetry'}
        if 'inlet' in key:
            f['boundaryField'][key] = {'type': 'fixedFluxPressure'} #type': 'zeroGradient', 'value': 'uniform 101325'
        if 'outlet' in key:
            f['boundaryField'][key] = {'type': 'fixedValue', 'value': 'uniform 101325'}
        if 'heat_in' in key:
            f['boundaryField'][key] = {'type': 'fixedFluxPressure'} #type': 'zeroGradient', 'value': 'uniform 101325'
    
    f.writeFile()
    
def setAlphat(path, region, patch_info):
    """Setup alphat file for fluid"""
   
    os.chdir(path+'/0/'+region)
    file = path+'/0/'+region+'/alphat'
    f = ParsedParameterFile(file)
    
    print('\nSetting alphat file..')
    
    switch = str(input('\nalphatJayatilleke (1) or alphat (2)? '))
    
    for key, value in patch_info.items():
        if 'adiabatic' in key:
            if '".*_adiabatic"' not in f['boundaryField']:
                if switch == '1':
                    f['boundaryField']['".*_adiabatic"'] = {'type': 'compressible::alphatJayatillekeWallFunction', 'value': 'uniform 0'}
                if switch == '2':
                    f['boundaryField']['".*_adiabatic"'] = {'type': 'compressible::alphatWallFunction', 'value': 'uniform 0'}
        if 'interface' in key:
            if '".*_interface"' not in f['boundaryField']:
                if switch == '1':
                    f['boundaryField']['".*_interface"'] = {'type': 'compressible::alphatJayatillekeWallFunction', 'value': 'uniform 0'}
                if switch == '2':
                    f['boundaryField']['".*_interface"'] = {'type': 'compressible::alphatWallFunction', 'value': 'uniform 0'}
        if 'symmetry' in key:
            if '".*_symmetry"' not in f['boundaryField']:
                f['boundaryField']['".*_symmetry"'] = {'type': 'symmetry'}
        if 'inlet' in key:
            f['boundaryField'][key] = {'type': 'calculated', 'value': 'uniform 0'}
        if 'outlet' in key:
            f['boundaryField'][key] = {'type': 'calculated', 'value': 'uniform 0'}
        if 'heat_in' in key:
            if switch == '1':
                f['boundaryField'][key] = {'type': 'compressible::alphatJayatillekeWallFunction', 'value': 'uniform 0'}
            if switch == '2':
                f['boundaryField'][key] = {'type': 'compressible::alphatWallFunction', 'value': 'uniform 0'}
    
    f.writeFile()
    
def setEpsilon(path, region, patch_info):
    """Setup epsilon file for fluid"""
   
    os.chdir(path+'/0/'+region)
    file = path+'/0/'+region+'/epsilon'
    f = ParsedParameterFile(file)
    
    print('\nSetting epsilon file..')
    
    switch = str(input('\nhighReNumber model (1) or lowReNumber model (2)? '))
    
    for key, value in patch_info.items():
        if 'adiabatic' in key:
            if '".*_adiabatic"' not in f['boundaryField']:
                if switch == '1':
                    f['boundaryField']['".*_adiabatic"'] = {'type': 'epsilonWallFunction', 'value': 'uniform 0.14'}
                if switch == '2':
                    f['boundaryField']['".*_adiabatic"'] = {'type': 'epsilonLowReWallFunction', 'value': 'uniform 0.14'}
        if 'interface' in key:
            if '".*_interface"' not in f['boundaryField']:
                if switch == '1':
                    f['boundaryField']['".*_interface"'] = {'type': 'epsilonWallFunction', 'value': 'uniform 0.14'}
                if switch == '2':
                    f['boundaryField']['".*_interface"'] = {'type': 'epsilonLowReWallFunction', 'value': 'uniform 0.14'}
        if 'symmetry' in key:
            if '".*_symmetry"' not in f['boundaryField']:
                f['boundaryField']['".*_symmetry"'] = {'type': 'symmetry'}
        if 'inlet' in key:
            f['boundaryField'][key] = {'type': 'fixedValue', 'value': 'uniform 0.14'}
        if 'outlet' in key:
            f['boundaryField'][key] = {'type': 'zeroGradient'}
        if 'heat_in' in key:
            if switch == '1':
                f['boundaryField'][key] = {'type': 'epsilonWallFunction', 'value': 'uniform 0.14'}
            if switch == '2':
                f['boundaryField'][key] = {'type': 'epsilonLowReWallFunction', 'value': 'uniform 0.14'}
    
    f.writeFile()
    
def setOmega(path, region, patch_info):
    """Setup epsilon file for fluid"""
   
    os.chdir(path+'/0/'+region)
    file = path+'/0/'+region+'/omega'
    f = ParsedParameterFile(file)
    
    print('\nSetting omega file..')
    
    for key, value in patch_info.items():
        if 'adiabatic' in key:
            if '".*_adiabatic"' not in f['boundaryField']:
                f['boundaryField']['".*_adiabatic"'] = {'type': 'omegaWallFunction', 'value': 'uniform 10'}
        if 'interface' in key:
            if '".*_interface"' not in f['boundaryField']:
                f['boundaryField']['".*_interface"'] = {'type': 'omegaWallFunction', 'value': 'uniform 10'}
        if 'symmetry' in key:
            if '".*_symmetry"' not in f['boundaryField']:
                f['boundaryField']['".*_symmetry"'] = {'type': 'symmetry'}
        if 'inlet' in key:
            f['boundaryField'][key] = {'type': 'fixedValue', 'value': 'uniform 10'}
        if 'outlet' in key:
            f['boundaryField'][key] = {'type': 'zeroGradient'}
        if 'heat_in' in key:
            f['boundaryField'][key] = {'type': 'omegaWallFunction', 'value': 'uniform 10'}
    
    f.writeFile()
    
def setK(path, region, patch_info):
    """Setup k file for fluid"""
   
    os.chdir(path+'/0/'+region)
    file = path+'/0/'+region+'/k'
    f = ParsedParameterFile(file)
    
    print('\nSetting k file..')
    
    switch = str(input('\nhighReNumber model (1) or lowReNumber model (2)? '))
    
    for key, value in patch_info.items():
        if 'adiabatic' in key:
            if '".*_adiabatic"' not in f['boundaryField']:
                if switch == '1':
                    f['boundaryField']['".*_adiabatic"'] = {'type': 'kqRWallFunction', 'value': 'uniform 0.01'}
                if switch == '2':
                    f['boundaryField']['".*_adiabatic"'] = {'type': 'kLowReWallFunction', 'value': 'uniform 0.01'}
        if 'interface' in key:
            if '".*_interface"' not in f['boundaryField']:
                if switch == '1':
                    f['boundaryField']['".*_interface"'] = {'type': 'kqRWallFunction', 'value': 'uniform 0.01'}
                if switch == '2':
                    f['boundaryField']['".*_interface"'] = {'type': 'kLowReWallFunction', 'value': 'uniform 0.01'}
        if 'symmetry' in key:
            if '".*_symmetry"' not in f['boundaryField']:
                f['boundaryField']['".*_symmetry"'] = {'type': 'symmetry'}
        if 'inlet' in key:
            f['boundaryField'][key] = {'type': 'fixedValue', 'value': 'uniform 0.01'}
        if 'outlet' in key:
            f['boundaryField'][key] = {'type': 'zeroGradient'}
        if 'heat_in' in key:
                if switch == '1':
                    f['boundaryField'][key] = {'type': 'kqRWallFunction', 'value': 'uniform 0.01'}
                if switch == '2':
                    f['boundaryField'][key] = {'type': 'kLowReWallFunction', 'value': 'uniform 0.01'}
    
    f.writeFile()
    
def setNut(path, region, patch_info):
    """Setup nut file for fluid"""
   
    os.chdir(path+'/0/'+region)
    file = path+'/0/'+region+'/nut'
    f = ParsedParameterFile(file)
    
    print('\nSetting nut file..')
    
    switch = str(input('\nhighReNumber model (1) or lowReNumber model (2)? '))
    
    for key, value in patch_info.items():
        if 'adiabatic' in key:
            if '".*_adiabatic"' not in f['boundaryField']:
                if switch == '1':
                    f['boundaryField']['".*_adiabatic"'] = {'type': 'nutkWallFunction', 'value': 'uniform 0'}
                if switch == '2':
                    f['boundaryField']['".*_adiabatic"'] = {'type': 'nutLowReWallFunction', 'value': 'uniform 0'}
        if 'interface' in key:
            if '".*_interface"' not in f['boundaryField']:
                if switch == '1':
                    f['boundaryField']['".*_interface"'] = {'type': 'nutkWallFunction', 'value': 'uniform 0'}
                if switch == '2':
                    f['boundaryField']['".*_interface"'] = {'type': 'nutLowReWallFunction', 'value': 'uniform 0'}
        if 'symmetry' in key:
            if '".*_symmetry"' not in f['boundaryField']:
                f['boundaryField']['".*_symmetry"'] = {'type': 'symmetry'}
        if 'inlet' in key:
            f['boundaryField'][key] = {'type': 'calculated', 'value': 'uniform 0'}
        if 'outlet' in key:
            f['boundaryField'][key] = {'type': 'calculated', 'value': 'uniform 0'}
        if 'heat_in' in key:
                if switch == '1':
                    f['boundaryField'][key] = {'type': 'nutkWallFunction', 'value': 'uniform 0'}
                if switch == '2':
                    f['boundaryField'][key] = {'type': 'nutLowReWallFunction', 'value': 'uniform 0'}
    
    f.writeFile()
                       
def set0Fluid(path, fluidRegions):
    """Setup 0 fluid files from templates"""
        
    filesFluid = ['alphat', 'epsilon', 'omega', 'k', 'nut', 'p', 'p_rgh', 'T', 'U']
    os.chdir(path)
    for region in fluidRegions:
        for file in filesFluid:
            subprocess.call(['cp', '-r', path+'/templates/'+file, path+'/0/'+region])            
            
    for region in fluidRegions:
       patchInfo = getPatchInfo(path, region)
       setPfluid(path, region, patchInfo)
       setTfluid(path, region, patchInfo)     
       setUfluid(path, region, patchInfo)
       setPrgh(path, region, patchInfo)
       setAlphat(path, region, patchInfo)
       setEpsilon(path, region, patchInfo)
       setOmega(path, region, patchInfo)
       setK(path, region, patchInfo)
       setNut(path, region, patchInfo)
            