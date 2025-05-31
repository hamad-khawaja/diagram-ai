import json

def convert_to_chat(example):
    if "messages" in example:
        return example  # Already in chat format
    elif "prompt" in example and "completion" in example:
        return {
            "messages": [
                {"role": "user", "content": example["prompt"]},
                {"role": "assistant", "content": example["completion"]}
            ]
        }
    else:
        return None  # Skip invalid

import os

input_file = "all_examples_for_finetune.jsonl"
output_file = "all_examples_for_finetune.chat.jsonl"

# Overwrite the output file if it exists
if os.path.exists(output_file):
    os.remove(output_file)

with open(input_file) as fin, open(output_file, "w") as fout:
    for line in fin:
        ex = json.loads(line)
        chat_ex = convert_to_chat(ex)
        if chat_ex:
            fout.write(json.dumps(chat_ex) + "\n")

print(f"Converted file written to {output_file}")
