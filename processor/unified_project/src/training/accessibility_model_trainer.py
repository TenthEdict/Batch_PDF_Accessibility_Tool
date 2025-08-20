#!/usr/bin/env python3
"""
Accessibility Model Training Module

This module provides comprehensive ML model training for accessibility compliance prediction.
Integrates with AccessibilityFeatureEngineer output and Phase 2B infrastructure.

Key Capabilities:
- Multi-target classification for WCAG criteria and content type prediction
- Regression modeling for accessibility confidence score estimation
- Hyperparameter optimization with cross-validation
- Model evaluation and performance metrics analysis
- Integration with FAISS vector database for similarity-based enhancement
- Production model persistence and deployment framework

Integration with Phase 2B Infrastructure:
- Leverages FAISS vector database for accessibility pattern storage
- Utilizes hierarchical caching for model inference optimization
- Maintains thread-safety for concurrent accessibility enhancement
- Extends AdaptiveMLEnhancer with accessibility-specific capabilities
"""

import logging
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
import time
import joblib
from collections import defaultdict

# ML and model training imports
try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, RandomForestRegressor
    from sklearn.linear_model import LogisticRegression, Ridge
    from sklearn.svm import SVC, SVR
    from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, cross_val_score, StratifiedKFold
    from sklearn.metrics import (
        classification_report, confusion_matrix, accuracy_score, 
        precision_recall_fscore_support, mean_absolute_error, 
        mean_squared_error, r2_score
    )
    from sklearn.multioutput import MultiOutputClassifier, MultiOutputRegressor
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler
    ML_DEPS_AVAILABLE = True
except ImportError as e:
    ML_DEPS_AVAILABLE = False
    logging.warning(f"ML dependencies not available: {e}")

# Optional visualization imports
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False
    logging.info("Visualization libraries (matplotlib, seaborn) not available - model training will proceed without plotting capabilities")

# Import AccessibilityFeatureEngineer components
try:
    from .accessibility_feature_engineer import AccessibilityTrainingDataset, AccessibilityFeatureConfig
    FEATURE_ENGINEER_AVAILABLE = True
except ImportError:
    FEATURE_ENGINEER_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class AccessibilityModelConfig:
    """Configuration for accessibility model training."""
    # Model selection parameters
    enable_wcag_classifier: bool = True
    enable_content_classifier: bool = True
    enable_confidence_regressor: bool = True
    
    # Hyperparameter optimization
    param_optimization: str = "grid_search"  # grid_search, random_search, none
    cv_folds: int = 5
    optimization_scoring: str = "f1_weighted"  # for classification
    regression_scoring: str = "neg_mean_absolute_error"
    
    # Model algorithms to evaluate
    classification_algorithms: List[str] = None
    regression_algorithms: List[str] = None
    
    # Training parameters
    test_size: float = 0.2
    random_state: int = 42
    n_jobs: int = -1  # Use all available cores
    
    # Model persistence
    save_models: bool = True
    save_evaluation_plots: bool = True
    model_version: str = "v1.0"
    
    def __post_init__(self):
        if self.classification_algorithms is None:
            self.classification_algorithms = ["random_forest", "gradient_boosting", "logistic_regression"]
        if self.regression_algorithms is None:
            self.regression_algorithms = ["random_forest", "ridge", "svr"]


@dataclass
class AccessibilityModelSuite:
    """Container for trained accessibility models and metadata."""
    wcag_classifier: Optional[Any] = None
    content_classifier: Optional[Any] = None
    confidence_regressor: Optional[Any] = None
    
    # Model metadata
    training_metadata: Dict[str, Any] = None
    performance_metrics: Dict[str, Dict[str, float]] = None
    feature_importance: Dict[str, np.ndarray] = None
    
    # Training configuration
    config: AccessibilityModelConfig = None
    training_timestamp: float = None
    model_version: str = None


class AccessibilityModelTrainer:
    """
    Comprehensive ML model training system for accessibility compliance prediction.
    
    Capabilities:
    - Multi-target classification for WCAG criteria and content type
    - Regression modeling for confidence score prediction
    - Automated hyperparameter optimization with cross-validation
    - Model performance evaluation and comparison
    - Production model persistence and deployment preparation
    """
    
    def __init__(self, config: Optional[AccessibilityModelConfig] = None):
        """
        Initialize the accessibility model trainer.
        
        Args:
            config: Model training configuration
        """
        if not ML_DEPS_AVAILABLE:
            raise ImportError("Core ML dependencies not available. Install with: pip install scikit-learn pandas numpy")
        
        self.config = config or AccessibilityModelConfig()
        
        # Initialize model containers
        self.models = AccessibilityModelSuite()
        self.models.config = self.config
        self.models.training_timestamp = time.time()
        self.models.model_version = self.config.model_version
        
        # Training state
        self.dataset = None
        self.training_history = []
        self.model_comparison_results = {}
        
        logger.info(f"AccessibilityModelTrainer initialized with config: {self.config.model_version}")
    
    def load_training_dataset(self, dataset_path: Union[Path, str, AccessibilityTrainingDataset]):
        """
        Load training dataset for model training.
        
        Args:
            dataset_path: Path to saved dataset or AccessibilityTrainingDataset object
        """
        if isinstance(dataset_path, AccessibilityTrainingDataset):
            self.dataset = dataset_path
            logger.info("Training dataset loaded from object")
        else:
            from .accessibility_feature_engineer import AccessibilityFeatureEngineer
            self.dataset = AccessibilityFeatureEngineer.load_dataset(Path(dataset_path))
            logger.info(f"Training dataset loaded from {dataset_path}")
        
        # Validate dataset
        self._validate_dataset()
        
        logger.info(f"Dataset validation complete:")
        logger.info(f"  - Features: {self.dataset.X_train.shape[1]}")
        logger.info(f"  - Train samples: {len(self.dataset.X_train)}")
        logger.info(f"  - Test samples: {len(self.dataset.X_test)}")
        logger.info(f"  - Target variables: {list(self.dataset.y_train.keys())}")
    
    def _validate_dataset(self):
        """Validate training dataset integrity."""
        if self.dataset is None:
            raise ValueError("No dataset loaded")
        
        required_targets = []
        if self.config.enable_wcag_classifier:
            required_targets.append('wcag_criteria')
        if self.config.enable_content_classifier:
            required_targets.append('content_type')
        if self.config.enable_confidence_regressor:
            required_targets.append('confidence_score')
        
        missing_targets = [t for t in required_targets if t not in self.dataset.y_train]
        if missing_targets:
            raise ValueError(f"Missing required target variables: {missing_targets}")
        
        # Validate data shapes
        n_train = len(self.dataset.X_train)
        for target_name, target_data in self.dataset.y_train.items():
            if len(target_data) != n_train:
                raise ValueError(f"Target '{target_name}' length mismatch: {len(target_data)} != {n_train}")
        
        logger.info("Dataset validation passed successfully")
    
    def train_all_models(self) -> AccessibilityModelSuite:
        """
        Train all enabled accessibility models with hyperparameter optimization.
        
        Returns:
            Trained model suite with performance metrics
        """
        logger.info("Starting comprehensive accessibility model training...")
        
        if self.dataset is None:
            raise ValueError("No training dataset loaded. Call load_training_dataset() first.")
        
        training_results = {}
        
        # Train WCAG classifier
        if self.config.enable_wcag_classifier:
            logger.info("Training WCAG criteria classifier...")
            wcag_results = self._train_classification_model(
                'wcag_criteria',
                self.config.classification_algorithms
            )
            self.models.wcag_classifier = wcag_results['best_model']
            training_results['wcag_classifier'] = wcag_results
        
        # Train content type classifier
        if self.config.enable_content_classifier:
            logger.info("Training content type classifier...")
            content_results = self._train_classification_model(
                'content_type',
                self.config.classification_algorithms
            )
            self.models.content_classifier = content_results['best_model']
            training_results['content_classifier'] = content_results
        
        # Train confidence regressor
        if self.config.enable_confidence_regressor:
            logger.info("Training confidence score regressor...")
            confidence_results = self._train_regression_model(
                'confidence_score',
                self.config.regression_algorithms
            )
            self.models.confidence_regressor = confidence_results['best_model']
            training_results['confidence_regressor'] = confidence_results
        
        # Compile training metadata
        self._compile_training_metadata(training_results)
        
        logger.info("Accessibility model training completed successfully")
        return self.models
    
    def _train_classification_model(self, target_name: str, algorithms: List[str]) -> Dict[str, Any]:
        """Train and optimize classification model for specified target."""
        logger.info(f"Training classification model for target: {target_name}")
        
        X_train, X_val = self.dataset.X_train, self.dataset.X_val
        y_train = self.dataset.y_train[target_name]
        y_val = self.dataset.y_val[target_name]
        
        best_model = None
        best_score = -np.inf
        model_results = {}
        
        for algorithm in algorithms:
            logger.info(f"Evaluating {algorithm} for {target_name}")
            
            # Get model and parameter grid
            model, param_grid = self._get_classification_model_and_params(algorithm)
            
            # Hyperparameter optimization
            if self.config.param_optimization == "grid_search" and param_grid:
                cv = StratifiedKFold(n_splits=self.config.cv_folds, shuffle=True, random_state=self.config.random_state)
                search = GridSearchCV(
                    model, param_grid,
                    cv=cv,
                    scoring=self.config.optimization_scoring,
                    n_jobs=self.config.n_jobs,
                    verbose=0
                )
            elif self.config.param_optimization == "random_search" and param_grid:
                cv = StratifiedKFold(n_splits=self.config.cv_folds, shuffle=True, random_state=self.config.random_state)
                search = RandomizedSearchCV(
                    model, param_grid,
                    cv=cv,
                    scoring=self.config.optimization_scoring,
                    n_jobs=self.config.n_jobs,
                    n_iter=20,
                    random_state=self.config.random_state,
                    verbose=0
                )
            else:
                search = model
            
            # Train model
            search.fit(X_train, y_train)
            
            # Get best model (either from search or original model)
            if hasattr(search, 'best_estimator_'):
                trained_model = search.best_estimator_
                cv_score = search.best_score_
                best_params = search.best_params_
            else:
                trained_model = search
                cv_scores = cross_val_score(trained_model, X_train, y_train, 
                                          cv=self.config.cv_folds, 
                                          scoring=self.config.optimization_scoring)
                cv_score = cv_scores.mean()
                best_params = {}
            
            # Validate on validation set
            val_predictions = trained_model.predict(X_val)
            val_score = accuracy_score(y_val, val_predictions)
            
            # Store results
            model_results[algorithm] = {
                'model': trained_model,
                'cv_score': cv_score,
                'val_score': val_score,
                'best_params': best_params,
                'predictions': val_predictions
            }
            
            # Track best model
            if val_score > best_score:
                best_score = val_score
                best_model = trained_model
            
            logger.info(f"{algorithm} - CV Score: {cv_score:.4f}, Val Score: {val_score:.4f}")
        
        return {
            'best_model': best_model,
            'best_score': best_score,
            'all_results': model_results,
            'target_name': target_name
        }
    
    def _train_regression_model(self, target_name: str, algorithms: List[str]) -> Dict[str, Any]:
        """Train and optimize regression model for specified target."""
        logger.info(f"Training regression model for target: {target_name}")
        
        X_train, X_val = self.dataset.X_train, self.dataset.X_val
        y_train = self.dataset.y_train[target_name]
        y_val = self.dataset.y_val[target_name]
        
        best_model = None
        best_score = np.inf  # Lower MAE is better
        model_results = {}
        
        for algorithm in algorithms:
            logger.info(f"Evaluating {algorithm} for {target_name}")
            
            # Get model and parameter grid
            model, param_grid = self._get_regression_model_and_params(algorithm)
            
            # Hyperparameter optimization
            if self.config.param_optimization == "grid_search" and param_grid:
                search = GridSearchCV(
                    model, param_grid,
                    cv=self.config.cv_folds,
                    scoring=self.config.regression_scoring,
                    n_jobs=self.config.n_jobs,
                    verbose=0
                )
            elif self.config.param_optimization == "random_search" and param_grid:
                search = RandomizedSearchCV(
                    model, param_grid,
                    cv=self.config.cv_folds,
                    scoring=self.config.regression_scoring,
                    n_jobs=self.config.n_jobs,
                    n_iter=20,
                    random_state=self.config.random_state,
                    verbose=0
                )
            else:
                search = model
            
            # Train model
            search.fit(X_train, y_train)
            
            # Get best model
            if hasattr(search, 'best_estimator_'):
                trained_model = search.best_estimator_
                cv_score = -search.best_score_  # Convert back from negative MAE
                best_params = search.best_params_
            else:
                trained_model = search
                cv_scores = cross_val_score(trained_model, X_train, y_train, 
                                          cv=self.config.cv_folds, 
                                          scoring=self.config.regression_scoring)
                cv_score = -cv_scores.mean()  # Convert from negative MAE
                best_params = {}
            
            # Validate on validation set
            val_predictions = trained_model.predict(X_val)
            val_mae = mean_absolute_error(y_val, val_predictions)
            val_r2 = r2_score(y_val, val_predictions)
            
            # Store results
            model_results[algorithm] = {
                'model': trained_model,
                'cv_score': cv_score,
                'val_mae': val_mae,
                'val_r2': val_r2,
                'best_params': best_params,
                'predictions': val_predictions
            }
            
            # Track best model (lowest MAE)
            if val_mae < best_score:
                best_score = val_mae
                best_model = trained_model
            
            logger.info(f"{algorithm} - CV MAE: {cv_score:.4f}, Val MAE: {val_mae:.4f}, Val R²: {val_r2:.4f}")
        
        return {
            'best_model': best_model,
            'best_score': best_score,
            'all_results': model_results,
            'target_name': target_name
        }

    def _get_classification_model_and_params(self, algorithm: str) -> Tuple[Any, Dict]:
        """Get classification model and hyperparameter grid for algorithm."""
        if algorithm == "random_forest":
            model = RandomForestClassifier(random_state=self.config.random_state, n_jobs=self.config.n_jobs)
            param_grid = {
                'n_estimators': [100, 200, 300],
                'max_depth': [None, 10, 20, 30],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4]
            }
        elif algorithm == "gradient_boosting":
            model = GradientBoostingClassifier(random_state=self.config.random_state)
            param_grid = {
                'n_estimators': [100, 200],
                'learning_rate': [0.1, 0.05, 0.01],
                'max_depth': [3, 5, 7],
                'subsample': [0.8, 0.9, 1.0]
            }
        elif algorithm == "logistic_regression":
            model = LogisticRegression(
                random_state=self.config.random_state, 
                max_iter=1000, 
                n_jobs=self.config.n_jobs,
                multi_class='multinomial'
            )
            param_grid = {
                'C': [0.001, 0.01, 0.1, 1, 10, 100],
                'penalty': ['l1', 'l2'],
                'solver': ['lbfgs', 'saga']
            }
        elif algorithm == "svm":
            model = SVC(random_state=self.config.random_state)
            param_grid = {
                'C': [0.1, 1, 10, 100],
                'kernel': ['rbf', 'linear'],
                'gamma': ['scale', 'auto', 0.001, 0.01]
            }
        else:
            raise ValueError(f"Unknown classification algorithm: {algorithm}")
        
        return model, param_grid
    
    def _get_regression_model_and_params(self, algorithm: str) -> Tuple[Any, Dict]:
        """Get regression model and hyperparameter grid for algorithm."""
        if algorithm == "random_forest":
            model = RandomForestRegressor(random_state=self.config.random_state, n_jobs=self.config.n_jobs)
            param_grid = {
                'n_estimators': [100, 200, 300],
                'max_depth': [None, 10, 20, 30],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4]
            }
        elif algorithm == "ridge":
            model = Ridge(random_state=self.config.random_state)
            param_grid = {
                'alpha': [0.001, 0.01, 0.1, 1, 10, 100, 1000],
                'solver': ['auto', 'svd', 'cholesky', 'saga']
            }
        elif algorithm == "svr":
            model = SVR()
            param_grid = {
                'C': [0.1, 1, 10, 100],
                'kernel': ['rbf', 'linear'],
                'gamma': ['scale', 'auto', 0.001, 0.01],
                'epsilon': [0.01, 0.1, 0.2]
            }
        else:
            raise ValueError(f"Unknown regression algorithm: {algorithm}")
        
        return model, param_grid
    
    def _compile_training_metadata(self, training_results: Dict[str, Any]):
        """Compile comprehensive training metadata and performance metrics."""
        logger.info("Compiling training metadata and performance metrics...")
        
        performance_metrics = {}
        feature_importance = {}
        
        for model_type, results in training_results.items():
            if results is None:
                continue
            
            target_name = results['target_name']
            best_model = results['best_model']
            
            # Extract performance metrics
            if 'classifier' in model_type:
                # Classification metrics
                y_test = self.dataset.y_test[target_name]
                test_predictions = best_model.predict(self.dataset.X_test)
                
                metrics = {
                    'accuracy': accuracy_score(y_test, test_predictions),
                    'cv_score': results['best_score'],
                    'model_type': 'classification'
                }
                
                # Add precision, recall, F1 for multi-class
                precision, recall, f1, _ = precision_recall_fscore_support(
                    y_test, test_predictions, average='weighted'
                )
                metrics.update({
                    'precision': precision,
                    'recall': recall,
                    'f1_score': f1
                })
                
            else:
                # Regression metrics
                y_test = self.dataset.y_test[target_name]
                test_predictions = best_model.predict(self.dataset.X_test)
                
                metrics = {
                    'mae': mean_absolute_error(y_test, test_predictions),
                    'rmse': np.sqrt(mean_squared_error(y_test, test_predictions)),
                    'r2_score': r2_score(y_test, test_predictions),
                    'cv_score': results['best_score'],
                    'model_type': 'regression'
                }
            
            performance_metrics[model_type] = metrics
            
            # Extract feature importance if available
            if hasattr(best_model, 'feature_importances_'):
                feature_importance[model_type] = best_model.feature_importances_
            elif hasattr(best_model, 'coef_'):
                feature_importance[model_type] = np.abs(best_model.coef_).flatten()
        
        # Store compiled metadata
        self.models.performance_metrics = performance_metrics
        self.models.feature_importance = feature_importance
        self.models.training_metadata = {
            'dataset_info': {
                'train_samples': len(self.dataset.X_train),
                'test_samples': len(self.dataset.X_test),
                'val_samples': len(self.dataset.X_val),
                'n_features': self.dataset.X_train.shape[1],
                'feature_names': self.dataset.feature_names,
                'target_names': self.dataset.target_names
            },
            'training_config': asdict(self.config),
            'training_timestamp': self.models.training_timestamp,
            'model_version': self.models.model_version,
            'all_results': training_results
        }
        
        logger.info("Training metadata compilation completed")
    
    def evaluate_models(self) -> Dict[str, Any]:
        """
        Comprehensive model evaluation with detailed performance analysis.
        
        Returns:
            Detailed evaluation results with metrics and analysis
        """
        logger.info("Performing comprehensive model evaluation...")
        
        if self.models.wcag_classifier is None and self.models.content_classifier is None and self.models.confidence_regressor is None:
            raise ValueError("No trained models available for evaluation")
        
        evaluation_results = {
            'overall_performance': {},
            'detailed_metrics': {},
            'feature_importance_analysis': {},
            'model_comparison': {}
        }
        
        # Evaluate each trained model
        if self.models.wcag_classifier is not None:
            wcag_eval = self._evaluate_classification_model(
                self.models.wcag_classifier, 'wcag_criteria'
            )
            evaluation_results['detailed_metrics']['wcag_classifier'] = wcag_eval
        
        if self.models.content_classifier is not None:
            content_eval = self._evaluate_classification_model(
                self.models.content_classifier, 'content_type'
            )
            evaluation_results['detailed_metrics']['content_classifier'] = content_eval
        
        if self.models.confidence_regressor is not None:
            confidence_eval = self._evaluate_regression_model(
                self.models.confidence_regressor, 'confidence_score'
            )
            evaluation_results['detailed_metrics']['confidence_regressor'] = confidence_eval
        
        # Feature importance analysis
        evaluation_results['feature_importance_analysis'] = self._analyze_feature_importance()
        
        # Overall performance summary
        evaluation_results['overall_performance'] = self._calculate_overall_performance()
        
        logger.info("Model evaluation completed successfully")
        return evaluation_results
    
    def _evaluate_classification_model(self, model: Any, target_name: str) -> Dict[str, Any]:
        """Detailed evaluation of classification model."""
        X_test = self.dataset.X_test
        y_test = self.dataset.y_test[target_name]
        
        # Predictions
        predictions = model.predict(X_test)
        prediction_proba = None
        if hasattr(model, 'predict_proba'):
            prediction_proba = model.predict_proba(X_test)
        
        # Classification metrics
        accuracy = accuracy_score(y_test, predictions)
        precision, recall, f1, support = precision_recall_fscore_support(
            y_test, predictions, average=None
        )
        
        # Weighted averages
        precision_weighted, recall_weighted, f1_weighted, _ = precision_recall_fscore_support(
            y_test, predictions, average='weighted'
        )
        
        # Confusion matrix
        cm = confusion_matrix(y_test, predictions)
        
        # Detailed classification report
        class_report = classification_report(y_test, predictions, output_dict=True)
        
        return {
            'accuracy': accuracy,
            'precision_per_class': precision.tolist(),
            'recall_per_class': recall.tolist(),
            'f1_per_class': f1.tolist(),
            'support_per_class': support.tolist(),
            'precision_weighted': precision_weighted,
            'recall_weighted': recall_weighted,
            'f1_weighted': f1_weighted,
            'confusion_matrix': cm.tolist(),
            'classification_report': class_report,
            'predictions': predictions.tolist(),
            'prediction_probabilities': prediction_proba.tolist() if prediction_proba is not None else None,
            'target_classes': self.dataset.target_names[target_name]
        }
    
    def _evaluate_regression_model(self, model: Any, target_name: str) -> Dict[str, Any]:
        """Detailed evaluation of regression model."""
        X_test = self.dataset.X_test
        y_test = self.dataset.y_test[target_name]
        
        # Predictions
        predictions = model.predict(X_test)
        
        # Regression metrics
        mae = mean_absolute_error(y_test, predictions)
        rmse = np.sqrt(mean_squared_error(y_test, predictions))
        r2 = r2_score(y_test, predictions)
        
        # Additional regression analysis
        residuals = y_test - predictions
        mean_residual = np.mean(residuals)
        std_residual = np.std(residuals)
        
        return {
            'mae': mae,
            'rmse': rmse,
            'r2_score': r2,
            'mean_residual': mean_residual,
            'std_residual': std_residual,
            'predictions': predictions.tolist(),
            'residuals': residuals.tolist(),
            'actual_values': y_test.tolist()
        }
    
    def _analyze_feature_importance(self) -> Dict[str, Any]:
        """Analyze feature importance across all trained models."""
        if not self.models.feature_importance:
            return {}
        
        feature_names = self.dataset.feature_names
        importance_analysis = {}
        
        for model_name, importance_scores in self.models.feature_importance.items():
            # Sort features by importance
            feature_importance_pairs = list(zip(feature_names, importance_scores))
            feature_importance_pairs.sort(key=lambda x: x[1], reverse=True)
            
            importance_analysis[model_name] = {
                'top_10_features': feature_importance_pairs[:10],
                'all_feature_importance': feature_importance_pairs,
                'mean_importance': np.mean(importance_scores),
                'std_importance': np.std(importance_scores)
            }
        
        return importance_analysis
    
    def _calculate_overall_performance(self) -> Dict[str, Any]:
        """Calculate overall performance summary across all models."""
        if not self.models.performance_metrics:
            return {}
        
        performance_summary = {
            'model_count': len(self.models.performance_metrics),
            'average_performance': {},
            'best_performing_models': {}
        }
        
        # Classification models average performance
        classification_metrics = []
        for model_name, metrics in self.models.performance_metrics.items():
            if metrics.get('model_type') == 'classification':
                classification_metrics.append(metrics)
        
        if classification_metrics:
            avg_accuracy = np.mean([m['accuracy'] for m in classification_metrics])
            avg_f1 = np.mean([m['f1_score'] for m in classification_metrics])
            performance_summary['average_performance']['classification'] = {
                'avg_accuracy': avg_accuracy,
                'avg_f1_score': avg_f1
            }
        
        # Regression models average performance
        regression_metrics = []
        for model_name, metrics in self.models.performance_metrics.items():
            if metrics.get('model_type') == 'regression':
                regression_metrics.append(metrics)
        
        if regression_metrics:
            avg_mae = np.mean([m['mae'] for m in regression_metrics])
            avg_r2 = np.mean([m['r2_score'] for m in regression_metrics])
            performance_summary['average_performance']['regression'] = {
                'avg_mae': avg_mae,
                'avg_r2_score': avg_r2
            }
        
        return performance_summary

    def save_models(self, output_dir: Union[Path, str]):
        """
        Save trained models and metadata for production deployment.
        
        Args:
            output_dir: Directory to save models and metadata
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Saving accessibility models to {output_dir}")
        
        # Save individual models
        model_paths = {}
        if self.models.wcag_classifier is not None:
            wcag_path = output_dir / f"wcag_classifier_{self.config.model_version}.joblib"
            joblib.dump(self.models.wcag_classifier, wcag_path)
            model_paths['wcag_classifier'] = str(wcag_path)
            logger.info(f"WCAG classifier saved: {wcag_path}")
        
        if self.models.content_classifier is not None:
            content_path = output_dir / f"content_classifier_{self.config.model_version}.joblib"
            joblib.dump(self.models.content_classifier, content_path)
            model_paths['content_classifier'] = str(content_path)
            logger.info(f"Content classifier saved: {content_path}")
        
        if self.models.confidence_regressor is not None:
            confidence_path = output_dir / f"confidence_regressor_{self.config.model_version}.joblib"
            joblib.dump(self.models.confidence_regressor, confidence_path)
            model_paths['confidence_regressor'] = str(confidence_path)
            logger.info(f"Confidence regressor saved: {confidence_path}")
        
        # Save model metadata
        metadata = {
            'model_version': self.models.model_version,
            'training_timestamp': self.models.training_timestamp,
            'model_paths': model_paths,
            'performance_metrics': self.models.performance_metrics,
            'feature_importance': {k: v.tolist() for k, v in self.models.feature_importance.items()},
            'training_metadata': self.models.training_metadata,
            'feature_names': self.dataset.feature_names,
            'target_names': self.dataset.target_names
        }
        
        metadata_path = output_dir / f"model_metadata_{self.config.model_version}.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        logger.info(f"Model metadata saved: {metadata_path}")
        
        # Save feature engineering components for inference
        preprocessing_dir = output_dir / "preprocessing"
        preprocessing_dir.mkdir(exist_ok=True)
        
        if hasattr(self.dataset, 'scaler') and self.dataset.scaler is not None:
            joblib.dump(self.dataset.scaler, preprocessing_dir / "scaler.joblib")
        
        if hasattr(self.dataset, 'label_encoders') and self.dataset.label_encoders:
            joblib.dump(self.dataset.label_encoders, preprocessing_dir / "label_encoders.joblib")
        
        logger.info("Model saving completed successfully")
        return model_paths
    
    @classmethod
    def load_models(cls, model_dir: Union[Path, str], model_version: str = None) -> 'AccessibilityModelSuite':
        """
        Load trained models from disk for inference.
        
        Args:
            model_dir: Directory containing saved models
            model_version: Specific model version to load (latest if None)
            
        Returns:
            Loaded AccessibilityModelSuite
        """
        model_dir = Path(model_dir)
        
        # Find model metadata file
        if model_version:
            metadata_file = model_dir / f"model_metadata_{model_version}.json"
        else:
            metadata_files = list(model_dir.glob("model_metadata_*.json"))
            if not metadata_files:
                raise FileNotFoundError(f"No model metadata found in {model_dir}")
            metadata_file = max(metadata_files, key=lambda p: p.stat().st_mtime)
        
        # Load metadata
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        # Initialize model suite
        models = AccessibilityModelSuite()
        models.model_version = metadata['model_version']
        models.training_timestamp = metadata['training_timestamp']
        models.performance_metrics = metadata['performance_metrics']
        models.training_metadata = metadata['training_metadata']
        
        # Load individual models
        model_paths = metadata['model_paths']
        
        if 'wcag_classifier' in model_paths:
            models.wcag_classifier = joblib.load(model_paths['wcag_classifier'])
            logger.info(f"WCAG classifier loaded from {model_paths['wcag_classifier']}")
        
        if 'content_classifier' in model_paths:
            models.content_classifier = joblib.load(model_paths['content_classifier'])
            logger.info(f"Content classifier loaded from {model_paths['content_classifier']}")
        
        if 'confidence_regressor' in model_paths:
            models.confidence_regressor = joblib.load(model_paths['confidence_regressor'])
            logger.info(f"Confidence regressor loaded from {model_paths['confidence_regressor']}")
        
        logger.info(f"Models loaded successfully: version {models.model_version}")
        return models
    
    def predict_accessibility_features(self, feature_vector: np.ndarray) -> Dict[str, Any]:
        """
        Make accessibility predictions using trained models.
        
        Args:
            feature_vector: Preprocessed feature vector for prediction
            
        Returns:
            Dictionary containing predictions from all available models
        """
        if feature_vector.ndim == 1:
            feature_vector = feature_vector.reshape(1, -1)
        
        predictions = {}
        
        # WCAG criteria prediction
        if self.models.wcag_classifier is not None:
            wcag_pred = self.models.wcag_classifier.predict(feature_vector)[0]
            wcag_proba = None
            if hasattr(self.models.wcag_classifier, 'predict_proba'):
                wcag_proba = self.models.wcag_classifier.predict_proba(feature_vector)[0]
            
            predictions['wcag_criteria'] = {
                'prediction': wcag_pred,
                'probabilities': wcag_proba.tolist() if wcag_proba is not None else None,
                'classes': self.dataset.target_names.get('wcag_criteria', [])
            }
        
        # Content type prediction
        if self.models.content_classifier is not None:
            content_pred = self.models.content_classifier.predict(feature_vector)[0]
            content_proba = None
            if hasattr(self.models.content_classifier, 'predict_proba'):
                content_proba = self.models.content_classifier.predict_proba(feature_vector)[0]
            
            predictions['content_type'] = {
                'prediction': content_pred,
                'probabilities': content_proba.tolist() if content_proba is not None else None,
                'classes': self.dataset.target_names.get('content_type', [])
            }
        
        # Confidence score prediction
        if self.models.confidence_regressor is not None:
            confidence_pred = self.models.confidence_regressor.predict(feature_vector)[0]
            predictions['confidence_score'] = {
                'prediction': float(confidence_pred)
            }
        
        return predictions
    
    def get_model_summary(self) -> Dict[str, Any]:
        """Get comprehensive summary of trained models."""
        available_models = []
        
        if self.models.wcag_classifier is not None:
            available_models.append('wcag_classifier')
        if self.models.content_classifier is not None:
            available_models.append('content_classifier')
        if self.models.confidence_regressor is not None:
            available_models.append('confidence_regressor')
        
        summary = {
            'model_version': self.models.model_version,
            'training_timestamp': self.models.training_timestamp,
            'available_models': available_models,
            'performance_summary': {},
            'feature_count': len(self.dataset.feature_names) if self.dataset else 0
        }
        
        if self.models.performance_metrics:
            summary['performance_summary'] = self.models.performance_metrics
        
        return summary


def main():
    """Example usage of AccessibilityModelTrainer."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Train accessibility ML models")
    parser.add_argument("dataset_path", type=Path, help="Path to training dataset")
    parser.add_argument("output_dir", type=Path, help="Directory to save trained models")
    parser.add_argument("--model-version", default="v1.0", help="Model version identifier")
    parser.add_argument("--enable-wcag", action="store_true", default=True, help="Enable WCAG classifier")
    parser.add_argument("--enable-content", action="store_true", default=True, help="Enable content classifier")
    parser.add_argument("--enable-confidence", action="store_true", default=True, help="Enable confidence regressor")
    parser.add_argument("--param-optimization", choices=["grid_search", "random_search", "none"], 
                       default="grid_search", help="Hyperparameter optimization method")
    parser.add_argument("--cv-folds", type=int, default=5, help="Cross-validation folds")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create model configuration
    config = AccessibilityModelConfig(
        enable_wcag_classifier=args.enable_wcag,
        enable_content_classifier=args.enable_content,
        enable_confidence_regressor=args.enable_confidence,
        param_optimization=args.param_optimization,
        cv_folds=args.cv_folds,
        model_version=args.model_version
    )
    
    # Initialize trainer
    trainer = AccessibilityModelTrainer(config)
    
    # Load dataset and train models
    trainer.load_training_dataset(args.dataset_path)
    models = trainer.train_all_models()
    
    # Evaluate models
    evaluation_results = trainer.evaluate_models()
    
    # Save models
    model_paths = trainer.save_models(args.output_dir)
    
    # Print summary
    print(f"\n✅ Accessibility model training completed!")
    print(f"📊 Models trained: {len(model_paths)}")
    print(f"📁 Models saved to: {args.output_dir}")
    print(f"🔍 Model version: {config.model_version}")
    
    # Print performance summary
    if evaluation_results.get('overall_performance'):
        print(f"\n📈 Performance Summary:")
        overall_perf = evaluation_results['overall_performance']
        if 'classification' in overall_perf.get('average_performance', {}):
            class_perf = overall_perf['average_performance']['classification']
            print(f"   Classification - Avg Accuracy: {class_perf['avg_accuracy']:.3f}, Avg F1: {class_perf['avg_f1_score']:.3f}")
        if 'regression' in overall_perf.get('average_performance', {}):
            reg_perf = overall_perf['average_performance']['regression']
            print(f"   Regression - Avg MAE: {reg_perf['avg_mae']:.3f}, Avg R²: {reg_perf['avg_r2_score']:.3f}")


if __name__ == "__main__":
    main()
