import logging
import tqdm
import torch
from server.libs.morphy import normalize_text

from server.apps.core.models import IncidentType, Article


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Code use llama model for text classification.
# Text summarization for economy price.
# Main llama_promt use in system pront for priority.

# TODO: convert to async


def predict_is_incident_bert(incident: IncidentType,  article: Article, model, tokenizer) -> bool:

    # Normalize text
    normalized_text = normalize_text(article.text)

    try:
        encoding = tokenizer(
            normalized_text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=256,
        )
        input_ids = encoding["input_ids"]
        dataset = torch.utils.data.TensorDataset(
            input_ids,
        )
        model_iter = torch.utils.data.DataLoader(
            dataset, batch_size=1, shuffle=False)

        predictions_pos = 0.0
        predictions_neg = 0.0
        for text in tqdm.tqdm(model_iter):
            outputs = model(text[0])
            predictions_pos += outputs.logits[0][1].item()
            predictions_neg += outputs.logits[0][0].item()

        logits = torch.tensor([predictions_neg, predictions_pos])
        probabilities = torch.nn.functional.softmax(logits, dim=0).tolist()

        # save rate
        article.rate[incident.current_incident_type.description] = probabilities
        article.save()

        return probabilities[0] - probabilities[1] > incident.current_incident_type.treshold
    except Exception as e:
        logger.error(f"Error in predict_is_incident_bert: {e}")
        return False  # Default value if an error occurs
