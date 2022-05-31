import pandas as pd
import torch

from config import TopicClassificationConfig
from ml.topic_classification import NewsClassificationDataModule, NewsClassificationModule
from pytorch_lightning import Trainer


def predict(stories, weights_path):
    config = TopicClassificationConfig()
    classes_to_ix = {cl: i for i, cl in enumerate(config.classes)}
    ix_to_classes = {i: cl for cl, i in classes_to_ix.items()}
    df = pd.DataFrame({"title": stories})

    datamodule = NewsClassificationDataModule(df, model_name=config.model_name)
    model = NewsClassificationModule.load_from_checkpoint(
        weights_path, num_classes=len(config.classes), model_name=config.model_name
    )

    trainer = Trainer()
    preds = trainer.predict(model, datamodule=datamodule, return_predictions=True)

    pred_classes = torch.cat([pred for pred in preds]).tolist()
    pred_classes = [ix_to_classes[pred] for pred in pred_classes]
    return pred_classes
