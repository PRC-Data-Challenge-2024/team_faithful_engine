import os
from pathlib import Path
from typing import List
import warnings

import pandas as pd
from utils.data_loader import DataLoader

from preprocessing.base_preprocessor import BasePreprocessor
from preprocessing.clean_dataset import CleanDatasetPreprocessor
from preprocessing.aircraft_performance import AircraftPerformancePreprocessor
from preprocessing.fuel_price_preprocessor import FuelPricePreprocessor
from preprocessing.runway import RunwayInfoPreprocessor
from preprocessing.pax_flow_preprocessor import PaxFlowPreprocessor
from preprocessing.weather import WeatherDataPreprocessor
from preprocessing.derived_features import DerivedFeaturePreprocessor
from preprocessing.airport_preprocessor import AirportPreprocessor
from preprocessing.trajectory_preprocessor import TrajectoryPreprocessor
from preprocessing.weather_safety_features import WeatherSafetyFeatures

# from preprocessing.payload_prediction_preprocessor import PayloadPredictionPreprocessor
from preprocessing.feature_engineering import FeatureEngineeringPreprocessor
from preprocessing.creative_feature_engineering import CreativeWeightPreprocessor
from preprocessing.openap_fuelflow import OpenAPFuelFlowPreprocessor
from preprocessing.aircraft_performance_openap import (
    OpenAPAircraftPerformancePreprocessor,
)

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

PREPROCESSORS: List[BasePreprocessor] = [
    AirportPreprocessor(),
    OpenAPAircraftPerformancePreprocessor(),
    AircraftPerformancePreprocessor(),
    FuelPricePreprocessor(),
    RunwayInfoPreprocessor(),
    PaxFlowPreprocessor(),
    WeatherDataPreprocessor(),
    WeatherSafetyFeatures(),
    DerivedFeaturePreprocessor(),
    TrajectoryPreprocessor(),
    OpenAPFuelFlowPreprocessor(),
    FeatureEngineeringPreprocessor(),
    CreativeWeightPreprocessor(),
    CleanDatasetPreprocessor(),
]

model_config = {
    "time_limit": args.time,
    "preset": args.quality,
    "verbosity": 2,
}

evaluator = MetricEvals()
model = AutogluonModel(**model_config)
loader = DataLoader(Path("data"), num_days=0)


def train(dataset, final=False):
    for preprocessor in PREPROCESSORS:
        dataset = preprocessor.apply(dataset)

    train_percent = 1.0 if final else 0.9
    train_df, val_df = dataset.split(train_percent=train_percent, seed=0)
    print(f"\n\nTraining model {model.name}")
    model.train(train_df)

    if not final:
        predictions = model.predict(val_df)
        evaluator.evaluate_and_log(val_df.tow, predictions)

    wandb.log_model(output, name="model")
    model.log_feature_importance(train_df)
    return model


if __name__ == "__main__":
    wandb.init(project="flying_penguins")
    wandb.config["model_name"] = model.name
    wandb.config["model_config"] = model_config
    wandb.config["model_info"] = model.info()
    wandb.config["preprocessors"] = [p.__class__.__name__ for p in PREPROCESSORS]

    challenge, _, _ = loader.load()
    model = train(challenge)

    output = sorted(Path("AutogluonModels").glob("ag-*"), key=os.path.getmtime)[-1]
    wandb.log({"raw_model_info": model.info()})
    # wandb.log_model(output, name="model")

    print("Done with training.")
