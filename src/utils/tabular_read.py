from tqdm import tqdm
import sys, os, re
import pandas as pd
import numpy as np
import operator

general_path = os.getcwd().split("gaznomed")[0]+"gaznomed/"
sys.path.append(general_path+'src')
from utils.constants import SCT_TAGS_SPANISH, SCT_TAGS_ENGLISH, SCT_TAG_ES2EN, ADDITIONAL_EN_SCT, ADDITIONAL_ES_SCT


def active_terms_from_conceptRF2_file(concept_path):
    """
    Function to load a dataframe of concepts from the concept RF2 file. 
    This function only loads active terms present in that file
    This file can be both in english and spanish.
    Args:
        concept_path (str): Path to the snomed-ct concept rf2 file

    Returns:
        pd.DataFrame: Dataframe with 6 columns: effectiveTime, active, conceptId, languageCode, typeId, term
    """
    file = open(concept_path, 'r')
    lines = file.readlines()
    concept_dicts = dict()
    for index in tqdm(range(0, len(lines))):
        if index == 0:
            continue
        else:  
            elementos = lines[index].split("\t")
            # si el código está dentro del diccionario, añadimos.
            if elementos[4] in concept_dicts.keys():
                # Si typeId es main term (900000000000003001) añadimos la entrada, pero quitamos ese mainterm al resto de elementos de la lista. 
                if elementos[6] == "900000000000003001":
                    # Buscamos que elemento de la lista tiene en el campo main term 
                    lista_tuplas = concept_dicts[elementos[4]]

                    # Actualizamos ese elemento
                    nueva_lista_tuplas = []
                    for tupla in lista_tuplas:
                        # Si el elemento guardado anteriormente tiene es FSN (ese codigo)
                        if tupla[4] == "900000000000003001":
                            # Lo guardo con el codigo sinonimo
                            nueva_tupla = (tupla[0], tupla[1], tupla[2], tupla[3], "900000000000013009", tupla[5])
                        else:
                            # Si no lo dejo igual
                            nueva_tupla = tupla
                        # La añado
                        nueva_lista_tuplas.append(nueva_tupla)
                    # Añado a la lista el nuevo elemento
                    nueva_lista_tuplas_end = nueva_lista_tuplas+[(elementos[1],elementos[2],elementos[4],elementos[5],elementos[6],elementos[7])]
                    # Guardamos en el diccionario
                    concept_dicts[elementos[4]] = nueva_lista_tuplas_end# .append((elementos[1],elementos[2],elementos[4],elementos[5],elementos[6],elementos[7]))
                # Si no exoste se guarda dentro de la lista
                else: 
                    concept_dicts[elementos[4]].append((elementos[1],elementos[2],elementos[4],elementos[5],elementos[6],elementos[7]))
            else: # Si el código no está dentro.
                # Se añade los datos de interés 
                concept_dicts[elementos[4]] = [(elementos[1],elementos[2],elementos[4],elementos[5],elementos[6],elementos[7])] 
    # Convertimos el diccionario en una lista de tuplas
    lista_tuplas = [(v[0],v[1],v[2],v[3],v[4],v[5]) for k in concept_dicts.keys() for v in concept_dicts[k]]
    # Creamos el dataframe a partir de la lista de tuplas
    df = pd.DataFrame(lista_tuplas, columns=["effectiveTime","active","conceptId","languageCode","typeId","term"])
    return df


def get_snomed_semantic_class(sct_mention, language):
    """ Function to extract the semantic class of a mention. The semantic class is the text
    contained between brackects at the end of a string

    Args:
        sct_mention ([str]): Snomed-CT mention
        language ([str]): Language of Snomed-CT mention
        
    Returns:
      output (str): Semantic class string
    """
    # If there is semantic class, the last element of the string will be a close bracket (")")
    if sct_mention[-1] ==")": #There are semantic class
        try:
            # Take the string between parenthesis.
            candidate_sem_tag = re.sub("[()]", "", re.findall('\(.*?\)',sct_mention)[-1])
            # Depending on language, take a different list of valid semantic_tags
            if "es" in language: #Spanish snomed-ct
                # If candidate_sem_Tag is in the list of valid semantic tags, take always de english verison.
                if candidate_sem_tag in SCT_TAGS_SPANISH+ADDITIONAL_ES_SCT:
                            output = SCT_TAG_ES2EN[candidate_sem_tag] # Take always english version
                else:
                    output = None
            elif "en" in language:
                # If candidate_sem_Tag is in the list of valid semantic tags, take always de english verison.
                if candidate_sem_tag in SCT_TAGS_ENGLISH+ADDITIONAL_EN_SCT:
                            output = candidate_sem_tag 
                else:
                    output = None
        except:
            output = None
    else:
        output = None
    return output


def snomed_remove_semantictag(sct_mention):
    """ Function to extract the semantic class of a mention. The semantic class is the text
    contained between brackects at the end of a string

    Args:
        sct_mention ([str]): Snomed-CT mention
        language ([str]): Language of Snomed-CT mention
        
    Returns:
      output (str): 
    """
    # If there is semantic class, the last element of the string will be a close bracket (")")
    if sct_mention[-1] ==")": #There are semantic class
        try:
            # Take the mention and remove the last paranthesis information (that yusually is the semantic tag)
            candidate_sem_tag = re.findall('\(.*?\)',sct_mention)[-1]
            valid_sct_sem_tags = SCT_TAGS_SPANISH+ADDITIONAL_ES_SCT+SCT_TAGS_ENGLISH+ADDITIONAL_EN_SCT
            # If candidate semantic tags is in the valid list of semantic tags, remove it. 
            # We remove the parenthesis to search in the list
            if re.sub("[()]", "", candidate_sem_tag) in valid_sct_sem_tags:
                output = sct_mention.replace(candidate_sem_tag,"").strip()
            else:
                output = sct_mention
        except:
            output = sct_mention
    else:
        output = sct_mention
    
    return output


def prepare_concept_df(df, language):
    """
    This functions transform concept dataframe to a more readable format.
    It extract semantic classes from concepto descriptors, remove duplicates, etc
    """
    # Extract semantic tags from descriptors
    df["semantic_tag"] = df.term.apply(lambda x: get_snomed_semantic_class(x,language))
    # Identify which terms are fully specified names
    df["mainterm"] = df.typeId.apply(lambda x: 1 if x=="900000000000003001" else 0)
    # Remove semantic tags from texts
    df["mention"] = df.term.apply(lambda x: snomed_remove_semantictag(x))
    # Ordenamos por conceptId, este paso no es necesario al 100%
    df = df.sort_values(by=["conceptId","mainterm"], ascending=False).reset_index(drop=True)
    # Genero diccionario con los valores únicos de codigos y sus semantic_tag:
    mapping_dict = dict(df[df.typeId=="900000000000003001"].loc[df['semantic_tag'].notnull(), ['conceptId', 'semantic_tag']].values)
    # mapeo los valores nones de semantic_tag con los valores del diccionario
    df['semantic_tag2'] = df['semantic_tag'].fillna(df['conceptId'].map(mapping_dict))
    # Only select columns we are interested in
    sct_df = df[["conceptId","languageCode","mention","semantic_tag2","mainterm"]].copy()
    # Remove last None values (that are obsolete terms)
    sct_df = sct_df[sct_df.semantic_tag2.notnull()].sort_values(by=["mention","mainterm"], ascending=False).reset_index(drop=True)
    # Create a new dict of code:semantic_tag of the mainterms to ensure we have the same semantic_tag for each code.
    dict_sem_tags = dict(zip(sct_df.loc[sct_df['mainterm'] == 1].conceptId, sct_df.loc[sct_df['mainterm'] == 1].semantic_tag2))
    sct_df['semantic_tag2'] = sct_df['conceptId'].map(dict_sem_tags)
    # Remove duplicates
    sct_df = sct_df.drop_duplicates(subset=["mention","conceptId","semantic_tag2","mainterm"]).reset_index(drop=True)
    # Prepare output
    sct_df.columns = ["code","language","term","semantic_tag","mainterm"]
    sct_df["code"] = sct_df.code.astype(int)
    return sct_df


def get_active_relations(path_relations_file):
    """
    Leemos el archivo de relaciones de  snomed línea por línea, borrando aquellas relaciones
    no activas. Posteriormente eliminamos del diccionario resultante las claves (sct codes)
    que hay que borrar por pertenecer a conceptos inactivos. Por último, iteramos para conseguir
    la forma final del diccionario  "CODIGO" --> "Lista de codigos padre".
    """
    file = open(path_relations_file, 'r')
    lines = file.readlines()
    rels_dict = dict()
    # First round to get the active relationship
    for index in tqdm(range(0, len(lines))):
        if index == 0:
            continue
        else:  
            elementos = lines[index].split("\t")
            # Si la relación es de tipo is-a procesamos
            if (elementos[7] == "116680003"):
                if elementos[4] in rels_dict.keys():
                # Si la relación ya ha sido guardada previa,emente, pero había sido inactivada, cambiamos estado  
                    if elementos[2] =="1":
                        rels_dict[elementos[4]].append((elementos[5],"1"))
                    else:
                        try:
                        # Si el valor active pasa a 0, borramos el elemento que tenia ese valor
                            rels_dict[elementos[4]].remove((elementos[5],"1"))
                        except:
                            print("WARNING: Trying to remove key {} from dict. The element was removed before".format(elementos[4]))
                else:
                    if elementos[2] =="1":
                        rels_dict[elementos[4]] = [(elementos[5],"1")] 
                    else: # No guardamos cosas inactivas.
                        continue

    print("Se han obtenido {} relaciones del archivo".format(len(rels_dict)))

    rels_dict_final = {k: list(map(operator.itemgetter(0), v)) for k, v in rels_dict.items()}
    
    return rels_dict_final


from itertools import chain 
def list_of_active_codes_from_relations(active_rels):
    """
    Given a dictionary representing each snomed-ct code and the codes to which they are attached,
     this function extracts the list of active codes, which are those with a related concept.

    Args:
        active_rels (dict): Dictionary of relations between snomed-ct codes

    Returns:
        list: List of active codes in snomed-ct
    """
    output_list = list()
    for i in active_rels:
        if len(active_rels[i])>=1:
            codigos = active_rels[i]+[i]
            output_list.append(codigos)
    output_list_final = chain.from_iterable(output_list)
    codigos_active_out = list(np.unique(list(output_list_final)))
    codigos_active_out = [ int(value) for value in codigos_active_out] 
    return codigos_active_out

def filter_concepts_by_semantic_tag(dataframe_sct, tags):
    """
    Function to select concepts that are part of the semantic tags specified in tags.
    """
    return dataframe_sct[dataframe_sct.semantic_tag.isin(tags)].reset_index(drop=True).copy()