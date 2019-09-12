#-*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import division

import argparse
import os
import tempfile
import shutil
import re
import zipfile
import nbformat

#################################################
# DO NOT TOUCH THIS CONFIGS
HOMEWORK_FILENAMES = {
  'a1': [['pytorch101.ipynb'], ['kNN.ipynb', 'knn.ipynb']]
}
META_INFOS = {
  'pytorch101.ipynb': {
    'num_cells': 152,
    'num_markdowns': 89,
    'code_cell_idx_list': [2, 28, 33, 42, 57, 61, 70, 75, 77, 98, 113, 122, 140, 151],
    'num_code_outputs': 59,
  },
  'knn.ipynb': {
    'num_cells': 48,
    'num_markdowns': 25,
    'code_cell_idx_list': [16, 22, 26, 32, 40, 45],
    'num_code_outputs': 16,
  }
}
#################################################

OUR_TEST_ZIP_FILENAME = 'test.zip'
parser = argparse.ArgumentParser()
parser.add_argument('assignment', choices=HOMEWORK_FILENAMES.keys())
parser.add_argument('zip_file_path')

def run_evaluation(testfile_path, tempdir_path, filenames):
  # unzip the zip file
  temp_zipfile = zipfile.ZipFile(testfile_path, 'r')
  temp_zipfile.extractall(tempdir_path)
  temp_zipfile.close()

  # 2. check the filenames
  targetfile_list_str = " ".join([x[0] for x in filenames])
  repfile_to_repfile_dict = {}
  for single_filename_candiates in filenames:
    single_file_exists = False
    real_filename = None
    for single_filename in single_filename_candiates:
      if os.path.exists(os.path.join(tempdir_path, single_filename)):
        single_file_exists = True
        student_filename = single_filename
        break
    if not single_file_exists:
      print("[ERROR] Zip file does not include {}".format(single_filename_candiates[0]))
      print("[Comment] Please zip with with '$ zip uniquename_umid.zip {}'.".format(targetfile_list_str))
      return False
    repfile_to_repfile_dict[student_filename.lower()] = student_filename


  # 2-1. check is there any other files exists
  flatten_filename_list = [y for x in filenames for y in x]
  flatten_filename_list.append(OUR_TEST_ZIP_FILENAME)
  for iter_filename in os.listdir(tempdir_path):
    single_filename = os.path.basename(iter_filename)
    if single_filename not in flatten_filename_list:
      print("[ERROR] Zipfile includes unexpected file: {}".format(single_filename))
      print("[Comment] Please zip with with '$ zip uniquename_umid.zip {}'.".format(targetfile_list_str))
      return False


  # 3. start to check about ipynb files
  for repfile, studentfile in repfile_to_repfile_dict.items():
    with open(os.path.join(tempdir_path, studentfile), 'r') as f:
      nb = nbformat.read(f, nbformat.NO_CONVERT)

    metadata = META_INFOS[repfile]

    # 3.1 Check they put their name in the IPython notebook
    if nb.cells[1]['source'].strip().endswith('#12345678') or \
       nb.cells[1]['source'].strip().endswith('#00000000') or \
       nb.cells[1]['source'].strip().endswith('#XXXXXXXX'):
      print("[ERROR] please put your Name and UMID in {}".format(studentfile))
      return False

    # 3.2 Check the number of Cells
    if len(nb.cells) != metadata['num_cells']:
      print("[ERROR] The number of cells are not matched: {}".format(repfile))
      print("Expected vs Real : {} vs {}".format(metadata['num_cells'], len(nb.cells)))
      print("DO NOT REMOVE/ADD additional cells")
      return False

    # 3.3 Check the number of the markdown cells
    num_markdown_cells = len([idx for idx, c in enumerate(nb.cells) if c['cell_type'] == 'markdown'])
    if num_markdown_cells != metadata['num_markdowns']:
      print("[ERROR] The number of markdown cells are not matched: {}".format(repfile))
      print("Please check whether you removed any of the text cell or not")
      return False

    # 3.4 Check the position of code cells
    stduent_code_cell_idx_list = [idx for idx, c in enumerate(nb.cells)
                                  if "END OF YOUR CODE" in c['source']]
    if metadata['code_cell_idx_list'] != stduent_code_cell_idx_list:
      print("[ERROR] Position of code cells are not matched: {}".format(repfile))
      print("Please check the order of your cells")
      return False

    # 3.5 Check if student wipe out the print log in any code cells
    stduent_code_cell_print_count = sum([1 for c in nb.cells if (c['cell_type'] == 'code') and (len(c.get('outputs', [])) != 0)])
    if stduent_code_cell_print_count != metadata['num_code_outputs']:
      print("[ERROR] Some print logs are removed: {}".format(repfile))
      print("Expected vs Real : {} vs {}".format(metadata['num_code_outputs'], stduent_code_cell_print_count))
      print("Please re-run your ipynb file.")
      return False

  return True



def main(args):
  print("Zip file path: {}".format(args.zip_file_path))
  # 0. Check file exists
  if not os.path.exists(args.zip_file_path):
    print("[Error] Failed to find zip file.")
    return

  # 1. Check zip filename format
  filename = os.path.basename(args.zip_file_path)
  if not re.match(r"[a-z]+_\d{8}\.zip", filename):
    print("[Warning] Please set it as uniquename_umid.zip.")


  # create temporary folder
  tempdir_path = tempfile.mkdtemp()
  print("Temp folder path: {}".format(tempdir_path))

  # copy the zip file to temporary folder
  testfile_path = os.path.join(tempdir_path, OUR_TEST_ZIP_FILENAME)
  shutil.copyfile(args.zip_file_path, testfile_path)

  # get the filenames for this assignment
  filenames = HOMEWORK_FILENAMES[args.assignment]

  is_LGTM = run_evaluation(testfile_path, tempdir_path, filenames)

  # 4. remove temporary folder
  print("Removing the temp folder {}".format(tempdir_path))
  shutil.rmtree(tempdir_path)
  if is_LGTM:
    print("Your zipfile {} looks good to me!".format(args.zip_file_path))


if __name__ == "__main__":
  main(parser.parse_args())
