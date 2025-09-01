import argparse
import subprocess
import os
import shutil

def download_genomes(accessions_file, output_dir):
    """
    Downloads genome sequences from NCBI from a list of IDs and saves them to an output directory.
    
    Args:
        -f accessions.txt: Path to the text file with accession IDs (one per line).
        -o output_dir: Path to the directory where the files will be saved.
    """
    # 1. Check if the input file exists
    if not os.path.exists(accessions_file):
        print(f"Error: The file '{accessions_file}' was not found.")
        return

    # 2. Read the IDs from the file
    with open(accessions_file, 'r') as f:
        accessions = [line.strip() for line in f if line.strip()]

    if not accessions:
        print(f"The file '{accessions_file}' is empty. No genomes to download.")
        return

    # 3. Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Output directory '{output_dir}' created.")

    print(f"Starting the download of {len(accessions)} genomes...")
    
    for accession in accessions:
        print(f"\n--- Processing genome: {accession} ---")
        
        # 4. Command to download the data package
        command = [
            "datasets",
            "download",
            "genome",
            "accession",
            accession,
            "--no-progressbar"
        ]
        
        try:
            print(f"Downloading data for '{accession}'...")
            subprocess.run(command, check=True)
            
            # 'datasets' saves the file as 'ncbi_dataset.zip'
            temp_zip_path = "ncbi_dataset.zip"

            if not os.path.exists(temp_zip_path):
                print(f"Warning: The file '{temp_zip_path}' was not created. Download may have failed for '{accession}'.")
                continue

            # 5. Unzip the temporary file
            print("Decompressing the file...")
            shutil.unpack_archive(temp_zip_path, extract_dir=".")
            
            # 6. Find the .fna or .fasta file inside the folder structure
            download_folder = os.path.join("ncbi_dataset", "data", accession)
            genome_file = None

            if os.path.exists(download_folder):
                for file in os.listdir(download_folder):
                    if file.endswith(".fna") or file.endswith(".fasta"):
                        genome_file = file
                        break
            
            if genome_file:
                source_path = os.path.join(download_folder, genome_file)
                dest_path = os.path.join(output_dir, f"{accession}.fasta")

                # 7. Move the file to the output directory and rename it
                shutil.move(source_path, dest_path)
                print(f"Genome for '{accession}' saved to '{dest_path}'.")
            else:
                print(f"Warning: Could not find a .fna/.fasta file for {accession}.")
                
        except subprocess.CalledProcessError as e:
            print(f"Error: Download for '{accession}' failed. Command '{' '.join(e.cmd)}' returned with exit code {e.returncode}.")
        except FileNotFoundError:
            print("Error: The 'datasets' command was not found. Make sure the tool is installed and in your PATH.")
            return
        finally:
            # 8. Clean up temporary files and folders
            if os.path.exists("ncbi_dataset"):
                shutil.rmtree("ncbi_dataset", ignore_errors=True)
            if os.path.exists(temp_zip_path):
                os.remove(temp_zip_path)
        
    print("\n--- Download process finished. ---")

def main():
    """
    Main function to set up command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Download genomes from NCBI from a list of IDs and save them to a specified directory.",
        epilog="Example: python download_genomes.py --file accessions.txt --output my_genomes"
    )
    
    parser.add_argument(
        '-f', '--file', 
        type=str,
        required=True,
        help="Path to the text file containing NCBI genome accession IDs (one per line)."
    )
    
    parser.add_argument(
        '-o', '--output', 
        type=str,
        required=True,
        help="Path to the output directory where the .fasta files will be saved."
    )
    
    args = parser.parse_args()
    download_genomes(args.file, args.output)

if __name__ == "__main__":
    main()
