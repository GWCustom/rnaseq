import pandas as pd

def create_sample_sheet_csv(dataset=None):
    """
    Create a samplesheet CSV file required for nf-core/rnaseq.

    Assumes dataset is a dictionary containing:
    - 'Name' for sample names
    - 'Read1' for R1 FASTQ file paths
    - 'Read2' for R2 FASTQ file paths

    Output:
        Creates './samplesheet.csv' in the current directory
    """

    # Fallback if no dataset provided (e.g., during standalone testing)
    if dataset is None:
        raise ValueError("No dataset provided to create_sample_sheet_csv().")

    try:
        df = pd.DataFrame(dataset)

        # Ensure necessary columns exist
        for col in ["Sample", "FASTQ Read 1", "FASTQ Read 2"]:
            if col not in df.columns:
                raise KeyError(f"Missing required column in dataset: {col}")


        df["fastq_1"] = df["FASTQ Read 1"]
        df["fastq_2"] = df["FASTQ Read 2"]
        df["sample"] = df["Sample"]
        df["strandedness"] = "auto"

        # Final samplesheet
        samplesheet_df = df[["sample", "fastq_1", "fastq_2", "strandedness"]]

        # Save to CSV
        samplesheet_df.to_csv("./samplesheet.csv", index=False)

        print("samplesheet.csv created successfully.")

    except Exception as e:
        print(f"Error while creating samplesheet: {e}")
