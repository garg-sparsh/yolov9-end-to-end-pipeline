import json

import mlflow
import tempfile
import os
import wandb
import hydra
from omegaconf import DictConfig

_steps = [
    "download",
    "inference",
    "data",
    "validation",
    "yolov9",
    # NOTE: We do not include this in the steps so it is not run by mistake.
    # You first need to promote a model export to "prod" before you can run this,
    # then you need to run this step explicitly
#    "test_regression_model"
]


# This automatically reads in the configuration
@hydra.main(config_name='config')
def go(config: DictConfig):

    # Setup the wandb experiment. All runs will be grouped under this name
    os.environ["WANDB_PROJECT"] = "YOLO_v9"
    os.environ["WANDB_RUN_GROUP"] = "devlopment"

    # Steps to execute
    steps_par = config['main']['steps']
    active_steps = steps_par.split(",") if steps_par != "all" else _steps

    # Move to a temporary directory
    with tempfile.TemporaryDirectory() as tmp_dir:

        if "yolov9" in active_steps:
            # Download file and load in W&B
            _ = mlflow.run(
                os.path.join(hydra.utils.get_original_cwd(), "src", "yolov9"),
                "main",
                version='main',
                parameters={
                    "workers": 8,
                    "device": 0,
                    "name": "yolov9-c",
                    "epochs" : 1,
                    "output_artifact": "yolov9_training"
                },
            )
        if "validation" in active_steps:
            # Download file and load in W&B
            _ = mlflow.run(
                os.path.join(hydra.utils.get_original_cwd(), "src", "validation"),
                "main",
                version='main',
                parameters={
                    "batch-size": 32,
                    "device": 0,
                    "weights": "yolov9-c",
                    "name" : "yolov9_c_640_val",
                    "input_artifact": "yolov9_training:latest"
                },
            )

        if "inference" in active_steps:
            # Download file and load in W&B
            _ = mlflow.run(
                os.path.join(hydra.utils.get_original_cwd(), "src", "inference"),
                "main",
                version='main',
            )

        
        # if "basic_cleaning" in active_steps:
        #     _ = mlflow.run(
        #         os.path.join(hydra.utils.get_original_cwd(), "src", "basic_cleaning"),
        #         "main",
        #         parameters={
        #             "input_artifact": "sample.csv:latest",
        #             "output_artifact": "clean_sample.csv",
        #             "output_type": "clean_sample",
        #             "output_description": "Data with outliers and null values removed",
        #             "min_price": config['etl']['min_price'],
        #             "max_price": config['etl']['max_price']
        #         },
        #     )

        # if "data_check" in active_steps:
        #     ##################
        #     # Implement here #
        #     ##################
        #     _ = mlflow.run(
        #         os.path.join(hydra.utils.get_original_cwd(), "src", "data_check"),
        #         "main",
        #         parameters={
        #             "csv": "clean_sample.csv:latest",
        #             "ref": "clean_sample.csv:reference",
        #             "kl_threshold": config['data_check']['kl_threshold'],
        #             "min_price": config['etl']['min_price'],
        #             "max_price": config['etl']['max_price']
        #         },
        #     )

        # if "data_split" in active_steps:
        #     ##################
        #     # Implement here #
        #     ##################
        #     _ = mlflow.run(
        #         os.path.join(hydra.utils.get_original_cwd(), "components", "data_split"),
        #         "main",
        #         parameters={
        #             "input": "clean_sample.csv:latest",
        #             "test_size": config['modeling']['test_size'],
        #             "stratify_by": config['modeling']['stratify_by'],
        #         },
        #     )

        # if "train_random_forest" in active_steps:

        #     # NOTE: we need to serialize the random forest configuration into JSON
        #     rf_config = os.path.abspath("rf_config.json")
        #     with open(rf_config, "w+") as fp:
        #         json.dump(dict(config["modeling"]["random_forest"].items()), fp)  # DO NOT TOUCH

        #     # NOTE: use the rf_config we just created as the rf_config parameter for the train_random_forest
        #     # step

        #     ##################
        #     # Implement here #
        #     ##################

        #     _ = mlflow.run(
        #         os.path.join(hydra.utils.get_original_cwd(), "src", "train_random_forest"),
        #         "main",
        #         parameters={
        #             "trainval_artifact": "trainval_data.csv:latest",
        #             "val_size": config['modeling']['val_size'],
        #             "random_seed": config['modeling']['random_seed'],
        #             "stratify_by": config['modeling']['stratify_by'],
        #             "rf_config":rf_config,
        #             "max_tfidf_features": config['modeling']['max_tfidf_features'],
        #             "output_artifact":"randomForest_model"
        #         },
        #     )

        # if "test_regression_model" in active_steps:

        #     ##################
        #     # Implement here #
        #     ##################

        #     _ = mlflow.run(
        #         os.path.join(hydra.utils.get_original_cwd(), "components", "test_regression_model"),
        #         "main",
        #         parameters={
        #             "mlflow_model": "randomForest_model:prod",
        #             "test_dataset":"test_data.csv:latest"
        #         },
        #     )


if __name__ == "__main__":
    go()