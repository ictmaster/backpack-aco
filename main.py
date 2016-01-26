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

        con = sqlite3.connect(db_name)
        c = con.cursor()
        print("roulette...")
        c.execute("""
        SELECT id
        FROM edges
        WHERE from_node = ?
        LIMIT 1;
        """,(self.id,))
        edge_id = c.fetchone()[0]
        con.close()
        return edge_id

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
    for i,node in enumerate(nodes[:]):
        coords = (node.lat, node.lon)
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
    print("Generating edges for",len(nodes),"nodes...")
    con = sqlite3.connect(db_name)
    c = con.cursor()
    for i,a in enumerate(nodes):
        for j,b in enumerate(nodes):
            if a != b:
                c.execute('insert into edges (from_node, to_node, cost, pheromones) values (?, ?, ?, ?)', (i, j, str(calculate_distance(a, b)), 1))
        con.commit()
        print('Committed edges from',i,'to db...')
    con.commit()
    con.close()

class ANT:
    def __init__(self):
        self.visited_edges = []

    def check_if_done(self):
        """con = sqlite3.connect(db_name)
        c = con.cursor()
        c.execute("select * from edges where id=?", (self.visited_edges[-1]))
        print (c.fetchone())
        con.commit()
        con.close()"""
        return len(self.visited_edges) > 10


    def walk(self, start_node):
        print("Ant starting his walk...")
        current_node = start_node
        current_edge_id = None
        while not self.check_if_done():
            current_edge_id = current_node.roulette_wheel(self.visited_edges, start_node)
            edge = db.get_edge_by_id(current_edge_id)
            current_node = nodes[int(edge[2])]
            self.visited_edges.append(current_edge_id)
        print(self.visited_edges)

    # TODO: update pheromones to work with database
    def pheromones(self):
        currentCost = getSum(self.visitedEdges)
        if(currentCose < MAXCOST):
            score = 1000**(1-float(currentCost)/MAXCOST)
            for edge in self.visitedEdges:
                edge.pheromones += score


if __name__ == '__main__':
    start_main = time.time()
    print("Started execution...")
    city_file = 'worldcitiespop.txt'

    nodes = get_cities(city_file)
    #generate_edges(nodes)
    ant = ANT()
    ant.walk(nodes[0])



    print("Main script executed in " + "{0:.2f}".format(time.time() - start_main) + ' seconds...')
