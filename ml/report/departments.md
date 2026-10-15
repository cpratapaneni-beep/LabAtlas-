# The wet/dry axis, department by department

Every unit was classified by hand by its research character (`department_types.csv`). That typing was used to choose which investigators to read and label next, and to report accuracy by department. It is **not** an input to any one person's call: tested as a model feature, it cost 3-4 points on the investigators who do not match their department (the physician-scientist with a bench lab in a clinical department, the pathologist listed in a basic-science programme), so each person is read from their own work.

## Accuracy on the locked test set, by research character

| research character | test investigators | model on the right side |
|---|---|---|
| Clinical | 279 | 91% (254 of 279) |
| Public & population health | 45 | 89% (40 of 45) |
| Translational research centre | 40 | 70% (28 of 40) |
| Basic science | 23 | 78% (18 of 23) |
| Pathology & laboratory medicine | 15 | 100% (15 of 15) |
| Nursing | 14 | 100% (14 of 14) |
| Engineering | 8 | 88% (7 of 8) |
| Genetics | 8 | 88% (7 of 8) |
| Quantitative | 7 | 71% (5 of 7) |
| Behavioural & social science | 4 | 75% (3 of 4) |
| Administrative | 2 | 100% (2 of 2) |

A person in several units counts once in each. Small groups carry wide uncertainty.

## Every unit

| unit | character | members | wet side | hybrid | dry side | unclassified | hand-labelled | test: right / scored |
|---|---|---|---|---|---|---|---|---|
| Medicine (SOM) | Clinical | 1183 | 93 | 18 | 773 | 299 | 171 | 54 / 58 |
| Pediatrics (SOM) | Clinical | 939 | 103 | 11 | 599 | 226 | 137 | 53 / 63 |
| Environmental Health (RSPH) | Public & population health | 583 | 5 | 6 | 470 | 102 | 78 | 26 / 31 |
| Global Health (RSPH) | Public & population health | 576 | 5 | 6 | 463 | 102 | 77 | 26 / 31 |
| Psychiatry (SOM) | Clinical | 512 | 23 | 7 | 297 | 185 | 60 | 26 / 28 |
| Radiology & Imaging (SOM) | Clinical | 349 | 10 | 1 | 246 | 92 | 33 | 7 / 7 |
| Surgery (SOM) | Clinical | 307 | 14 | 3 | 259 | 31 | 47 | 18 / 18 |
| Neurology (SOM) | Clinical | 254 | 20 | 2 | 141 | 91 | 28 | 7 / 10 |
| Anesthesiology (SOM) | Clinical | 250 | 8 | 0 | 158 | 84 | 25 | 7 / 8 |
| Pathology & Lab Medicine (SOM) | Pathology & laboratory medicine | 242 | 63 | 11 | 124 | 44 | 54 | 15 / 15 |
| Emergency Medicine (SOM) | Clinical | 234 | 5 | 0 | 171 | 58 | 25 | 7 / 8 |
| Cancer Prevention & Control (Winship) | Public & population health | 224 | 2 | 3 | 218 | 1 | 32 | 18 / 19 |
| Discovery & Developmental Therapeutics (Winship) | Translational research centre | 209 | 57 | 8 | 143 | 1 | 39 | 9 / 12 |
| General faculty (Nursing) | Nursing | 199 | 2 | 0 | 169 | 28 | 37 | 14 / 14 |
| Family & Preventive Med. (SOM) | Clinical | 181 | 4 | 2 | 91 | 84 | 20 | 7 / 9 |
| Orthopaedics (SOM) | Clinical | 175 | 15 | 3 | 121 | 36 | 30 | 9 / 9 |
| Hematology / Oncology (SOM) | Clinical | 167 | 28 | 5 | 118 | 16 | 26 | 5 / 6 |
| Epidemiology (RSPH) | Public & population health | 151 | 2 | 1 | 128 | 20 | 22 | 6 / 7 |
| Human Genetics (SOM) | Genetics | 145 | 29 | 6 | 74 | 36 | 33 | 7 / 8 |
| CCTR (CHOA) | Clinical | 143 | 5 | 5 | 104 | 29 | 23 | 8 / 10 |
| Aflac (CHOA) | Clinical | 143 | 29 | 8 | 79 | 27 | 23 | 8 / 9 |
| Rehabilitation Medicine (SOM) | Clinical | 137 | 3 | 1 | 87 | 46 | 19 | 10 / 10 |
| Ophthalmology (SOM) | Clinical | 122 | 14 | 2 | 75 | 31 | 17 | 8 / 8 |
| Cell & Molecular Biology (Winship) | Basic science | 120 | 82 | 10 | 28 | 0 | 37 | 7 / 9 |
| Gynecology & Obstetrics (SOM) | Clinical | 118 | 6 | 0 | 83 | 29 | 19 | 3 / 3 |
| Biomedical Engineering (SOM) | Engineering | 107 | 51 | 7 | 30 | 19 | 24 | 4 / 4 |
| CF-AIR (CHOA) | Translational research centre | 99 | 42 | 1 | 35 | 21 | 15 | 4 / 6 |
| Behavioral, Social, & Health Education Scien… (RSPH) | Public & population health | 97 | 0 | 1 | 84 | 12 | 16 | 6 / 6 |
| REACH Center (CHOA) | Clinical | 95 | 1 | 1 | 77 | 16 | 13 | 6 / 6 |
| Health Policy & Management (RSPH) | Public & population health | 87 | 0 | 0 | 63 | 24 | 7 | 2 / 3 |
| Radiation Oncology (SOM) | Clinical | 86 | 10 | 1 | 74 | 1 | 16 | 5 / 5 |
| CCNR (CHOA) | Translational research centre | 79 | 30 | 2 | 42 | 5 | 15 | 7 / 8 |
| SOMPI (SOM) | Clinical | 78 | 2 | 1 | 55 | 20 | 12 | 8 / 8 |
| Dermatology (SOM) | Clinical | 73 | 8 | 0 | 50 | 15 | 9 | 2 / 2 |
| Cancer Immunology (Winship) | Translational research centre | 69 | 37 | 4 | 28 | 0 | 15 | 2 / 4 |
| Otolaryngology (SOM) | Clinical | 63 | 1 | 0 | 53 | 9 | 11 | 2 / 2 |
| Neurosurgery (SOM) | Clinical | 63 | 9 | 6 | 44 | 4 | 14 | 7 / 8 |
| GENI (CHOA) | Translational research centre | 62 | 21 | 1 | 32 | 8 | 8 | 2 / 3 |
| CIAG (CHOA) | Translational research centre | 61 | 19 | 4 | 32 | 6 | 7 | 1 / 4 |
| Biostatistics & Bioinformatics (RSPH) | Quantitative | 60 | 0 | 2 | 47 | 11 | 8 | 3 / 5 |
| Cell Biology (SOM) | Basic science | 59 | 51 | 1 | 1 | 6 | 5 | 1 / 1 |
| CCIV (CHOA) | Translational research centre | 57 | 28 | 3 | 16 | 10 | 8 | 2 / 3 |
| SOM: Medicine: Primary Care (SOM) | Clinical | 56 | 2 | 1 | 29 | 24 | 9 | 2 / 2 |
| Marcus Autism Center (CHOA) | Behavioural & social science | 52 | 7 | 0 | 33 | 12 | 6 | 2 / 2 |
| Pharmacology & Chemical Biology (SOM) | Basic science | 51 | 40 | 1 | 1 | 9 | 4 | 2 / 2 |
| Emory Vaccine Center (Vaccine) | Basic science | 48 | 35 | 3 | 8 | 2 | 15 | 2 / 3 |
| Urology (SOM) | Clinical | 47 | 7 | 1 | 37 | 2 | 9 | 3 / 3 |
| Microbiology & Immunology (SOM) | Basic science | 46 | 42 | 0 | 1 | 3 | 5 | 3 / 3 |
| HeRO (CHOA) | Translational research centre | 43 | 13 | 1 | 16 | 13 | 9 | 1 / 3 |
| Biochemistry (SOM) | Basic science | 36 | 26 | 2 | 2 | 6 | 9 | 3 / 3 |
| Executive MPH (RSPH) | Public & population health | 30 | 1 | 0 | 22 | 7 | 3 | 1 / 1 |
| Biomedical Informatics (SOM) | Quantitative | 29 | 1 | 1 | 23 | 4 | 5 | 2 / 2 |
| PTC (CHOA) | Engineering | 27 | 9 | 1 | 13 | 4 | 9 | 3 / 4 |
| Psychology (ECAS) | Behavioural & social science | 26 | 5 | 2 | 19 | 0 | 7 | 0 / 1 |
| Biology (ECAS) | Basic science | 24 | 18 | 1 | 1 | 4 | 1 | 0 / 1 |
| Human Health (ECAS) | Behavioural & social science | 20 | 4 | 0 | 11 | 5 | 3 | 1 / 1 |
| CVC (CHOA) | Translational research centre | 19 | 14 | 1 | 0 | 4 | 5 | 2 / 3 |
| Chemistry (ECAS) | Basic science | 17 | 16 | 0 | 0 | 1 | 2 | - |
| Cardiology (ECCRI) | Clinical | 16 | 0 | 0 | 14 | 2 | 1 | - |
| Microbiology & Immunology (EPC) | Basic science | 15 | 14 | 0 | 1 | 0 | 5 | 1 / 2 |
| Emory Center for AIDS Research (Vaccine) | Basic science | 13 | 10 | 0 | 3 | 0 | 6 | 1 / 1 |
| Neuropharmacology (EPC) | Basic science | 10 | 8 | 1 | 0 | 1 | 3 | 0 / 1 |
| Sociology (ECAS) | Behavioural & social science | 10 | 0 | 0 | 9 | 1 | 1 | - |
| Physiology (SOM) | Basic science | 9 | 5 | 0 | 1 | 3 | 1 | - |
| Developmental & Cognitive Neuroscience (EPC) | Translational research centre | 9 | 6 | 2 | 1 | 0 | 2 | - |
| Emory National Primate Research Center (EPC) | Basic science | 8 | 8 | 0 | 0 | 0 | 2 | 1 / 1 |
| Behavioral Neuroscience & Psychiatric Disord… (EPC) | Basic science | 8 | 7 | 0 | 0 | 1 | 0 | - |
| Data & Decision Sciences (ECAS) | Quantitative | 7 | 0 | 0 | 5 | 2 | 0 | - |
| Affiliate Faculty, Emory Vaccine Center (Vaccine) | Basic science | 6 | 3 | 0 | 3 | 0 | 3 | - |
| Animal Resources (EPC) | Basic science | 6 | 6 | 0 | 0 | 0 | 0 | - |
| SOM: Surgery: Pediatrics (SOM) | Clinical | 5 | 0 | 0 | 5 | 0 | 1 | - |
| Georgia Solve Sickle Cell Initiative (CHOA) | Clinical | 5 | 3 | 0 | 0 | 2 | 1 | - |
| Environmental Science (ECAS) | Public & population health | 5 | 0 | 0 | 3 | 2 | 1 | - |
| Georgia Research Alliance (Vaccine) | Basic science | 4 | 4 | 0 | 0 | 0 | 1 | - |
| SOMPI: Pallative Care (SOM) | Clinical | 4 | 0 | 2 | 1 | 1 | 1 | - |
| EVPHA (SOM) | Administrative | 4 | 2 | 0 | 2 | 0 | 1 | - |
| Office of Medical Education & Student Affairs (SOM) | Administrative | 3 | 0 | 0 | 3 | 0 | 2 | 2 / 2 |
| Marcus Center for Cellular Therapy (CHOA) | Translational research centre | 3 | 2 | 0 | 0 | 1 | 1 | - |
| Microbiology & Immunology (Vaccine) | Basic science | 2 | 2 | 0 | 0 | 0 | 0 | - |
| Biochemistry (Vaccine) | Basic science | 2 | 1 | 1 | 0 | 0 | 0 | - |
| Medical School Administration (SOM) | Administrative | 2 | 0 | 0 | 1 | 1 | 0 | - |
| Emory National Primate Research Center (SOM) | Basic science | 2 | 2 | 0 | 0 | 0 | 0 | - |
| Pathology & Lab Medicine (Vaccine) | Basic science | 2 | 2 | 0 | 0 | 0 | 1 | 1 / 1 |
| Emory National Primate Research Center (Vaccine) | Basic science | 2 | 2 | 0 | 0 | 0 | 0 | - |
| Cardiology, Epidemiology (ECCRI) | Public & population health | 2 | 0 | 0 | 0 | 2 | 0 | - |
| Neuroscience & Behavioral Biology (ECAS) | Basic science | 2 | 1 | 0 | 1 | 0 | 1 | 1 / 1 |
| Pathology (EPC) | Basic science | 2 | 2 | 0 | 0 | 0 | 0 | - |
| SOM: Peds: General (SOM) | Clinical | 1 | 0 | 0 | 1 | 0 | 0 | - |
| Ethics Center (SOM) | Administrative | 1 | 0 | 0 | 1 | 0 | 0 | - |
| Leadership (SOM) | Administrative | 1 | 0 | 0 | 1 | 0 | 0 | - |
| of Microbiology & Immunology (Vaccine) | Basic science | 1 | 1 | 0 | 0 | 0 | 0 | - |
| EVP Health Affairs (SOM) | Administrative | 1 | 0 | 0 | 0 | 1 | 0 | - |
| CEPAR (SOM) | Administrative | 1 | 0 | 0 | 1 | 0 | 0 | - |
| Pediatrics (Vaccine) | Translational research centre | 1 | 1 | 0 | 0 | 0 | 0 | - |
| Academics (SOM) | Administrative | 1 | 1 | 0 | 0 | 0 | 1 | - |
| Georgia Research Alliance Eminent Scholar in… (Vaccine) | Basic science | 1 | 1 | 0 | 0 | 0 | 1 | - |
| SOMPI: DOP Pediatrics Admin (SOM) | Clinical | 1 | 0 | 0 | 1 | 0 | 1 | - |
| Radiology (SOM) | Clinical | 1 | 0 | 0 | 0 | 1 | 0 | - |
| Microbiology Immunology (SOM) | Basic science | 1 | 1 | 0 | 0 | 0 | 0 | - |
| School of Medicine (SOM) | Administrative | 1 | 0 | 0 | 1 | 0 | 0 | - |
| Global Health & Epidemiology (Vaccine) | Public & population health | 1 | 0 | 0 | 1 | 0 | 0 | - |
| Physics (Biophysics) (ECAS) | Basic science | 1 | 1 | 0 | 0 | 0 | 1 | - |
| NHP (Vaccine) | Basic science | 1 | 1 | 0 | 0 | 0 | 1 | 0 / 1 |
| CFAR (Vaccine) | Basic science | 1 | 1 | 0 | 0 | 0 | 1 | 0 / 1 |
| EPC Director / Microbiology & Immunology (EPC) | Basic science | 1 | 1 | 0 | 0 | 0 | 0 | - |
| Pathology Advanced Translational Unit (Vaccine) | Basic science | 1 | 1 | 0 | 0 | 0 | 1 | 1 / 1 |
| Biostatistics & Bioinformatics (ECCRI) | Quantitative | 1 | 0 | 0 | 1 | 0 | 0 | - |
