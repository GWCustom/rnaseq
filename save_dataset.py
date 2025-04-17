import pandas as pd
import bfabric_web_apps
import io

csv_data = """
sample,fastq_1,fastq_2,strandedness
Run_1913_10,/STORAGE/OUTPUT_TEST/200611_A00789R_0071_BHHVCCDRXX/L001/37767/894884/Run_1913_10_S3_L001_R1_001.fastq.gz,/STORAGE/OUTPUT_TEST/200611_A00789R_0071_BHHVCCDRXX/L001/37767/894884/Run_1913_10_S3_L001_R2_001.fastq.gz,auto
Run_1913_4,/STORAGE/OUTPUT_TEST/200611_A00789R_0071_BHHVCCDRXX/L001/37767/894878/Run_1913_4_S9_L001_R1_001.fastq.gz,/STORAGE/OUTPUT_TEST/200611_A00789R_0071_BHHVCCDRXX/L001/37767/894878/Run_1913_4_S9_L001_R2_001.fastq.gz,auto
Run_1913_10,/STORAGE/OUTPUT_TEST/200611_A00789R_0071_BHHVCCDRXX/L002/37767/894884/Run_1913_10_S3_L002_R1_001.fastq.gz,/STORAGE/OUTPUT_TEST/200611_A00789R_0071_BHHVCCDRXX/L002/37767/894884/Run_1913_10_S3_L002_R2_001.fastq.gz,auto
Run_1913_4,/STORAGE/OUTPUT_TEST/200611_A00789R_0071_BHHVCCDRXX/L002/37767/894878/Run_1913_4_S9_L002_R1_001.fastq.gz,/STORAGE/OUTPUT_TEST/200611_A00789R_0071_BHHVCCDRXX/L002/37767/894878/Run_1913_4_S9_L002_R2_001.fastq.gz,auto
Run_1913_11,/STORAGE/OUTPUT_TEST/200611_A00789R_0071_BHHVCCDRXX/L001/37767/894885/Run_1913_11_S2_L001_R1_001.fastq.gz,/STORAGE/OUTPUT_TEST/200611_A00789R_0071_BHHVCCDRXX/L001/37767/894885/Run_1913_11_S2_L001_R2_001.fastq.gz,auto
Run_1913_11,/STORAGE/OUTPUT_TEST/200611_A00789R_0071_BHHVCCDRXX/L002/37767/894885/Run_1913_11_S2_L002_R1_001.fastq.gz,/STORAGE/OUTPUT_TEST/200611_A00789R_0071_BHHVCCDRXX/L002/37767/894885/Run_1913_11_S2_L002_R2_001.fastq.gz,auto
"""

df = pd.read_csv(io.StringIO(csv_data.strip()))

wrapper = bfabric_web_apps.get_power_user_wrapper({"environment": "test"})

attributes = [
    {"name": "Sample", "position": "1", "type": "String"},
    {"name": "FASTQ Read 1", "position": "2", "type": "Resource"},
    {"name": "FASTQ Read 2", "position": "3", "type": "Resource"},
    {"name": "Strandedness", "position": "4", "type": "String"},
]

items = []
for idx, row in df.iterrows():
    fields = [
        {"attributeposition": "1", "value": row["sample"]},
        {"attributeposition": "2", "value": row["fastq_1"]},
        {"attributeposition": "3", "value": row["fastq_2"]},
        {"attributeposition": "4", "value": row["strandedness"]},
    ]
    items.append({"field": fields, "position": str(idx + 1)})

dataset_data = {
    "name": "Uploaded FASTQ Dataset (Run 1913)",
    "attribute": attributes,
    "item": items,
    "id": 2220
}

response = wrapper.save("dataset", dataset_data)
print("Upload erfolgreich:", response)


