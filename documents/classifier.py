# 📄 Document Classification Module (Training & Prediction)

from __future__ import annotations

import os
import logging
from typing import Tuple, List

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

from documents.ocr import extract_text_from_image


# 🛠️ Logger Setup
logger = logging.getLogger(__name__)


# 📂 Load Documents from Folder Structure
def load_documents_from_folders(base_path: str = "docs-sm") -> Tuple[List[str], List[str]]:
    """
    📥 Load documents for training.
    
    Each subfolder represents a document label. Supported files: PNG, JPG, JPEG.

    Args:
        base_path (str): Path to the dataset folder.

    Returns:
        texts (list): Extracted document texts.
        labels (list): Corresponding labels (from folder names).
    """
    texts, labels = [], []

    logger.info(f"📂 Scanning documents in {base_path}...")

    if not os.path.exists(base_path):
        logger.error(f"❌ Base path not found: {base_path}")
        return texts, labels

    for label in os.listdir(base_path):
        label_path = os.path.join(base_path, label)
        if not os.path.isdir(label_path):
            logger.warning(f"⚠️ Skipping non-folder: {label_path}")
            continue

        logger.info(f"🏷️ Found label folder: {label}")

        for file in os.listdir(label_path):
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                full_path = os.path.join(label_path, file)
                try:
                    text = extract_text_from_image(full_path, cache_dir="/app/ocr-cache")
                    texts.append(text)
                    labels.append(label)
                    logger.info(f"📄 Processed: {file}")
                except Exception as e:
                    logger.error(f"❌ Skipping {full_path}: {e}", exc_info=True)
            else:
                logger.debug(f"🔍 Skipping non-image file: {file}")

    logger.info(f"✅ Loaded {len(texts)} documents across {len(set(labels))} labels.")
    return texts, labels


# 🤖 Train Classifier & Save Model
def train_and_save_model(output_path: str = "model.joblib") -> None:
    """
    🏋️ Train a document classification model and save it to disk.
    
    Args:
        output_path (str): Destination file for saving the trained model.
    """
    texts, labels = load_documents_from_folders()

    if not texts or not labels:
        logger.error("❌ No data to train on. Check your '/docs-sm' directory and file formats.")
        return

    logger.info("✂️ Splitting data for training/testing...")
    X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=42)

    # 📊 ML Pipeline: TF-IDF + Logistic Regression
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(max_features=5000)),
        ('clf', LogisticRegression(max_iter=1000)),
    ])

    logger.info("🤖 Training document classifier...")
    pipeline.fit(X_train, y_train)

    logger.info("📊 Evaluating model...")
    predictions = pipeline.predict(X_test)
    report = classification_report(y_test, predictions)
    logger.info(f"\n📋 Classification Report:\n{report}")

    joblib.dump(pipeline, output_path)
    logger.info(f"💾 Model saved to: {output_path}")
    logger.info("✅ Model training complete.")


# 🔮 Predict Document Type
def predict_document_type(text: str, model_path: str = "model.joblib") -> str:
    """
    🔮 Predict the type of a document using the trained model.

    Args:
        text (str): Raw document text.
        model_path (str): Path to the saved model.

    Returns:
        str: Predicted document type (label).
    """
    if not os.path.exists(model_path):
        error_message = f"❌ Model not found at path: {model_path}. Please train it first."
        logger.error(error_message)
        raise FileNotFoundError(error_message)

    model = joblib.load(model_path)
    logger.debug(f"📦 Loaded model from {model_path} for prediction.")

    return model.predict([text])[0]
