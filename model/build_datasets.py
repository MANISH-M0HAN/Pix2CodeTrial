#!/usr/bin/env python
from __future__ import print_function
from __future__ import absolute_import
__author__ = 'Tony Beltramelli - www.tonybeltramelli.com'

import os
import sys
import hashlib
import shutil
import numpy as np

argv = sys.argv[1:]

if len(argv) < 1:
    print("Error: not enough argument supplied:")
    print("build_datasets.py <input path> <distribution (default: 6)>")
    exit(0)
else:
    input_path = argv[0]

distribution = int(argv[1]) if len(argv) >= 2 else 6

TRAINING_SET_NAME = "training_set"
EVALUATION_SET_NAME = "eval_set"

paths = []
for f in os.listdir(input_path):
    if f.endswith(".gui"):
        file_name = f[:-4]
        if os.path.isfile(f"{input_path}/{file_name}.png"):
            paths.append(file_name)

total_samples = len(paths)
if total_samples == 0:
    print("Error: No valid .gui and .png file pairs found.")
    exit(1)

evaluation_samples_number = total_samples // (distribution + 1)
training_samples_number = evaluation_samples_number * distribution

# Ensure we have enough samples for the split
if training_samples_number + evaluation_samples_number > total_samples:
    print("Error: Not enough samples to split according to the specified distribution.")
    exit(1)

print("Splitting datasets, training samples: {}, evaluation samples: {}".format(training_samples_number, evaluation_samples_number))

np.random.shuffle(paths)

eval_set = []
train_set = []
hashes = set()  # Use a set for faster lookups

for path in paths:
    with open(f"{input_path}/{path}.gui", 'r', encoding='utf-8') as f:
        chars = f.read()
        content_hash = hashlib.sha256(chars.replace(" ", "").replace("\n", "").encode('utf-8')).hexdigest()

    # Check if we can add to eval_set
    if len(eval_set) < evaluation_samples_number and content_hash not in hashes:
        eval_set.append(path)
        hashes.add(content_hash)
    elif len(train_set) < training_samples_number:
        train_set.append(path)

# Check final counts
print(f"Final eval_set length: {len(eval_set)}")
print(f"Final train_set length: {len(train_set)}")

# Ensure the counts match the expected numbers
assert len(eval_set) == evaluation_samples_number, f"Expected {evaluation_samples_number} evaluation samples, but got {len(eval_set)}"
assert len(train_set) == training_samples_number, f"Expected {training_samples_number} training samples, but got {len(train_set)}"

# Create directories for the datasets if they don't exist
os.makedirs(f"{os.path.dirname(input_path)}/{EVALUATION_SET_NAME}", exist_ok=True)
os.makedirs(f"{os.path.dirname(input_path)}/{TRAINING_SET_NAME}", exist_ok=True)

# Copy files to evaluation set
for path in eval_set:
    shutil.copyfile(f"{input_path}/{path}.png", f"{os.path.dirname(input_path)}/{EVALUATION_SET_NAME}/{path}.png")
    shutil.copyfile(f"{input_path}/{path}.gui", f"{os.path.dirname(input_path)}/{EVALUATION_SET_NAME}/{path}.gui")

# Copy files to training set
for path in train_set:
    shutil.copyfile(f"{input_path}/{path}.png", f"{os.path.dirname(input_path)}/{TRAINING_SET_NAME}/{path}.png")
    shutil.copyfile(f"{input_path}/{path}.gui", f"{os.path.dirname(input_path)}/{TRAINING_SET_NAME}/{path}.gui")

print("Training dataset: {}/{}".format(os.path.dirname(input_path), TRAINING_SET_NAME))
print("Evaluation dataset: {}/{}".format(os.path.dirname(input_path), EVALUATION_SET_NAME))

