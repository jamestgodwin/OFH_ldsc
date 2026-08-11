# Installing LDSC (Python 3.9+ Branch)

This guide covers the use of the amended `ldsc39` branch from the CBIIT repository. The repo has been amended to be used directly on Our Future Health's DNAnexus platform. 

This pipeline is untested and not currently validated. 

## 1. Availability of pipeline

`ldsc39` is available through the Reprogen_2026 project. You should download the folder using the following command using the terminal in the jupyter workspace

```
dx download Reprogen_2026:/helpful_files/ldsc/ -r
```

Please do not edit any of the files in the folder, only edit any files once they are in your own personal directory!  

## 2. Create the Virtual Environment (No Conda Required)

You can run LDSC without conda by using Python's built-in venv module and pip. This is the recommended simple approach if you don't want to manage conda environments.

### Using python -m venv

```
python3 -m venv venv
source venv/bin/activate
```


Once the virtual environment is activated, install requirements:

```
pip install numpy pandas scipy
```

## 3. Verify Installation

Run the help command to ensure the script executes correctly:

```
python ldsc.py -h
```

## 4. Download Reference Data

LDSC requires reference LD scores and HapMap3 SNP lists to run. If you are not using the LDscore cloud web tool and are running this locally, you must download these files:

```
# Example: Download BBJ_HDLC22 LD Scores (approx 5.4MB)
wget https://ldlink.nih.gov/LDlinkRestWeb/copy_and_download/BBJ_HDLC22.txt
# munge sumstats
python munge_sumstats.py --sumstats BBJ_HDLC22.txt --out BBJ_HDLC22
# manually download ref EAS data from 1000 genomes and uncompress, move to folder with ldsc.py script
https://drive.google.com/file/d/1BtpWx02ON33KfjyCFSdmoWYlMZWImh2f/view
```

## 5. Basic Usage Example

Once installed, you can run a basic heritability analysis:

```
python ldsc.py \
    --h2 BBJ_HDLC22.sumstats.gz \
    --ref-ld-chr eas_ldscores/ \
    --w-ld-chr eas_ldscores/ \
    --out your_analysis_results
```

