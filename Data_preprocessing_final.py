# -*- coding: utf-8 -*-
"""
Created on Sat Sep 25 13:08:09 2021
@author: mehdi G

"""

import numpy as np
import json

import pandas as pd

WS = pd.read_excel("data/1. Network Data/3. UTA Runcut File  Aug2016.xlsx")
UTA_Runcut_File = np.array(WS)

rM = pd.read_excel("data/routeMileage.xlsx") # Importing the mileage of each root
rM = np.array(rM)

#Using the following function the BEB list, bus mileage, bus charging seq. and, Charging station indexes are extrated based on each plan:
    
def import_data (filename):
    """
    This function, imports the train/test data and create the attribute matrix and labels using the input data
    """
    data = []
    with open(filename) as f:
        for line in f:
            sample = line.split()
            data.append([sample[0], (sample[1])])
        data.pop(0)
        
    "Extract the BEB indexes based on the plans"
    plan_BEBs = []
    for i in data:
        k1 = i[0]
        
        
        if (str(k1[0]) == 'Z'):
            k2 = int(k1[1:])
            plan_BEBs.append([k2, int(i[1])])
    
    BEB_list = []
    for j in plan_BEBs:
        if (j[1]==1):
            BEB_list.append(j[0])
            
    Dist_mil = []
    for i in data:
        k1 = i[0]
        if (str(k1[0]) == 'm'):
            k2 = k1[1:]
            k3 = k2.split('_')
            Dist_mil.append([int(k3[0]), int(k3[1]), float(i[1])])
         
    bus_ix, nbs = np.unique (np.asarray(Dist_mil)[:,0], return_counts=True)
    
    Dist_mil = np.asarray(Dist_mil)
    
    bus_milage = {}
    
    for i in range(len(bus_ix)):
        dict1 = {}
        for j in range (nbs[i]):      
            y1 = Dist_mil[np.logical_and(Dist_mil[:,0] == int(bus_ix[i]) , Dist_mil[:,1] == int(j))][-1][-1]
            dict1[j] = y1     
        bus_milage[int(bus_ix[i])] = dict1
    
    Charge_seq = []
    for i in data:
        k1 = i[0]
        if (str(k1[0]) == 'X'):
            k2 = k1[1:]
            k3 = k2.split('_')
            Charge_seq.append([int(k3[0]), int(k3[1]), float(i[1])])
         
    bus_ix, nbs = np.unique (np.asarray(Charge_seq)[:,0], return_counts=True)
    
    Charge_seq = np.asarray(Charge_seq)
    
    bus_charge_seq = {}
    
    for i in range(len(bus_ix)):
        dict1 = {}
        for j in range (nbs[i]):      
            y1 = Charge_seq[np.logical_and(Charge_seq[:,0] == int(bus_ix[i]) , Charge_seq[:,1] == int(j))][-1][-1]
            dict1[j] = y1     
        bus_charge_seq[int(bus_ix[i])] = dict1
    
    Charging_stations = []
    for i in data:
        k1 = i[0]
        if (str(k1[0]) == 'Y'):
            k2 = k1[1:]
            Charging_stations.append([int(k2), int(i[1])])
         
    Charging_stations = np.asarray(Charging_stations)
    
    
    Charging_stations_ix = Charging_stations[Charging_stations[:,1] == 1][:,0]
    
    return BEB_list, bus_milage, bus_charge_seq, Charging_stations_ix



#This function extracts the beb routes based on the beb lists (for each plan) that are extracted from last part


def extract_BEB_routes (BEB_list):  
    BEB_Route = np.empty((0,9))
    for bus in BEB_list:
        BEB_Route1 = UTA_Runcut_File[(UTA_Runcut_File[:,3] == bus)]
        z_route=[]
        for i in BEB_Route1:
            z_route.append([i[0], i[1], i[2], i[3], i[4], i[5], i[6].hour+i[6].minute/60.0, i[7], i[8].hour+i[8].minute/60.0])
        
        BEB_Route = np.append(BEB_Route, np.asarray(z_route), axis = 0)
        
    Routes_ix, nbs_r = np.unique (BEB_Route[:,0], return_counts=True)
    return BEB_Route




t_interval = np.arange(0, 24.2, 0.25)


#This function generates a dictionary based on the variables extrated in last part and the output is used in the visualization

def extract_final_dic (BEB_list, root_mileage, bus_milage, bus_charge_seq, runcut_file):
    dic1 = {}
    for bus in BEB_list:
     

        BEB_Route1 = runcut_file[(runcut_file[:,3] == bus)]
        z_route=[]
        for i in BEB_Route1:
            z_route.append([i[0], i[1], i[2], i[3], i[4], i[5], float(i[6].hour+i[6].minute/60.0), i[7], float(i[8].hour+i[8].minute/60.0)])
        z_route = np.asarray(z_route)
        
        
        if bus in bus_charge_seq.keys():
            pass
        else:
            u1 = {}
            for i in range (z_route.shape[0]):
                                    
                Route_length = float(root_mileage[(root_mileage[:,0] == float(z_route[i][0]))][0][1])
                if i < 1 :
                    u1[i] = 0
                    u1[i+1] = Route_length
                else:
                    u1[i+1] = Route_length + u1[i]
                    
            bus_milage[bus] = u1
     
     
        dic2 = {}
        for t in t_interval:
            y = {}
            if t <= float(z_route[0][6]):
                SoC = 100
                Mil = 0
                Route = z_route[0,0]
                Location = z_route[0,5]
                Distance_from_last_station = 0
                Route_length = float(root_mileage[(root_mileage[:,0] == float(z_route[0][0]))][0][1])
                
                route_percentage = Distance_from_last_station * 100 / (Route_length)
                
                if bus in bus_charge_seq.keys():
                    Charging_status = bus_charge_seq[bus][0]
                else:
                    Charging_status = 0.0
                
                y = {"SoC":SoC, "Mileage": Mil, "Route_number": Route, "Location": Location,
                     "Distance_from_last_station":Distance_from_last_station, "Route_length":Route_length,
                     "route_percentage":route_percentage, "Charging_status": Charging_status}
            
            else:
                if t >= float(z_route[z_route.shape[0]-1][8]):
                    
    
                    Mil = bus_milage[bus][z_route.shape[0]]
                    SoC = 100 - (100*Mil/62)
                    Route = z_route[z_route.shape[0]-1,0]
                    Location = z_route[z_route.shape[0]-1,5]
                    Distance_from_last_station = 0
                    
                    Route_length = float(root_mileage[(root_mileage[:,0] == float(z_route[z_route.shape[0]-1][0]))][0][1])
                    route_percentage = Distance_from_last_station * 100 / (Route_length) 
                    if bus in bus_charge_seq.keys():
                        
                        Charging_status = bus_charge_seq[bus][z_route.shape[0]]
                    else:
                        Charging_status = 0.0
                    
                    y = {"SoC":SoC, "Mileage": Mil, "Route_number": Route, "Location": Location,
                         "Distance_from_last_station":Distance_from_last_station, "Route_length":Route_length,
                         "route_percentage":route_percentage, "Charging_status": Charging_status}
                    
                elif (t >= float(z_route[z_route.shape[0]-1][6]) and t <= float(z_route[z_route.shape[0]-1][8])):
                        tp = (t - float(z_route[z_route.shape[0]-1][6]))/(float(z_route[z_route.shape[0]-1][8]) - float(z_route[z_route.shape[0]-1][6])) # the time percentage between the bus stations
                        
                        Route_length = float(root_mileage[(root_mileage[:,0] == float(z_route[z_route.shape[0]-1][0]))][0][1])
                        
                        
                        Mil = bus_milage[bus][z_route.shape[0]-1] + tp * (Route_length)
                        SoC = 100 - (100*Mil/62)
                        Route = z_route[z_route.shape[0]-1][0]
                        Location = "On Route"
                        Distance_from_last_station = tp * (Route_length)
                        
                        route_percentage = Distance_from_last_station * 100 / (Route_length) 
                        Charging_status = 0
                        
                        y = {"SoC":SoC, "Mileage": Mil, "Route_number": Route, "Location": Location,
                             "Distance_from_last_station":Distance_from_last_station, "Route_length":Route_length,
                             "route_percentage":route_percentage, "Charging_status": Charging_status}
                    
                else:
                    for i in range (z_route.shape[0]-1):
                        
                        if (t >= float(z_route[i][8]) and t < float( z_route[i+1][6]) ):
                            
                            Mil = bus_milage[bus][i+1]
                            SoC = 100 - (100*Mil/62)
                            Route = z_route[i+1,0]
                            Location = z_route[i+1,5]
                            Distance_from_last_station = 0
                            
                            Route_length = float(root_mileage[(root_mileage[:,0] == float(z_route[i+1][0]))][0][1])
                            
                            route_percentage = Distance_from_last_station * 100 / (Route_length)
                            
                            if bus in bus_charge_seq.keys():
                        
                                Charging_status = bus_charge_seq[bus][i+1]
                            else:
                                Charging_status = 0.0
                            
                            
                            y = {"SoC":SoC, "Mileage": Mil, "Route_number": Route, "Location": Location,
                                 "Distance_from_last_station":Distance_from_last_station, "Route_length":Route_length,
                                 "route_percentage":route_percentage, "Charging_status": Charging_status}
                            
                        elif (t < float(z_route[i][8]) and t >= float(z_route[i][6])):
                            tp = (t - float(z_route[i][6]))/(float(z_route[i][8]) - float(z_route[i][6])) # the time percentage between the bus stations
                            
                            Route_length = float(root_mileage[(root_mileage[:,0] == float(z_route[i][0]))][0][1])
                            
                            
                            Mil = bus_milage[bus][i] + tp * (Route_length)
                            SoC = 100 - (100*Mil/62)
                            Route = z_route[i,0]
                            Location = "On Route"
                            Distance_from_last_station = tp * (Route_length)
                            
                            route_percentage = Distance_from_last_station * 100 / (Route_length) 
                            Charging_status = 0
                            
                            y = {"SoC":SoC, "Mileage": Mil, "Route_number": Route, "Location": Location,
                                 "Distance_from_last_station":Distance_from_last_station, "Route_length":Route_length,
                                 "route_percentage":route_percentage, "Charging_status": Charging_status}
                        
                        
                                  
            if (y=={}):
                print("warning, empty dictionary in t= ", t, "BEB=", bus)
            
            dic2[t] = y
            
            
        dic1[bus] = dic2
    return dic1
                
                
filename20 = 'data/2. Deployment Plans/1. Solutions/p20.txt'
BEB_list_p20, bus_milage_p20_, bus_charge_seq_p20_, Charging_stations_ix_p20 = import_data(filename20)
bus_milage_p20 = { beb: bus_milage_p20_[beb] for beb in BEB_list_p20 }
bus_charge_seq_p20 = { beb: bus_charge_seq_p20_[beb] for beb in BEB_list_p20 }
BEB_Route_p20 = extract_BEB_routes (BEB_list_p20)                
dic1 = extract_final_dic (BEB_list_p20, rM, bus_milage_p20, bus_charge_seq_p20, UTA_Runcut_File)

filename60 = 'data/2. Deployment Plans/1. Solutions/p60.txt'
BEB_list_p60, bus_milage_p60, bus_charge_seq_p60, Charging_stations_ix_p60 = import_data(filename60)
BEB_Route_p60 = extract_BEB_routes (BEB_list_p60)
dic2 = extract_final_dic (BEB_list_p60, rM, bus_milage_p60, bus_charge_seq_p60, UTA_Runcut_File)

filename180 = 'data/2. Deployment Plans/1. Solutions/p180.txt'
BEB_list_p180, bus_milage_p180, bus_charge_seq_p180, Charging_stations_ix_p180 = import_data(filename180)
BEB_Route_p180 = extract_BEB_routes (BEB_list_p180)
dic3 = extract_final_dic (BEB_list_p180, rM, bus_milage_p180, bus_charge_seq_p180, UTA_Runcut_File)

Plans = ["Plan1", "Plan2","Plan3"]
final_data = {Plans[0]: dic1, Plans[1]: dic2, Plans[2]: dic3}
final_data = json.dumps(final_data)  
jsonFile = open("dataset/final_data.json", "w")
jsonFile.write(final_data)
jsonFile.close()


# Ectracting charging station occupncy

t_interval = np.arange(0, 24.2, 0.125)
def extract_cs_dic (BEB_list, Charging_stations_list, bus_milage, bus_charge_seq, runcut_file):
    m=1
    dic1 = {}
    y1 = []
    for bus in BEB_list:
        BEB_Route1 = runcut_file[(runcut_file[:,3] == bus)]
        z_route=[]
        for i in BEB_Route1:
            z_route.append([i[0], i[1], i[2], i[3], i[4], i[5], float(i[6].hour+i[6].minute/60.0), i[7], float(i[8].hour+i[8].minute/60.0)])
        z_route = np.asarray(z_route)
        dic2 = {}        
        sq_i = 0
              
        for t in t_interval:        
            y = {}
            if t <= float(z_route[0][6]):
                y = {"chargin_status":"Free"}
            else:
                if t >= float(z_route[z_route.shape[0]-1][8]):                 
                    y = {"chargin_status":"Free"}
                else:
                    for i in range (z_route.shape[0]-1):
                                              
                        if (t >= float(z_route[i][8]) and t < float( z_route[i+1][6]) ):
                            
                            
                            if bus in bus_charge_seq.keys():
                        
                                Charging_status = bus_charge_seq[bus][i+1]
                            else:
                                Charging_status = 0.0
                                
                                

                            if Charging_status == 1.0 :       
                                charging_station = z_route[i+1][5]
                                seq = i+5
                                if  sq_i != seq:
                                    sq_i = seq         
                                    Mil = bus_milage[bus][i]
                                    energy = 400 - 400*Mil/62                                    
                                    y3 = [float(t), bus, seq, charging_station, energy]
                                                                        
                                    y1.append(y3)
                                    m = m+1
                                                                                                   
                                    y = {"chargin_status":"In-use",  "Bus":bus, "seq":seq, "charging_station": charging_station, "energy": energy}
                                else:
                                    y = {"chargin_status":"Free"}
                        elif (t < float(z_route[i][8]) and t >= float(z_route[i][6])):
                            y = {"chargin_status":"Free"}
                        
                        elif (t >= float(z_route[z_route.shape[0]-1][6]) and t <= float(z_route[z_route.shape[0]-1][8])):
                            y = {"chargin_status":"Free"}                                             
            dic2[t] = y    
        dic1[bus] = dic2        
    y2 = np.asarray(y1)    
    for i in range (y2.shape[0]):
        y2[i][0] = float(y2[i][0])
        y2[i][4] = round(float(y2[i][4]), 2)   
    cs_list = np.unique((y2[:,3]))
    cs1 = {}
    for cs in cs_list:
        d1 = y2[y2[:,3]==cs,:]
        d1 = d1[np.argsort(d1[:,0].astype(float))]
        d1 = np.delete(d1, 3, 1)
        d1 = d1.astype(float)
        energy = 0
        cs2 = {}
        for t in t_interval:
            z1 = d1[d1[:,0].astype(float)==t,:]
            if z1.shape[0] ==1:
                status = "In Use"
                bus = z1[0][1]
                seq = z1[0][2]
                energy += z1[0][3]
            else:
                status = "Free"
                bus = "no bus"
                seq ="no seq"
            
            cs2[t] = {"chargin_status":status,  "Bus":bus, "seq":seq, "energy": energy}
        cs1[cs] = cs2   
    return cs1


stop_list = pd.read_excel("data/2. Deployment Plans/2. UTA_Runcut_Potential_Stop.xlsx")
stop_list = np.array(stop_list)
stop_list[:,0] = stop_list[:,0].astype(int)


def find_list(cs_list, cs_ix):
    cs_l=[]
    for i in cs_ix:
        z = cs_list[cs_list[:,0] == i, :]
        
        cs_l.append(z[0])
    cs_l = np.asarray(cs_l)
    return (cs_l)



    
        

Charging_stations_list_p20 = find_list(stop_list, Charging_stations_ix_p20)
Charging_stations_list_p60 = find_list(stop_list, Charging_stations_ix_p60)



        
Charging_stations_list_p180 = find_list(stop_list, Charging_stations_ix_p180)
cs_p20 = extract_cs_dic (BEB_list_p20, Charging_stations_list_p20, bus_milage_p20, bus_charge_seq_p20, UTA_Runcut_File)
cs_p60 = extract_cs_dic (BEB_list_p60, Charging_stations_list_p60, bus_milage_p60, bus_charge_seq_p60, UTA_Runcut_File)
cs_p180 = extract_cs_dic (BEB_list_p180, Charging_stations_list_p180, bus_milage_p180, bus_charge_seq_p180, UTA_Runcut_File)
final_cs = {Plans[0]: cs_p20, Plans[1]: cs_p60, Plans[2]: cs_p180}

final_cs = json.dumps(final_cs)  
jsonFile = open("dataset/final_cs.json", "w")
jsonFile.write(final_cs)
jsonFile.close()


#%%
# Extracting non-charging stations:
def non_cs_list(cs_dic, BEB_Route):
    cs_list = cs_dic.keys()
    
    cs_list = [str(key) for key in cs_list]
    cs_list = np.array(cs_list)
    print((cs_list.shape))
    
    all_stations_list = np.unique([BEB_Route[:,5], BEB_Route[:,7]])
    
    
    print(all_stations_list.shape)
    non_cs_l = [i for i in all_stations_list if i not in cs_list]
    
    
    return non_cs_l


non_cs_list_p20 = non_cs_list(cs_p20, BEB_Route_p20)
    
non_cs_list_p60 = non_cs_list(cs_p60, BEB_Route_p60)

non_cs_list_p180 = non_cs_list(cs_p180, BEB_Route_p180)


non_cs_data = {Plans[0]: non_cs_list_p20, Plans[1]: non_cs_list_p60, Plans[2]: non_cs_list_p180}
non_cs_data = json.dumps(non_cs_data)  
jsonFile = open("dataset/non_cs_data.json", "w")
jsonFile.write(non_cs_data)
jsonFile.close()

    
    
