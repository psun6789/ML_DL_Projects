import os
import yaml
from pathlib import Path
from ImageClassification.utils.common import read_yaml, create_directories
from ImageClassification.constants import CONFIG_FILE_PATH, PARAMS_FILE_PATH
from ImageClassification.entity.config_entity import DataIngestionConfig
from ImageClassification.entity.config_entity import PrepareBaseModelConfig
from ImageClassification.entity.config_entity import PrepareCallbacksConfig
from ImageClassification.entity.config_entity import TrainingConfig
from ImageClassification.entity.config_entity import EvaluationConfig

class ConfigurationManager:
    def __init__(self,
        config_filepath: Path = CONFIG_FILE_PATH,
        params_filepath: Path = PARAMS_FILE_PATH):

        self.config_filepath = config_filepath  # Store config filepath as attribute
        self.params_filepath = params_filepath

        self.config = read_yaml(config_filepath)
        self.params = read_yaml(params_filepath)

        create_directories([self.config.artifacts_root])

    def get_data_ingestion_config(self) -> DataIngestionConfig:
        with open(self.config_filepath, 'r') as file:
            self.config = yaml.safe_load(file)

        data_root_path = Path(self.config['data_root_path'])
        data_ingestion = self.config['data_ingestion']

        return DataIngestionConfig(
        root_dir=Path(data_ingestion['root_dir']),
        train_dir=data_root_path / data_ingestion['train_dir'],
        validation_dir=data_root_path / data_ingestion['validation_dir'],
        test_dir=data_root_path / data_ingestion['test_dir'],
        source_URL=data_ingestion['source_URL'],
        local_data_file=data_root_path / data_ingestion['local_data_file'],
        unzip_dir=data_root_path / data_ingestion['unzip_dir']
        )

    def get_prepare_base_model_config(self) -> PrepareBaseModelConfig:
        config = self.config.prepare_base_model

        create_directories([config.root_dir])

        prepare_base_model_config = PrepareBaseModelConfig(
            root_dir=Path(config.root_dir),
            base_model_path=Path(config.base_model_path),
            update_base_model_path=Path(config.update_base_model_path),
            params_image_size = self.params.IMAGE_SIZE,
            params_learning_rate = self.params.LEARNING_RATE,
            params_include_top = self.params.INCLUDE_TOP,
            params_weights = self.params.WEIGHTS,
            params_classes = self.params['CLASSES']
        )
        return prepare_base_model_config
    
    def get_prepare_callback_config(self) -> PrepareCallbacksConfig:
        config = self.config.perpare_callbacks

        model_ckpt_dir = os.path.dirname(config.checkpoint_model_filepath)
        create_directories([
            Path(model_ckpt_dir),
            Path(config.tensorboard_root_log_dir)
        ])

        prepare_callback_config = PrepareCallbacksConfig(
            root_dir=Path(config.root_dir),
            tensorboard_root_log_dir=(config.tensorboard_root_log_dir),
            checkpoint_model_filepath=(config.checkpoint_model_filepath)
        )

        return prepare_callback_config


    def get_training_config(self) -> TrainingConfig:
        training = self.config.training
        prepare_base_model = self.config.prepare_base_model
        params = self.params
        training_data = os.path.join(self.config.data_ingestion.unzip_dir, 'chicken-fecal-images')
        create_directories([Path(training.root_dir)])

        training_config = TrainingConfig(
            root_dir = Path(training.root_dir),
            trained_model_path = Path(training.trained_model_path),
            updated_base_model_path = Path(prepare_base_model.update_base_model_path),
            training_data = Path(training_data),
            params_epochs = params.EPOCHS,
            params_batch_size = params.BATCH_SIZE,
            params_is_augmentation = params.AUGMENTATION,
            params_image_size = params.IMAGE_SIZE
            )
        return training_config
    
    def get_validation_config(self) -> EvaluationConfig:
        eval_config = EvaluationConfig(
            path_of_model="artifacts/training/model.keras",
            training_data="artifacts/data_ingestion/Chicken-fecal-images",
            all_params=self.params,
            params_image_size=self.params.IMAGE_SIZE,
            params_batch_size=self.params.BATCH_SIZE
        )
        return eval_config