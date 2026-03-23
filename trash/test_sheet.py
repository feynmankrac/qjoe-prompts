from sheet_client import get_jobs_to_process


SPREADSHEET_ID = "10DSDAsJpXWmdpafk-MlG_FXA-5-idxnlzuWLY83G7Kk"

jobs = get_jobs_to_process(SPREADSHEET_ID)

print(len(jobs))
print(jobs[:3])