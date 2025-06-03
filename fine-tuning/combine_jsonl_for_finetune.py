
import glob

output_file = "all_examples_for_finetune.jsonl"
input_files = glob.glob("*.jsonl")

with open(output_file, "w") as outfile:
    for fname in input_files:
        if fname == output_file:
            continue  # Skip the output file if it already exists in the directory
        with open(fname, "r") as infile:
            for line in infile:
                outfile.write(line)

print(f"Combined {len(input_files)} files into {output_file}")
