# Bachelor Thesis

**Yvan Richard**

University of St. Gallen, Spring Term 2026

## Presentation

This repository is an aggregate of the code and notebooks I used to produce the empirical findings presented in my bachelor thesis at the University of St. Gallen. The bachelor thesis was submitted on May 19, 2026.

## Structure of the Repository

The repository is organized as follows:

```txt
.
├── README.md              # Overview of the repository
├── .gitignore             # Files and folders excluded from version control
├── notebooks/             # Notebooks used to produce the empirical findings
|   ├── CRSP/
|   ├── CRSP_RH/
|   ├── Fama_French/
|   ├── RavenPack/
|   ├── Robintrack/
|   ├── TAQ/
|   └── main/
├── src/                   # Reusable Python source code
|   ├── cleaning/
|   ├── computing/
|   ├── google_trends/
|   └── merging/
└── thesis/                # PDF of the final version
```

The `notebooks/` directory contains the main empirical workflows used for data cleaning, variable construction, estimation, and visualization. The `src/` directory contains reusable functions and scripts that support these workflows. Other directories are not directly relevant.
