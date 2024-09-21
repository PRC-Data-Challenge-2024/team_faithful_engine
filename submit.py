import wandb
from pathlib import Path
from autogluon.tabular import TabularDataset, TabularPredictor
from utils.data_loader import DataLoader
from run import PREPROCESSORS
import boto3
import json

SUBMIT_ARTIFCAT = "model:v0"

submission_dir = Path("submissions")
version = len(list(submission_dir.glob("*.csv")))

SECRETS_FILE = ".access_keys.json"
if not Path(SECRETS_FILE).exists():
    print(f"The file {SECRETS_FILE} does not exist.")
    print(f"Please paste the provided access keys into a file called {SECRETS_FILE}")
    exit()

access_keys = json.load(open(SECRETS_FILE, "r"))

# Create a session using your credentials
session = boto3.Session(
    aws_access_key_id=access_keys.get("bucket_access_key"),
    aws_secret_access_key=access_keys.get("bucket_access_secret"),
)


wandb.init(project="flying_penguins")
artifact = wandb.run.use_artifact(SUBMIT_ARTIFCAT)
model = TabularPredictor.load(artifact.download())

loader = DataLoader(Path("data"), num_days=0)
_, dataset, _ = loader.load()


for preprocessor in PREPROCESSORS:
    dataset = preprocessor.apply(dataset)

print("Starting prediction")
predictions = model.predict(TabularDataset(dataset.df))
result = dataset.df[["flight_id", "tow"]]
result["tow"] = predictions
result = result.set_index("flight_id")

print("Saving to file")
team = access_keys.get("team_name")
team_id = access_keys.get("team_id")
filename = f"{team}_v{version}_{team_id}.csv"

result.to_csv(submission_dir / filename)

print("Uploading")
# Create an S3 client with the appropriate configuration
s3_client = session.client("s3", endpoint_url="https://s3.opensky-network.org")

with open(submission_dir / filename, "rb") as data:
    s3_client.upload_fileobj(data, "submissions", filename)
print("Submitted the file.")