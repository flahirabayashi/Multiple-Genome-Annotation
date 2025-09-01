# Multiple-Genome-Annotation
A Python pipeline for identifying repetitive elements and predicting proteins across multiple eukaryotic genomes, using RepeatModeler, RepeatMasker and BRAKER3.

## Overview
This repository provides an automated pipeline for eukaryotic genome annotation. This workflow is designed to handle multiple genomes. It integrates a series of bioinformatics tools to perform three essential stages:

    Genome Data Retrieval: Downloads raw genome assemblies from the NCBI using accession IDs.

    Repeat Masking: Uses RepeatModeler and RepeatMasker to first build a repeat library and then mask repetitive elements in the genomes.

    Gene Prediction: Employs BRAKER3 to perform a hybrid gene annotation. This method combines ab initio gene prediction with evidence from a protein database, resulting in highly accurate gene structures.

## Requirements

Software

    NCBI Datasets CLI: Used by the first script to download genome sequences directly from NCBI.

    RepeatModeler 2.0+: A tool to build a de novo repeat library. Requires a dependency on TRF (Tandem Repeats Finder).

    RepeatMasker: The tool to mask the genome using the repeat library. It requires a search engine; we configured the script to use rmblast for optimal performance.

    BRAKER3: The primary gene prediction tool. It has internal dependencies:

        GeneMark-ES/ET, AUGUSTUS and Protein Homology Search Tool - The pipeline requires either DIAMOND or BLAST+ to find homologous proteins, it uses DIAMOND.

Data

    Genome Accession List: A plain text file (e.g., accessions.txt) containing a list of NCBI accession IDs, with one ID per line.

    Protein Database: A protein database in FASTA format. This database should be from a closely related species to maximize the accuracy of the gene predictions. You can use databases from sources like UniProt, OrthoDB, or specific research projects.

## How to Use

### Step 1: Prepare Your Accession List and Environment

Before you begin, create a plain text file named accessions.txt with one NCBI genome accession ID per line. This list will tell the pipeline which genomes to download. For example:
```
GCA_000001405.1
GCA_000002945.1
GCA_000002985.1
.
.
.
```
Next, create and activate your Conda environment to manage the software dependencies and avoid conflicts (usefull mainly to run BRAKER3):
```
conda create -n annotation_env python=3.9
conda activate annotation_env
```
### Step 2: Download Genomes from NCBI
Use the genome_downloader.py script to retrieve the genomes listed in your accessions.txt file.
```
python3 genome_downloader.py \
  -f accessions.txt \
  -o genomes
```
### Step 3: Mask Repeats
Run the multi_masker.py script. This step will create a new subdirectory for each genome, containing the repeat library and the masked genome file (*.masked).
```
python3 multi_masker.py \
  -i path/to/genomes \
  -t 20 \
  -o masked_genomes
```
### Step 4: Run BRAKER3 for Gene Prediction
Finally, use the prediction.py script to perform the gene prediction on the masked genomes. This step requires a protein database. \*The --fungus flag was used to optimize the script for fungal genomes, but it can be changed for other organisms.
```
python3 run_braker.py \
  -i path/to/masked_genomes \
  -p /path/to/protein_db.faa \
  -t 20 \
  -o prediction_output
```

## Generated Output

### Masking Output

Inside each genome's folder, you'll find the following key files and directories:

    repmod_db: A directory containing the database files used by RepeatModeler.

    repeatmodeler_out: A subdirectory with the results of the de novo repeat library generation.

        consensi.fa.classified: This is the custom-built repeat library in FASTA format, ready for use with RepeatMasker.

    repeatmasker_out: A subdirectory containing the results of the masking process.

        *.fasta.masked: The masked genome. This is the core output file that serves as the input for the next step. In this file, repetitive regions are converted to lowercase letters.

        *.fasta.out: A detailed text file listing the coordinates and type of each repeat found.

        *.fasta.tbl: A summary table of the repeat content found in the genome.

<hr>

### BRAKER3 Annotation Output

The prediction.py script creates a new output directory for each genome (e.g., braker_results_dir/genome_name). Inside, you will find subdirectories and files that detail the gene prediction process. Some of them are:

    braker.aa: A FASTA file containing the predicted protein sequences (amino acids) corresponding to the annotated genes.
    
    braker.log: The main log file for the BRAKER3 run.

    braker.gff3: The primary output file containing the final gene annotations in GFF3 format.

    braker.codingseq: A FASTA file containing the nucleotide coding sequences of the predicted genes.

    prothint.gff: A GFF file that contains the extrinsic evidence (protein alignment) data extracted from your protein database.

    species/: A directory containing the species-specific training parameters for AUGUSTUS.

    GeneMark-ES/, GeneMark-EP/, Augustus/, errors/: Directories containing various intermediate files and log files from the individual tools within the BRAKER pipeline.
