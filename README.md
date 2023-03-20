# gaznomed
This repository contains a script to generate a snomed-ct concept gazzeteer from snomed-ct RF2 arhcives. The script allows to generate only codes corresponding to specific snomed semantic branches. In addition, it also allows to generate gazzeteers from the children of a specified code list.



### Installation

1. Clone the repo

   ```sh
   git clone https://github.com/luisgasco/gaznomed.git
   ```

2. Create a new virtual environment

   ```sh
   python3 -m venv .env_gaznomed
   ```

3. Activate the new environment

   ```sh
   source .env_gaznomed/bin/activate
   ```

4. Install the requirements

    ```sh
    pip install -r requirements.txt
    ```

5. Download the RF2 files from Snomed-CT

### Usage
The gazenomed.py script has the following options:


- **Concept file path** (-c or --concept_file): Path to the RF2 snomed-ct concept file. This file is named `sct2_Description_Full...` and is located in the Snomed-CT relative path `/Full/Terminology/`
- **Relation file path** (-r or --relation_file): Path to the RF2 snomed-ct relation file. This file is named `sct2_Relationship_Full_...` and is located in the Snomed-CT relative path `/Full/Terminology/`. This file only exists in the international version.
- **Language** (-l or --language): Language of the concept file. It can be 'en' or 'es'
- **Semantic tags** (-s or --semantic_tags): list of snomed-ct semantic tags separated by comma (without space) you want to select from sct terminology. The default value ('all0) selects all semantic tags. If you don't want to select any semantic tag, write 'None'
- **Subtrees** (-t or --subtrees): a comma-separated list of snomed-ct codes (without spaces) from which you want to get the subtrees
- **Output path** (-o or --out): Absolute output path where you want to save the gazetteer

## Some examples: 

- Obtain the codes of the subtrees corresponding to the codes 159682009 and 159700006: 
    ```bash
    python src/gaznomed.py --concept_file "PATH_TO_SCT_FILES/SnomedCT_InternationalRF2_PRODUCTION_20210731T120000Z/Full/Terminology/sct2_Description_Full-en_INT_20210731.txt" \
    --relation_file "PATH_TO_SCT_FILES/SnomedCT_InternationalRF2_PRODUCTION_20210731T120000Z/Full/Terminology/sct2_Relationship_Full_INT_20210731.txt" \
    --language en \ # We use 'en' because the concept file is in english
    --semantic_tags None \
    --subtrees 159682009,159700006 \ #It is very important not to put spaces after commas
    --out "OUTPUTFILE.tsv"
    ```

- Obtain the codes of the semantic class "person" and "substance":
    ```bash
    python src/gaznomed.py --concept_file "PATH_TO_SCT_FILES/SnomedCT_InternationalRF2_PRODUCTION_20210731T120000Z/Full/Terminology/sct2_Description_Full-en_INT_20210731.txt" \
    --relation_file "PATH_TO_SCT_FILES/SnomedCT_InternationalRF2_PRODUCTION_20210731T120000Z/Full/Terminology/sct2_Relationship_Full_INT_20210731.txt" \
    --language en \ # We use 'en' because the concept file is in english
    --semantic_tags substance,person \
    --out "OUTPUTFILE.tsv"
    ```

- Obtain the full snomed-ct gazzetteer:
    ```bash
    python src/gaznomed.py --concept_file "PATH_TO_SCT_FILES/SnomedCT_InternationalRF2_PRODUCTION_20210731T120000Z/Full/Terminology/sct2_Description_Full-en_INT_20210731.txt" \
    --relation_file "PATH_TO_SCT_FILES/SnomedCT_InternationalRF2_PRODUCTION_20210731T120000Z/Full/Terminology/sct2_Relationship_Full_INT_20210731.txt" \
    --language en \ # We use 'en' because the concept file is in english
    --out "OUTPUTFILE.tsv"
    ```
