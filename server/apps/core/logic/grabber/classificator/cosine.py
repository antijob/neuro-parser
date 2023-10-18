import os
import tqdm

from django.conf import settings

import torch
from transformers import BertForSequenceClassification, AutoTokenizer


DATA_DIR = os.path.join(settings.BASE_DIR, 'server', 'apps',
                        'core', 'logic', 'grabber', 'classificator', 'data')


def rate(normalized_text):
    modelname = 'atiwar_fired'
    tokenizer = AutoTokenizer.from_pretrained(
        os.path.join(DATA_DIR, modelname), use_fast=False)

    model = BertForSequenceClassification.from_pretrained(
        os.path.join(DATA_DIR, modelname))
    model.eval()

    return rate_with_model_and_tokenizer(normalized_text, model, tokenizer)


def rate_with_model_and_tokenizer(normalized_text, model, tokenizer):
    encoding = tokenizer(
        normalized_text,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=256,
    )
    input_ids = encoding["input_ids"]
    dataset = torch.utils.data.TensorDataset(input_ids,)
    model_iter = torch.utils.data.DataLoader(
        dataset, batch_size=1, shuffle=False)

    predictions_pos = 0
    predictions_neg = 0
    for text in tqdm.tqdm(model_iter):
        outputs = model(text[0])
        predictions_pos += outputs.logits[0][1].item()
        predictions_neg += outputs.logits[0][0].item()
    return [predictions_neg, predictions_pos]
