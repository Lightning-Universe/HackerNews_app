from torch import nn, optim
from torchmetrics import Accuracy
from transformers import AutoModelForSequenceClassification

from pytorch_lightning import LightningModule

MAIN_CATEGORIES = {
    "Education": ["EDUCATION", "COLLEGE"],
    "Business": ["BUSINESS", "MONEY"],
    "Sports": ["SPORTS"],
    "Technology": ["TECH", "SCIENCE"],
    "News and Politics": [
        "POLITICS",
        "BLACK VOICES",
        "QUEER VOICES",
        "LATINO VOICES",
        "WOMEN",
        "IMPACT",
        "RELIGION",
        "CRIME",
        "GOOD NEWS",
        "MEDIA",
        "WEIRD NEWS",
        "WORLD NEWS",
        "THE WORLDPOST",
        "WORLDPOST",
    ],
    "Lifestyle": [
        "WELLNESS",
        "TRAVEL",
        "STYLE & BEAUTY",
        "PARENTING",
        "HEALTHY LIVING",
        "FOOD & DRINK",
        "HOME & LIVING",
        "ENVIRONMENT",
        "PARENTS",
        "STYLE",
        "TASTE",
        "GREEN",
        "FIFTY",
    ],
    "Culture and Arts": ["ARTS & CULTURE", "CULTURE & ARTS", "WEDDINGS", "DIVORCE", "ARTS"],
    "Entertainment": ["ENTERTAINMENT", "COMEDY"],
}

CLASSES = [
    "Education",
    "Business",
    "Sports",
    "Technology",
    "News and Politics",
    "Lifestyle",
    "Culture and Arts",
    "Entertainment",
]
CLASSES_TO_IX = {cl: i for i, cl in enumerate(CLASSES)}
IX_TO_CLASSES = {i: cl for cl, i in CLASSES_TO_IX.items()}
MODEL_NAME = "distilbert-base-uncased"


class NewsClassificationModule(LightningModule):
    def __init__(self, num_classes, model_name):
        super().__init__()

        # TODO: Fix this to not download the pre-trained backbone (@rohitgr7)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=num_classes)

        self.train_acc = Accuracy()
        self.val_acc = Accuracy()
        self.loss_fn = nn.CrossEntropyLoss()

    def forward(self, x):
        return self.model(input_ids=x["input_ids"], attention_mask=x["attention_mask"]).logits.argmax(dim=1)

    def training_step(self, batch, batch_idx):
        logits = self.model(input_ids=batch["input_ids"], attention_mask=batch["attention_mask"]).logits
        targets = batch["target"]
        loss = self.loss_fn(logits, targets)
        self.train_acc(logits, targets)
        self.log("train_acc", self.train_acc, prog_bar=True)
        return loss

    def validation_step(self, batch, batch_idx):
        logits = self.model(input_ids=batch["input_ids"], attention_mask=batch["attention_mask"]).logits
        targets = batch["target"]
        loss = self.loss_fn(logits, targets)
        self.val_acc.update(logits, targets)
        self.log("val_loss", loss, prog_bar=True)
        self.log("val_acc", self.val_acc, prog_bar=True)

    def configure_optimizers(self):
        opt = optim.AdamW(self.parameters(), lr=2e-5, weight_decay=1e-2)
        return {"optimizer": opt}
