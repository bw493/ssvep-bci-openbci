"""
Classification module for SSVEP BCI
Implements LDA and SVM classifiers for command decoding
"""

import numpy as np
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.svm import SVC
from sklearn.model_selection import cross_val_score
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from typing import Tuple, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import CLASSIFIER_TYPE, SVM_KERNEL, SVM_C


def create_classifier(classifier_type: str = CLASSIFIER_TYPE,
                     **kwargs):
    """
    Create a classifier instance
    
    Parameters:
    -----------
    classifier_type : str
        Type of classifier ('lda' or 'svm')
    **kwargs : dict
        Additional parameters for the classifier
        
    Returns:
    --------
    classifier : sklearn classifier
        Initialized classifier
    """
    if classifier_type.lower() == 'lda':
        print("Creating Linear Discriminant Analysis (LDA) classifier")
        return LinearDiscriminantAnalysis(**kwargs)
    
    elif classifier_type.lower() == 'svm':
        kernel = kwargs.get('kernel', SVM_KERNEL)
        C = kwargs.get('C', SVM_C)
        print(f"Creating Support Vector Machine (SVM) classifier")
        print(f"  Kernel: {kernel}, C: {C}")
        return SVC(kernel=kernel, C=C, **{k: v for k, v in kwargs.items() 
                                          if k not in ['kernel', 'C']})
    
    else:
        raise ValueError(f"Unknown classifier type: {classifier_type}")


def train_classifier(X_train: np.ndarray,
                    y_train: np.ndarray,
                    classifier_type: str = CLASSIFIER_TYPE,
                    **kwargs):
    """
    Train a classifier on the training data
    
    Parameters:
    -----------
    X_train : ndarray, shape (n_samples, n_features)
        Training features
    y_train : ndarray, shape (n_samples,)
        Training labels
    classifier_type : str
        Type of classifier
    **kwargs : dict
        Additional classifier parameters
        
    Returns:
    --------
    classifier : fitted classifier
        Trained classifier
    """
    print(f"\n=== Training {classifier_type.upper()} Classifier ===")
    print(f"Training samples: {X_train.shape[0]}")
    print(f"Features: {X_train.shape[1]}")
    print(f"Classes: {np.unique(y_train)}")
    
    # Create classifier
    classifier = create_classifier(classifier_type, **kwargs)
    
    # Train
    classifier.fit(X_train, y_train)
    
    # Training accuracy
    train_pred = classifier.predict(X_train)
    train_acc = accuracy_score(y_train, train_pred)
    print(f"Training accuracy: {train_acc:.2%}")
    
    print("=== Training Complete ===\n")
    
    return classifier


def evaluate_classifier(classifier,
                       X_test: np.ndarray,
                       y_test: np.ndarray,
                       class_names: list = None) -> dict:
    """
    Evaluate classifier performance on test data
    
    Parameters:
    -----------
    classifier : fitted classifier
        Trained classifier
    X_test : ndarray
        Test features
    y_test : ndarray
        Test labels
    class_names : list, optional
        Names of classes for reporting
        
    Returns:
    --------
    results : dict
        Dictionary containing evaluation metrics
    """
    print("\n=== Evaluating Classifier ===")
    
    # Predictions
    y_pred = classifier.predict(X_test)
    
    # Accuracy
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Test accuracy: {accuracy:.2%}")
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    print("\nConfusion Matrix:")
    print(cm)
    
    # Classification report
    if class_names is None:
        class_names = [f"Class {i}" for i in np.unique(y_test)]
    
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=class_names))
    
    results = {
        'accuracy': accuracy,
        'confusion_matrix': cm,
        'predictions': y_pred,
        'true_labels': y_test
    }
    
    print("=== Evaluation Complete ===\n")
    
    return results


def cross_validate_classifier(X: np.ndarray,
                             y: np.ndarray,
                             classifier_type: str = CLASSIFIER_TYPE,
                             cv: int = 5,
                             **kwargs) -> Tuple[np.ndarray, float]:
    """
    Perform cross-validation on the classifier
    
    Parameters:
    -----------
    X : ndarray
        Features
    y : ndarray
        Labels
    classifier_type : str
        Type of classifier
    cv : int
        Number of cross-validation folds
    **kwargs : dict
        Additional classifier parameters
        
    Returns:
    --------
    scores : ndarray
        Cross-validation scores for each fold
    mean_score : float
        Mean cross-validation score
    """
    print(f"\n=== Cross-Validation ({cv}-fold) ===")
    
    # Create classifier
    classifier = create_classifier(classifier_type, **kwargs)
    
    # Cross-validate
    scores = cross_val_score(classifier, X, y, cv=cv, scoring='accuracy')
    
    print(f"Fold scores: {scores}")
    print(f"Mean accuracy: {scores.mean():.2%} (+/- {scores.std() * 2:.2%})")
    
    print("=== Cross-Validation Complete ===\n")
    
    return scores, scores.mean()


def predict_command(classifier,
                   features: np.ndarray,
                   command_map: dict = None) -> str:
    """
    Predict command from features
    
    Parameters:
    -----------
    classifier : fitted classifier
        Trained classifier
    features : ndarray, shape (n_features,) or (1, n_features)
        Feature vector
    command_map : dict, optional
        Mapping from class labels to commands
        
    Returns:
    --------
    command : str
        Predicted command
    """
    # Ensure features are 2D
    if features.ndim == 1:
        features = features.reshape(1, -1)
    
    # Predict
    prediction = classifier.predict(features)[0]
    
    # Map to command
    if command_map is not None:
        command = command_map.get(prediction, f"Unknown ({prediction})")
    else:
        command = str(prediction)
    
    return command


if __name__ == "__main__":
    print("Classification module loaded successfully")
    print(f"Default classifier: {CLASSIFIER_TYPE.upper()}")
    if CLASSIFIER_TYPE.lower() == 'svm':
        print(f"  SVM kernel: {SVM_KERNEL}, C: {SVM_C}")
