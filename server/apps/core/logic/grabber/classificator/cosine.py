import os

from django.conf import settings
import joblib
import pandas as pd
import torch
from transformers import BertForSequenceClassification, AutoTokenizer
import argparse
import logging
import tqdm

DATA_DIR = os.path.join(settings.BASE_DIR, 'server', 'apps',
                        'core', 'logic', 'grabber', 'classificator', 'data')


def rate(normalized_text):
    modelname = 'atiwar_fired'
    tokenizer = AutoTokenizer.from_pretrained(os.path.join(DATA_DIR, modelname), use_fast=False)

    model = BertForSequenceClassification.from_pretrained(os.path.join(DATA_DIR, modelname))
    model.eval()

    encoding = tokenizer(
        normalized_text,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=256,
    )
    input_ids = encoding["input_ids"]
    dataset = torch.utils.data.TensorDataset(
        input_ids,)
    model_iter = torch.utils.data.DataLoader(dataset, batch_size=1, shuffle=False)
    for text in tqdm.tqdm(model_iter):
        outputs = model(text[0])
        predictions = outputs.logits
    return predictions[0][1].item()- predictions[0][0].item()

