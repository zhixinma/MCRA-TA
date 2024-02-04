# MCRA-TA

## Introduction
This repo is the TA's toolkit for the SMU course: IS446-Manage Customer Relationship with Analytics


## Getting Start

### Prerequisites
1. Clone this repo
```
git clone https://github.com/zhixinma/MCRA-TA
cd MCRA-TA
```

2. Data Preparation

The data should be organized as follows. The folder ```Trailheads``` and ```WeeklyReflection``` under ```data``` are the folders for the raw data. In the following file structure, ```M15W01``` and ```TrailheadLinks-20230913.csv``` are the examples to test the code. The example data can be found [here](https://drive.google.com/drive/folders/17ybolRxoeGSWJDxtODp8-mN60TJH2n_U?usp=sharing). The generated data will be output to the ```Analysis``` folder under ```data```.

```
.
├── data
│   ├── Trailheads
│   │   └── TrailheadLinks-20230913.csv
│   ├── WeeklyReflection
│   │   └── M15W01
│   │       ├── ESM6W01-Learn.csv
│   │       ├── ESM6W01-Topics.csv
│   │       ├── M15W01-Learn.csv
│   │       └── M15W01-Topics.csv
│   └── Analysis
│       ├── M15W01 (2024-01-19)
│       │   ├── ESM6W01-Learn_emo.csv
│       │   ├── ESM6W01-Learn_phrases.csv
│       │   ├── ESM6W01-Topics_phrases.csv
│       │   ├── M15W01-Learn_emo.csv
│       │   ├── M15W01-Learn_phrases.csv
│       │   └── M15W01-Topics_phrases.csv
│       └── Trailhead (2023-12-04)
│           ├── 2023-12-04_badges.csv
│           ├── 2023-12-04_details.csv
│           └── 2023-12-04_skills.csv
├── trailhead_analyze.py
└── weekly_survey_analyze.py
```

3. Requirements

A conda environment can be created using the code: ```conda env create --name MCRA_TA```

The required packages are as follows:
```
nltk==3.5
pandas==1.3.3
spacy==3.7.2
tqdm==4.47.0
spacytextblob==4.0.0
requests==2.24.0
```

### Run the code

#### Trailhead Analysis
```
python trailhead_analyze.py -f /path/to/the/raw/file
```

#### Weekly Reflection Analysis
Before running the code, make sure you have set the correct configuration in the ```main``` function:
```
COURSE_CODE = "M15"
ESM_COURSE_CODE = "ESM6"
WEEK_NUM = "02"
```
Then run the following cmd:
```
python weekly_survey_analyze.py
```

### Acknowledgements
Thanks for Jiapeng Lim's contribution to the original code.

