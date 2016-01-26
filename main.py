#!/usr/bin/python3
import random
import sys
import time
import debug
import json
import math
import sqlite3
from db import db_name
import db

class Node:
    def __init__(self, data_dict):
        self.data = data_dict
        self.country     = data_dict['Country']
        self.city        = data_dict['City']
        self.accent_city = data_dict['AccentCity']
        self.region      = data_dict['Region']
        self.population  = data_dict['Population']
        self.lat         = data_dict['Latitude']
        self.lon         = data_dict['Longitude']
        self.id          = -1
        self.edges       = []

    def __repr__(self):
        return self.data['City']

    def roulette_wheel(self, visited_edges, start_node):
        # TODO: REMOVE
        return random.sample(self.edges,1)[0]

        visited_nodes = [edge.to_node for edge in visited_edges]
        viable_edges = [edge for edge in self.edges if not edge.to_node in visited_nodes and edge.to_node != start_node]

        if not viable_edges:
            viable_edges = [edge for edge in self.edges]

        all_pheromones = sum([edge.pheromones for edge in viable_edges])
        num = random.uniform(0,all_pheromones)
        s = 0
        i = 0
        selected_edge = viable_edges[i]
        while(s<=num):
            selected_edge = viable_edges[i]
            s += selected_edge.pheromones
            i += 1
        return selected_edge

    def get_dict(self):
        return self.data

class Edge:
    def __init__(self, from_node, to_node, cost):
        self.from_node = from_node
        self.to_node = to_node
        self.cost = cost
        self.pheromones = 1

    def __repr__(self):
        return str(self.from_node) + " >--[" + str(self.cost) + "]--> " + str(self.to_node)

def get_cities(filename):
    print("Fetching cities from file...")
    nodes = []
    with open(filename, 'r', encoding='latin-1') as f:
        keys = f.readline().strip().split(',')
        for line in f.readlines():
            node = {}
            line = line.strip().split(',')
            if 'no' != line[0]:
                continue
            for i,key in enumerate(keys):
                node[key] = line[i]
            #if node not in nodes:
            nodes.append(Node(node))
    print("Fetched nodes, attempting to find duplicates...")
    unique_nodes = []
    new_coords   = []
    new_names    = []
    for i,node in enumerate(nodes):
        coords = (node.lat, node.lon)
        name = node.city
        if coords not in new_coords:
            unique_nodes.append(node)
            new_coords.append(coords)

    print("Removed",len(nodes)-len(unique_nodes),"duplicates...")
    for i, node in enumerate(unique_nodes):
        node.id = i
    return unique_nodes

def calculate_distance(node1, node2):
    lat1, lat2 = float(node1.lat), float(node2.lat)
    lon1, lon2 = float(node1.lon), float(node2.lon)

    rad      = 6371000
    phi1     = math.radians(lat1)
    phi2     = math.radians(lat2)
    d_phi    = math.radians(lat2-lat1)
    d_lambda = math.radians(lon2-lon1)

    a = (math.sin(d_phi / 2) ** 2) + (math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda) ** 2)
    c = 2*math.atan2(math.sqrt(a), math.sqrt(1-a))

    return rad * c

def generate_edges(nodes):
    print("Generating edges for",len(nodes),"nodes... ("+str(len(nodes)**2-len(nodes))+")")
    edges = []
    for i,a in enumerate(nodes):
        for j,b in enumerate(nodes):
            if i != j:
                edges.append(Edge(a, b, calculate_distance(a,b)))
    return edges

def get_sum(edges):
    return sum(e.cost for e in edges)

class ANT:
    def __init__(self):
        self.visited_edges = []

    def check_if_done(self, end_node):
        try:
            arrived = self.visited_edges[-1].to_node == end_node
        except IndexError:
            arrived = False
        return len(self.visited_edges) >= 10 and arrived


    def walk(self, start_node, end_node):
        current_node = start_node
        current_edge = None
        while not self.check_if_done(end_node):
            current_edge = current_node.roulette_wheel(self.visited_edges, start_node)
            current_node = current_edge.to_node
            self.visited_edges.append(current_edge)

    def pheromones(self):
        current_cost = get_sum(self.visited_edges)
        if(current_cost < MAXCOST):
            score = 1000**(1-float(current_cost)/MAXCOST)
            for edge in self.visited_edges:
                edge.pheromones += score

    def gps_stuff(self):
        gps_nodes = [edge.to_node for edge in self.visited_edges]
        gps_nodes.insert(0,self.visited_edges[0].from_node)
        for node in gps_nodes:
            print(node.city+','+node.country+','+node.lat+','+node.lon)

if __name__ == '__main__':
    start_main = time.time()
    print("Started execution...")
    city_file = 'worldcitiespop.txt'

    # Fetching nodes
    nodes = get_cities(city_file)
    random.shuffle(nodes)
    # Not using all cities cause slow
    nodes = nodes[:100]


    print("Generating edges...")
    edges = generate_edges(nodes)

    print("Assigning edges to nodes...")
    for edge in edges:
        for node in nodes:
            if(edge.from_node==node):
                node.edges.append(edge)

    print("Calculating MAXCOST...")
    MAXCOST = get_sum(edges)


    fastest_ant = (-1, -1, -1)
    slowest_ant = (-1, -1, -1)

    START_POINT = nodes[0]
    END_POINT = nodes[23]
    print("Starting the walking...")
    done_ants = []
    for i in range(1000000):
        ant = ANT()
        ant.walk(START_POINT, END_POINT)
        ant.pheromones()
        ant_cost = get_sum(ant.visited_edges)
        if(ant_cost < fastest_ant[1] or fastest_ant[1] == -1):
            fastest_ant = (i, ant_cost, len(ant.visited_edges))
            print("NEW FAST RECORD:",ant_cost, ", VISITED:",len(ant.visited_edges),", ANT NUMBER:",i)

        if(ant_cost > slowest_ant[1] or slowest_ant[1] == -1):
            slowest_ant = (i, ant_cost, len(ant.visited_edges))
            print("NEW SLOW RECORD:",ant_cost, ", VISITED:",len(ant.visited_edges),", ANT NUMBER:",i)
        done_ants.append(ant)

        # print (i, get_sum(ant.visited_edges))
    print("STARTING AT:",START_POINT)
    print("ENDING AT  :",END_POINT)
    print("The fastest ant was ant",fastest_ant[0],"with cost of",fastest_ant[1], "he visited",fastest_ant[2],"edges...")
    print("The slowest ant was ant",slowest_ant[0],"with cost of",slowest_ant[1], "he visited",slowest_ant[2],"edges...")

    done_ants[fastest_ant[0]].gps_stuff()

    ant = ANT()
    ant.walk(START_POINT, END_POINT)
    #for edge in ant.visited_edges:
        #pass#print(edge,edge.pheromones)

    print("Main script executed in " + "{0:.2f}".format(time.time() - start_main) + ' seconds...')
