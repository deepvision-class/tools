This repository has utility scripts for students.

## Installation

```bash
pip install nbformat
git clone https://github.com/deepvision-class/tools.git
```

## Homework Validation
Use this script to validate the .zip file for your homework before submitting it.

Usage:
```bash
python validate_submission.py [assignment] [zip file]
```

Example:
```bash
python validate_submission.py a1 justincj_012345.zip
```

This script will attempt to warn you about issues with your homework assignment:
- Zip file is not named correctly
- Zip file contains the correct files
- Notebook files did not have any cells modified that shouldn't have been
- All sections where you were supposed to write code have something filled in

Note that **this script does not check whether your homework is correct**.
It only provides some basic checks about the structure of your submitted files.

**In order to be graded your assignment must pass this validation script**.
It is your responsibility to run this script on your assignment before you submit it.
