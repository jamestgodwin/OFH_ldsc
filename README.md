# Installing LDSC (Python 3.9+ Branch)

This guide covers the installation of the `ldsc39` branch from the CBIIT repository.

## 1. Prerequisites

Ensure you have the following installed on your system:

- git
- Python 3.9 or higher

## 2. Clone the Repository

Clone the specific branch (`ldsc39`) from the CBIIT GitHub repository (or copy this repository into a working directory):

```
git clone -b ldsc39 https://github.com/CBIIT/ldsc.git
cd ldsc
```

If you have this repository locally (for example you copied the contents into a working directory), ensure you are in the project root where `ldsc.py` and the other scripts live.

## 3. Create a Virtual Environment (No Conda Required)

You can run LDSC without conda by using Python's built-in venv module and pip. This is the recommended simple approach if you don't want to manage conda environments.

### Using python -m venv (cross-platform)

Unix / macOS:

```
python3 -m venv venv
source venv/bin/activate
```

Windows (PowerShell):

```
python -m venv venv
venv\Scripts\Activate.ps1
```

Windows (cmd.exe):

```
python -m venv venv
venv\Scripts\activate.bat
```

Once the virtual environment is activated, upgrade pip and install requirements:

```
python -m pip install --upgrade pip
pip install -r requirements.txt
# Some packages may be needed explicitly depending on your platform
pip install numpy bitarray pandas scipy
```

(If you prefer not to use a virtual environment, you can install dependencies globally with pip, but this may conflict with other Python projects on your system.)

## 4. Verify Installation

Run the help command to ensure the script executes correctly:

```
python ldsc.py -h
```

## 5. Download Reference Data

LDSC requires reference LD scores and HapMap3 SNP lists to run. If you are not using the LDscore cloud web tool and are running this locally, you must download these files:

```
# Example: Download BBJ_HDLC22 LD Scores (approx 5.4MB)
wget https://ldlink.nih.gov/LDlinkRestWeb/copy_and_download/BBJ_HDLC22.txt
# munge sumstats
python munge_sumstats.py --sumstats BBJ_HDLC22.txt --out BBJ_HDLC22
# manually download ref EAS data from 1000 genomes and uncompress, move to folder with ldsc.py script
https://drive.google.com/file/d/1BtpWx02ON33KfjyCFSdmoWYlMZWImh2f/view
```

## 6. Basic Usage Example

Once installed, you can run a basic heritability analysis:

```
python ldsc.py \
    --h2 BBJ_HDLC22.sumstats.gz \
    --ref-ld-chr eas_ldscores/ \
    --w-ld-chr eas_ldscores/ \
    --out your_analysis_results
```

