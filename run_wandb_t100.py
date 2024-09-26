import os
from pathlib import Path
from typing import List
import warnings

import pandas as pd
from utils.data_loader import DataLoader
from utils.dataset import Dataset
import numpy as np

from preprocessing.base_preprocessor import BasePreprocessor
from preprocessing.clean_dataset import CleanDatasetPreprocessor
from preprocessing.aircraft_performance import AircraftPerformancePreprocessor
from preprocessing.fuel_price_preprocessor import FuelPricePreprocessor
from preprocessing.runway import RunwayInfoPreprocessor
from preprocessing.pax_flow_preprocessor import PaxFlowPreprocessor
from preprocessing.weather import WeatherDataPreprocessor
from preprocessing.derived_features import DerivedFeaturePreprocessor
from preprocessing.airport_preprocessor import AirportPreprocessor

from models.autogluon_model import AutogluonModel
from evals.metrics import MetricEvals
import argparse
import wandb

pd.set_option("future.no_silent_downcasting", True)
warnings.filterwarnings(action="ignore", message="Mean of empty slice")

parser = argparse.ArgumentParser()
parser.add_argument(
    "--quality", type=str, help="Quality Preset", default="best_quality"
)
parser.add_argument("--time", type=int, help="Time Limit (s)", default=300)
args = parser.parse_args()

PREPROCESSORS: List[BasePreprocessor] = []

model_config = {
    "time_limit": args.time,
    "preset": args.quality,
    "verbosity": 2,
}

evaluator = MetricEvals()
model = AutogluonModel(**model_config)


def train(dataset):
    for preprocessor in PREPROCESSORS:
        dataset = preprocessor.apply(dataset)

    train_df, val_df = dataset.split(train_percent=0.8, seed=0)
    print(f"\n\nTraining model {model.name}")
    model.train(train_df)
    predictions = model.predict(val_df)
    evaluator.log_evaluation(val_df.tow, predictions)

    model.log_feature_importance(train_df)
    return model


if __name__ == "__main__":
    wandb.init(project="flying_penguins")
    wandb.config["model_name"] = model.name
    wandb.config["model_config"] = model_config
    wandb.config["model_info"] = model.info()
    wandb.config["preprocessors"] = [p.__class__.__name__ for p in PREPROCESSORS]

    df = pd.read_csv("/home/wues_ni/Projects/ATOW-Prediction/notebooks/A320_T100.csv")
    df["aircraft_type"] = "A320"
    df["flight_id"] = np.arange(len(df))
    df.rename(columns={"PAYLOAD_PER_DEPARTURE": "tow"}, inplace=True)
    dataset = Dataset(df.reset_index(drop=True), name="T100")
    model = train(dataset)

    output = sorted(Path("AutogluonModels").glob("ag-*"), key=os.path.getmtime)[-1]
    wandb.log({"raw_model_info": model.info()})
    wandb.log_model(output, name="model")

    print("Done with training.")
