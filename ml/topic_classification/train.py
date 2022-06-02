import json

import pandas as pd

from config import TopicClassificationConfig
from ml.topic_classification import NewsClassificationDataModule, NewsClassificationModule
from pytorch_lightning import seed_everything, Trainer

if __name__ == "__main__":
    config = TopicClassificationConfig()
    seed_everything(7)

    data = []
    with open("data/News_Category_Dataset_v2.json", encoding="utf-8") as json_lines_file:
        for line in json_lines_file:
            data.append(json.loads(line))

    df = pd.DataFrame(data).sample(frac=1.0)

    cat_map = {vi: k for k, v in config.main_categories.items() for vi in v}
    df["category"] = df["category"].map(cat_map)
    df = df.loc[df["category"].isin(config.main_categories)]

    df["text"] = df["headline"].str.strip() + ". " + df["short_description"].str.strip()
    df = df[["text", "category"]]

    datamodule = NewsClassificationDataModule(df, model_name=config.model_name)
    model = NewsClassificationModule(num_classes=len(config.classes), model_name=config.model_name)

    trainer = Trainer(max_epochs=5, accelerator="cpu")
    trainer.fit(model, datamodule=datamodule)
