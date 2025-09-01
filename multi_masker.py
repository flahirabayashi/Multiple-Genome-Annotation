import argparse
import os
import subprocess
import glob

# --- ARGUMENT PARSER ---
parser = argparse.ArgumentParser(
    description="Pipeline for RepeatModeler and RepeatMasker (multiple genomes)"
)
parser.add_argument(
    "-i", "--input",
    required=True, help="Path to directory containing genome FASTA files"
)
parser.add_argument(
    "-t", "--threads",
    required=True, type=int, help="Number of threads to use"
)
parser.add_argument(
    "-o", "--output",
    required=True, help="Output directory for all results"
)
args = parser.parse_args()

# --- VARIABLES ---
input_dir = os.path.abspath(args.input)
threads = args.threads
outdir = os.path.abspath(args.output)

# Create main output directory if it does not exist
os.makedirs(outdir, exist_ok=True)

# Find all FASTA files in the input directory
genome_files = sorted(glob.glob(os.path.join(input_dir, "*.fasta")))
if not genome_files:
    raise FileNotFoundError(f"No .fasta files found in {input_dir}")

# --- PROCESS EACH GENOME ---
for genome_path in genome_files:
    genome = os.path.abspath(genome_path)
    genome_name = os.path.splitext(os.path.basename(genome_path))[0]

    print(f"\n=== Processing genome: {genome_name} ===")

    # Create output directory for this genome
    genome_outdir = os.path.join(outdir, genome_name)
    os.makedirs(genome_outdir, exist_ok=True)

    # Name for RepeatModeler database
    db_name = os.path.join(genome_outdir, "repmod_db")

    # --- STEP 1: BuildDatabase ---
    print(f"Building RepeatModeler database for {genome_name}...")
    subprocess.run([
        "/opt/apps/RepeatModeler-2.0.3/BuildDatabase",
        "-name", db_name,
        genome
    ], check=True)

    # --- STEP 2: Run RepeatModeler ---
    print(f"Running RepeatModeler for {genome_name}...")
    rmod_dir = os.path.join(genome_outdir, "repeatmodeler_out")
    os.makedirs(rmod_dir, exist_ok=True)

    subprocess.run([
        "RepeatModeler",
        "-database", db_name,
        "-pa", str(threads),
        "-LTRStruct",
        "-dir", rmod_dir
    ], check=True)

    # Path to RepeatModeler output library
    repeat_library = os.path.join(rmod_dir, "consensi.fa.classified")

    # --- STEP 3: Run RepeatMasker ---
    print(f"Running RepeatMasker for {genome_name}...")
    masked_dir = os.path.join(genome_outdir, "repeatmasker_out")
    os.makedirs(masked_dir, exist_ok=True)

    subprocess.run([
        "RepeatMasker",
        "-pa", str(threads),
        "-e", "rmblast",
        "-xsmall",
        "-lib", repeat_library,
        "-dir", masked_dir,
        "-gff",
        "-trf_prgm", "/usr/local/bin/",
        genome
    ], check=True)

    print(f"RepeatMasker results for {genome_name} are in: {masked_dir}")

print("\n=== All genomes processed successfully! ===")
