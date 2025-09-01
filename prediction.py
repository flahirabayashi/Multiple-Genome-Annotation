import argparse
import os
import subprocess
import glob

# --- ARGUMENTS ---
parser = argparse.ArgumentParser(
    description="Pipeline for BRAKER3 annotation on masked genomes (multiple genomes)"
)
parser.add_argument(
    "-i", "--input",
    required=True, help="Path to directory containing genome subfolders with RepeatMasker output"
)
parser.add_argument(
    "-p", "--proteins",
    required=True, help="Path to protein database FASTA file"
)
parser.add_argument(
    "-t", "--threads",
    required=True, type=int, help="Number of threads to use"
)
parser.add_argument(
    "-o", "--output",
    required=True, help="Output directory for all BRAKER results"
)
args = parser.parse_args()

# --- VARIABLES ---
input_dir = os.path.abspath(args.input)
protein_db = os.path.abspath(args.proteins)
threads = args.threads
outdir = os.path.abspath(args.output)

# Create main output directory
os.makedirs(outdir, exist_ok=True)

# Find all masked genome files (searching for *.masked)
masked_files = sorted(glob.glob(os.path.join(input_dir, "*", "repeatmasker_out", "*.masked")))

if not masked_files:
    raise FileNotFoundError(f"No masked genome files (*.masked) found in {input_dir}")

# --- PROCESS EACH GENOME ---
for masked_genome in masked_files:
    # Remove .fasta.masked para obter o nome base do genoma
    base_name = os.path.basename(masked_genome).replace(".fasta.masked", "")
    
    # Use o nome base como o nome do genoma
    genome_name = base_name.replace(".fna", "").replace(".fa", "")

    print(f"\n=== Running BRAKER3 for genome: {genome_name} ===")

    # Create genome-specific BRAKER output directory
    braker_outdir = os.path.join(outdir, genome_name)
    os.makedirs(braker_outdir, exist_ok=True)
    
    # --- RUNNING BRAKER3 ---
    subprocess.run([
        "braker.pl",
        f"--threads={threads}",
        "--fungus",
        f"--genome={masked_genome}",
        "--gff3",
        f"--species={genome_name}",
        f"--prot_seq={protein_db}",
        f"--workingdir={braker_outdir}",
    ], check=True)

    print(f"BRAKER3 annotation completed for {genome_name}. Results in: {braker_outdir}")