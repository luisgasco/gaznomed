import csv, os, sys, pickle
import pandas as pd

# Include system path
general_path = os.getcwd().split("gaznomed")[0]+"gaznomed/"
sys.path.append(general_path+'src/')
from utils.tabular_read import active_terms_from_conceptRF2_file, get_active_relations, \
                     list_of_active_codes_from_relations, filter_concepts_by_semantic_tag, \
                         prepare_concept_df
from utils.graph_read import load_ontology, get_sucessors_from_list
from optparse import OptionParser


# Function to parse comma-´separated values
def get_comma_separated_args(option, opt, value, parser):
    setattr(parser.values, option.dest, value.split(','))


def main(argv=None):
    parser = OptionParser()
    parser.add_option("-c", "--concept_file", dest = "concept_path", help = "Path to the RF2 snomed-ct concept file", default=None)
    parser.add_option("-r", "--relation_file", dest = "relation_path", help = "Path to the RF2 snomed-ct relation file", default=None)
    parser.add_option("-l", "--language", dest = "language", help = "Language of the concept file. It can be 'en' or 'es'.", default=None)
    parser.add_option("-s", "--semantic_tags", dest="semantic_tag_list", type=str, action="callback", callback=get_comma_separated_args, \
        help="Provide list of snomed-ct semantic tags separated by comma (without space) you want to select from sct terminology. Default \
            value selects all semantic tags. If you don't want to select any semantic tag, write 'None'", default="all")
    parser.add_option("-t", "--subtrees", dest="subtrees_code_list", type=str, action="callback", callback=get_comma_separated_args, \
        help="Provide a comma-separated list of snomed-ct codes (without spaces) from which you want to get the subtrees", default=None)
    parser.add_option("-o", "--out", dest="out", help="Absolute output path where you want to save the gazetteer")
    #parser.add_option("-p", "--preprocessing", dest = "preprocessing_args", type=str, action="callback", callback=get_comma_separated_args, help="Preprocessing to be done on text and terminologies")
    
    (options, args) = parser.parse_args(argv)
    print("Parameters selected for the attribute 'semantic_tags'")
    print(options.semantic_tag_list)
    print("Parameters selected for the attribute 'subtrees'")
    print(options.subtrees_code_list)
    
    # Rear active terms from the concepts Snomed-CT RF2 File
    concepts = active_terms_from_conceptRF2_file(options.concept_path)
    # Prepare a dataframe with the correct shape:
    concepts_df_prepared = prepare_concept_df(concepts,options.language)


    # Load a dictionary that contains the parent codes of each Snomed-CT code. If the code has no parents, means that that code is deprecated. 
    active_rels = get_active_relations(options.relation_path)
    # From that active_rels variable, obtain the list of active codes.
    active_codes = list_of_active_codes_from_relations(active_rels)
    # Filter the concept_df, only maintaining the active_codes
    concepts_df_prepared = concepts_df_prepared[concepts_df_prepared.code.isin(active_codes)].reset_index(drop=True).copy()

    # FILTER SEMANTIC TAGS 
    if options.semantic_tag_list == "all" or options.semantic_tag_list == ["all"]:
        filtered_concepts_df = concepts_df_prepared.copy()
    elif options.semantic_tag_list == ["None"]: 
        filtered_concepts_df = pd.DataFrame(columns=["code","language","term","semantic_tag","mainterm"])
    else:
        filtered_concepts_df = filter_concepts_by_semantic_tag(concepts_df_prepared.copy(), options.semantic_tag_list)



    # Check if we need to compute any substree
    if options.subtrees_code_list is None:
        print("No need to include subtree codes")
        subtrees_df = pd.DataFrame(columns=["code","language","term","semantic_tag","mainterm"])
    else: 
        # Load snomed-as hiearchical structure (networkx)
        g = load_ontology(options.relation_path, root_concept_code = "138875005", relation_types=["116680003"])
        # Compute the children from the codes.
        print("Generating subtrees codes")
        # Transform input codes to ints
        lista_ints = [int(i) for i in options.subtrees_code_list]
        codigos_subtress = get_sucessors_from_list(g, lista_ints)
        # Select from dataframe those codes
        subtrees_df = concepts_df_prepared[concepts_df_prepared.code.isin(codigos_subtress)].reset_index(drop=True).copy()

    # PREPARE OUTPUT FILE
    output_df = pd.concat([filtered_concepts_df, subtrees_df]).reset_index(drop=True).copy()
    output_df = output_df.drop_duplicates(subset=["code","language","term","semantic_tag"]).reset_index(drop=True)
    output_df.columns = ["code","term","semantic_tag","mainterm","language"]
    output_df.to_csv(options.out, sep="\t",index=False)
    print("Save file in {}".format(options.out))

if __name__ == "__main__":
  sys.exit(main())