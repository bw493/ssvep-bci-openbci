"""
Classification module for SSVEP BCI pipeline

Includes:
- LDA (Linear Discriminant Analysis)
- SVM (Support Vector Machine)
- Cross-validation utilities
- Prediction functions
"""

from .classifier import (
    create_classifier,
    train_classifier,
    evaluate_classifier,
    cross_validate_classifier,
    predict_command
)

__all__ = [
    'create_classifier',
    'train_classifier',
    'evaluate_classifier',
    'cross_validate_classifier',
    'predict_command'
]
