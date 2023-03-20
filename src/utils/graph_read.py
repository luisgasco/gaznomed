"""
This module contains functions to load the Snomed-CT ontology as a multigraph, and recover
subtrees of the graph given a code.
"""
from tqdm import tqdm
import networkx as nx


def load_ontology(file_name_rel, root_concept_code="138875005", relation_types = ["116680003"]):
    """Function to load SnomecCT relationships from RF2 format to netowrkx model.
    Args:
        file_name_rel (str): Path to the SnomedCT Relationship file in RF2 format
        root_concept_code (str, optional): snomed code of the code from which you want to generate
                                           the ontology file (For example if we want the branch
                                           "Pharmaceutical / biologic product" we would use the code
                                           "373873005", if we want the whole snomed ontology we would
                                           use the code "138875005").Defaults to "138875005".
        relation_types (str, optional): Type of relationship to consider when building the ontology.
                                        Use string "116680003" if you only want to consider "Is a"
                                        relationships, use "all" if you want to consider all types
                                        of relationships (including concept model attributes).Defaults to "116680003".
    Returns:
        Networkx DiGraph: SnomedCT model in a NetworkxDigraph format.
    
    This code is based on the one written by @emreg00 (https://github.com/emreg00/toolbox/blob/master/parse_snomedct.py)
    """
    ontology = nx.MultiDiGraph()
    f = open(file_name_rel)
    header = f.readline().strip("\n")
    col_to_idx = dict((val.lower(), i) for i, val in enumerate(header.split("\t")))
    ontology.add_node("138875005")
    for line in f:
        words = line.strip("\n").split("\t")
        #if relation_types == "116680003": #"Is a" relationship code
        if (words[col_to_idx["typeid"]] in relation_types) & (words[col_to_idx["active"]] == "0"):
            source_id = words[col_to_idx["sourceid"]]
            target_id = words[col_to_idx["destinationid"]]
            try:
                ontology.remove_edge(target_id, source_id,key=words[col_to_idx["id"]])
            except:
                print("Removing an already removed relation id {}".format(words[col_to_idx["id"]]))
        elif (words[col_to_idx["typeid"]] in relation_types) & (words[col_to_idx["active"]] == "1"):
            source_id = words[col_to_idx["sourceid"]]
            target_id = words[col_to_idx["destinationid"]]
            ontology.add_node(source_id)
            ontology.add_edge(target_id, source_id,key=words[col_to_idx["id"]])

    return ontology



def subtree_sucessors_code_list(ontology, code):
    """
    Función en la que dado un código y un grafo de NetworkX, devuelve
    la lista de códigos del subarbol que cuelga del código dado. 
    
    Args:
    ontology ([networkx.MultiDigraph]): ontologías calculada
    code ([str]): Código del que se quiere obtener la lista de códigos de su subarbol
    
    Nota: También incluye el código de la entrada (code)
    """
    # Get sucesores
    resultado_dict = nx.dfs_successors(ontology, source=code)
    # Cogemos la lista de listas de conceptos 
    lista_smallest_edges = [resultado_dict[i] for i in resultado_dict]
    lista_smallest_edges_flatten = [item for sublist in lista_smallest_edges for item in sublist]
    # Lista de hijos directos
    lista_nodes = list(resultado_dict.keys())
    # Unimos todo
    lista_end = lista_smallest_edges_flatten + lista_nodes
    # Devolmenos una lista de elementos únicos
    return list(set(lista_end))


def get_sucessors_from_list(g, list_codes):
    """_summary_

    Args:
        graph  ([networkx.MultiDigraph]): ontologías calculada
        list_codes (list): List of the codes from which the user wishes to obtain their subtrees

    Returns:
        list of codes
    """
    lista_codigos_subtree = list()
    list_codes = [str(code) for code in list_codes]
    for subtree in list_codes:
        lista_codigos_subtree.append(subtree_sucessors_code_list(g, subtree))
    # Hacemos set y pasamos valores a int
    lista_codigos_subtree_flatten = [int(i) for i in list(set([i for sublist in lista_codigos_subtree for i in sublist]))]
    return lista_codigos_subtree_flatten