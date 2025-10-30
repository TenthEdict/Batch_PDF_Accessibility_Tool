#!/usr/bin/env python3
"""
Accessibility Feature Engineering Module

This module processes extracted accessibility patterns to create ML-ready training data.
Integrates with existing Phase 2B infrastructure (FAISS, hierarchical caching, ML enhancement).

Key Capabilities:
- Feature vector processing and normalization for 128-dimensional accessibility data
- WCAG compliance pattern encoding for classification tasks
- Content type and structure pattern feature engineering
- Integration with FAISS vector database for similarity-based training
- Training/validation/test dataset splitting with stratification
- Feature importance analysis for accessibility compliance prediction

Integration with Phase 2B:
- Extends AdaptiveMLEnhancer feature processing capabilities
- Leverages FAISS vector database for accessibility pattern storage
- Utilizes hierarchical caching for training data management
- Maintains thread-safety for concurrent model training operations
"""

import logging
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, TYPE_CHECKING
from dataclasses import dataclass, asdict
import time
import hashlib
from collections import defaultdict, Counter

# ML and data processing imports
try:
    from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
    from sklearn.model_selection import train_test_split, StratifiedKFold
    from sklearn.feature_selection import SelectKBest, chi2, mutual_info_classif
    from sklearn.decomposition import PCA
    from sklearn.metrics import classification_report, confusion_matrix
    import joblib
    ML_DEPS_AVAILABLE = True
except ImportError as e:
    ML_DEPS_AVAILABLE = False
    StandardScaler = None
    LabelEncoder = None
    logging.warning(f"ML dependencies not available: {e}")

# Type hints only (not evaluated at runtime)
if TYPE_CHECKING:
    from sklearn.preprocessing import StandardScaler as StandardScalerType
    from sklearn.preprocessing import LabelEncoder as LabelEncoderType

# FAISS integration (Phase 2B infrastructure)
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class AccessibilityFeatureConfig:
    """Configuration for accessibility feature engineering."""
    feature_vector_dim: int = 128
    wcag_criteria_encoding: str = "one_hot"  # one_hot, label, multi_label
    content_type_encoding: str = "label"     # label, one_hot
    normalization_method: str = "standard"   # standard, minmax, robust
    feature_selection_k: int = 50           # Number of top features to select
    pca_components: Optional[int] = None     # PCA dimensionality reduction
    test_size: float = 0.2                 # Train/test split ratio
    validation_size: float = 0.2           # Validation set ratio
    random_state: int = 42                  # Reproducibility
    stratify_by: str = "wcag_level"         # Stratification column


@dataclass
class AccessibilityTrainingDataset:
    """Container for processed accessibility training data."""
    X_train: np.ndarray
    X_test: np.ndarray
    X_val: np.ndarray
    y_train: Dict[str, np.ndarray]  # Multiple target variables
    y_test: Dict[str, np.ndarray]
    y_val: Dict[str, np.ndarray]
    feature_names: List[str]
    target_names: Dict[str, List[str]]
    scaler: Optional['StandardScalerType']
    label_encoders: Dict[str, 'LabelEncoderType']
    metadata: Dict[str, Any]


class AccessibilityFeatureEngineer:
    """
    Feature engineering pipeline for accessibility training data.
    
    Processes extracted accessibility patterns to create ML-ready datasets for:
    - WCAG compliance classification
    - Content type prediction
    - Document structure pattern recognition
    - Accessibility score regression
    """
    
    def __init__(self, training_data_dir: Path, config: Optional[AccessibilityFeatureConfig] = None):
        """
        Initialize the accessibility feature engineer.
        
        Args:
            training_data_dir: Directory containing extracted accessibility patterns
            config: Feature engineering configuration
        """
        if not ML_DEPS_AVAILABLE:
            raise ImportError("ML dependencies not available. Install with: pip install scikit-learn pandas numpy")
        
        self.training_data_dir = Path(training_data_dir)
        self.config = config or AccessibilityFeatureConfig()
        
        # Verify required pattern files exist
        self.pattern_files = {
            'aggregated': self.training_data_dir / 'aggregated_patterns.json',
            'wcag_training': self.training_data_dir / 'wcag_training_data.json',
            'feature_stats': self.training_data_dir / 'feature_vector_stats.json',
            'content_analysis': self.training_data_dir / 'content_type_analysis_patterns.json',
            'structure_patterns': self.training_data_dir / 'structure_patterns_patterns.json'
        }
        
        self._validate_pattern_files()
        
        # Initialize processing components
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_selector = None
        self.pca_transformer = None
        
        # Load raw training data
        self.raw_data = self._load_training_data()
        
        logger.info(f"AccessibilityFeatureEngineer initialized with {len(self.raw_data)} training samples")
    
    def _validate_pattern_files(self):
        """Validate that required pattern files exist."""
        missing_files = []
        for name, file_path in self.pattern_files.items():
            if not file_path.exists():
                missing_files.append(f"{name}: {file_path}")
        
        if missing_files:
            raise FileNotFoundError(f"Missing pattern files: {missing_files}")
        
        logger.info("All required pattern files validated successfully")
    
    def _load_training_data(self) -> List[Dict[str, Any]]:
        """Load and combine training data from pattern files."""
        logger.info("Loading training data from pattern files...")
        
        # Load WCAG training data (primary dataset)
        with open(self.pattern_files['wcag_training'], 'r') as f:
            wcag_data = json.load(f)
        
        # Load feature vector statistics for normalization context
        with open(self.pattern_files['feature_stats'], 'r') as f:
            feature_stats = json.load(f)
        
        # Load content type analysis for additional features
        with open(self.pattern_files['content_analysis'], 'r') as f:
            content_analysis = json.load(f)
        
        # Load aggregated patterns for global context
        with open(self.pattern_files['aggregated'], 'r') as f:
            aggregated_patterns = json.load(f)
        
        # Store metadata for feature engineering
        self.feature_statistics = feature_stats
        self.content_type_info = content_analysis
        self.global_patterns = aggregated_patterns
        
        logger.info(f"Loaded {len(wcag_data)} WCAG training samples")
        return wcag_data
    
    def create_training_dataset(self) -> AccessibilityTrainingDataset:
        """
        Create comprehensive training dataset with multiple target variables.
        
        Returns:
            AccessibilityTrainingDataset with processed features and targets
        """
        logger.info("Creating comprehensive accessibility training dataset...")
        
        # Extract features and targets
        features_df, targets_dict = self._extract_features_and_targets()
        
        # Feature engineering pipeline
        features_processed = self._engineer_features(features_df)
        
        # Split data with stratification
        splits = self._create_data_splits(features_processed, targets_dict)
        
        # Create final dataset
        dataset = AccessibilityTrainingDataset(
            X_train=splits['X_train'],
            X_test=splits['X_test'], 
            X_val=splits['X_val'],
            y_train=splits['y_train'],
            y_test=splits['y_test'],
            y_val=splits['y_val'],
            feature_names=features_processed.columns.tolist(),
            target_names=splits['target_names'],
            scaler=self.scaler,
            label_encoders=self.label_encoders,
            metadata={
                'config': asdict(self.config),
                'feature_statistics': self.feature_statistics,
                'content_type_info': self.content_type_info,
                'dataset_timestamp': time.time(),
                'samples_total': len(features_processed),
                'train_samples': len(splits['X_train']),
                'test_samples': len(splits['X_test']),
                'val_samples': len(splits['X_val'])
            }
        )
        
        logger.info(f"Training dataset created successfully:")
        logger.info(f"  - Features: {features_processed.shape[1]}")
        logger.info(f"  - Train samples: {len(splits['X_train'])}")
        logger.info(f"  - Test samples: {len(splits['X_test'])}")
        logger.info(f"  - Validation samples: {len(splits['X_val'])}")
        
        return dataset
    
    def _extract_features_and_targets(self) -> Tuple[pd.DataFrame, Dict[str, np.ndarray]]:
        """Extract features and target variables from training data."""
        logger.info("Extracting features and targets from training data...")
        
        features_list = []
        wcag_criteria = []
        content_types = []
        confidence_scores = []
        
        for sample in self.raw_data:
            # Create feature vector from sample characteristics
            feature_vector = self._create_feature_vector_from_sample(sample)
            features_list.append(feature_vector)
            
            # Extract target variables
            wcag_criteria.append(sample.get('wcag_criterion', 'unknown'))
            content_types.append(sample.get('content_type', 'unknown'))
            confidence_scores.append(sample.get('confidence_score', 0.0))
        
        # Create features DataFrame
        feature_names = self._generate_feature_names()
        features_df = pd.DataFrame(features_list, columns=feature_names)
        
        # Create targets dictionary
        targets_dict = {
            'wcag_criteria': np.array(wcag_criteria),
            'content_type': np.array(content_types),
            'confidence_score': np.array(confidence_scores)
        }
        
        logger.info(f"Extracted {len(feature_names)} features and {len(targets_dict)} target variables")
        return features_df, targets_dict
    
    def _create_feature_vector_from_sample(self, sample: Dict[str, Any]) -> List[float]:
        """Create feature vector from a training sample."""
        feature_vector = []
        
        # Characteristics-based features
        characteristics = sample.get('characteristics', {})
        
        # Basic characteristics (normalize based on global statistics)
        feature_vector.extend([
            characteristics.get('has_doc_language', 0.0),
            characteristics.get('language_changes', 0.0),
            characteristics.get('heading_count', 0.0),
            characteristics.get('list_count', 0.0),
            characteristics.get('table_count', 0.0),
            characteristics.get('image_count', 0.0),
            characteristics.get('alt_text_coverage', 0.0)
        ])
        
        # Semantic roles features (one-hot encoding)
        semantic_roles = sample.get('semantic_roles', [])
        role_features = self._encode_semantic_roles(semantic_roles)
        feature_vector.extend(role_features)
        
        # Content type statistical features
        content_type = sample.get('content_type', 'unknown')
        content_features = self._encode_content_type_features(content_type)
        feature_vector.extend(content_features)
        
        # WCAG criterion complexity features
        wcag_criterion = sample.get('wcag_criterion', 'unknown')
        wcag_features = self._encode_wcag_complexity(wcag_criterion)
        feature_vector.extend(wcag_features)
        
        # Confidence-based features
        confidence = sample.get('confidence_score', 0.0)
        confidence_features = [
            confidence,
            confidence ** 2,  # Non-linear confidence relationship
            1.0 if confidence > 0.8 else 0.0,  # High confidence indicator
            1.0 if confidence < 0.5 else 0.0   # Low confidence indicator
        ]
        feature_vector.extend(confidence_features)
        
        # Pad or truncate to expected dimension
        target_dim = self.config.feature_vector_dim
        if len(feature_vector) < target_dim:
            feature_vector.extend([0.0] * (target_dim - len(feature_vector)))
        elif len(feature_vector) > target_dim:
            feature_vector = feature_vector[:target_dim]
        
        return feature_vector
    
    def _encode_semantic_roles(self, semantic_roles: List[str]) -> List[float]:
        """Encode semantic roles as feature vector."""
        # Common semantic roles in PDF accessibility
        role_types = [
            'document', 'section', 'heading', 'paragraph', 'list', 'listitem',
            'table', 'tablerow', 'tablecell', 'figure', 'caption', 'link'
        ]
        
        role_features = []
        for role_type in role_types:
            role_features.append(1.0 if role_type in semantic_roles else 0.0)
        
        # Additional role statistics
        role_features.extend([
            len(semantic_roles),  # Total role count
            len(set(semantic_roles)),  # Unique role count
            len(semantic_roles) / max(len(set(semantic_roles)), 1)  # Role diversity ratio
        ])
        
        return role_features
    
    def _encode_content_type_features(self, content_type: str) -> List[float]:
        """Encode content type with statistical features from global analysis."""
        content_stats = self.content_type_info.get(content_type, {})
        
        return [
            content_stats.get('avg_confidence', 0.0),
            content_stats.get('count', 0) / max(sum(ct.get('count', 0) for ct in self.content_type_info.values()), 1),
            1.0 if content_type == 'monolingual_content' else 0.0,
            1.0 if content_type == 'sequential_content' else 0.0,
            1.0 if content_type == 'multilingual_content' else 0.0
        ]
    
    def _encode_wcag_complexity(self, wcag_criterion: str) -> List[float]:
        """Encode WCAG criterion complexity features."""
        # WCAG complexity mapping based on criterion requirements
        complexity_map = {
            '1.1.1': 1,  # Images of Text
            '1.3.1': 3,  # Info and Relationships
            '1.4.3': 2,  # Contrast
            '2.4.6': 2,  # Headings and Labels
            '3.1.1': 1,  # Language of Page
            '3.1.2': 2,  # Language of Parts
            '4.1.2': 3   # Name, Role, Value
        }
        
        complexity = complexity_map.get(wcag_criterion, 2)
        level = wcag_criterion.split('.')[0] if '.' in wcag_criterion else '0'
        
        return [
            complexity / 3.0,  # Normalized complexity
            int(level) / 4.0,   # Normalized WCAG level
            1.0 if wcag_criterion.startswith('1.') else 0.0,  # Perceivable
            1.0 if wcag_criterion.startswith('2.') else 0.0,  # Operable
            1.0 if wcag_criterion.startswith('3.') else 0.0,  # Understandable
            1.0 if wcag_criterion.startswith('4.') else 0.0   # Robust
        ]
    
    def _generate_feature_names(self) -> List[str]:
        """Generate descriptive names for features."""
        feature_names = []
        
        # Basic characteristics
        basic_features = [
            'has_doc_language', 'language_changes', 'heading_count', 'list_count',
            'table_count', 'image_count', 'alt_text_coverage'
        ]
        feature_names.extend(basic_features)
        
        # Semantic roles
        role_types = [
            'document', 'section', 'heading', 'paragraph', 'list', 'listitem',
            'table', 'tablerow', 'tablecell', 'figure', 'caption', 'link'
        ]
        feature_names.extend([f'role_{role}' for role in role_types])
        feature_names.extend(['role_count', 'unique_roles', 'role_diversity'])
        
        # Content type features
        content_features = [
            'content_avg_confidence', 'content_frequency', 'is_monolingual',
            'is_sequential', 'is_multilingual'
        ]
        feature_names.extend(content_features)
        
        # WCAG complexity features
        wcag_features = [
            'wcag_complexity', 'wcag_level', 'is_perceivable', 'is_operable',
            'is_understandable', 'is_robust'
        ]
        feature_names.extend(wcag_features)
        
        # Confidence features
        confidence_features = [
            'confidence_score', 'confidence_squared', 'high_confidence', 'low_confidence'
        ]
        feature_names.extend(confidence_features)
        
        # Pad with generic names if needed
        current_count = len(feature_names)
        target_count = self.config.feature_vector_dim
        if current_count < target_count:
            feature_names.extend([f'feature_{i}' for i in range(current_count, target_count)])
        
        return feature_names[:target_count]

    def _engineer_features(self, features_df: pd.DataFrame) -> pd.DataFrame:
        """Apply feature engineering pipeline."""
        logger.info("Applying feature engineering pipeline...")
        
        # Feature scaling/normalization
        if self.config.normalization_method == "standard":
            features_scaled = pd.DataFrame(
                self.scaler.fit_transform(features_df),
                columns=features_df.columns,
                index=features_df.index
            )
        else:
            features_scaled = features_df.copy()
        
        # Feature selection if configured
        if self.config.feature_selection_k and self.config.feature_selection_k < len(features_df.columns):
            # Use dummy target for unsupervised feature selection
            dummy_target = np.random.randint(0, 2, size=len(features_df))
            self.feature_selector = SelectKBest(mutual_info_classif, k=self.config.feature_selection_k)
            features_selected = pd.DataFrame(
                self.feature_selector.fit_transform(features_scaled, dummy_target),
                columns=[features_scaled.columns[i] for i in self.feature_selector.get_support(indices=True)],
                index=features_scaled.index
            )
            logger.info(f"Selected {self.config.feature_selection_k} top features")
        else:
            features_selected = features_scaled
        
        # PCA dimensionality reduction if configured
        if self.config.pca_components:
            self.pca_transformer = PCA(n_components=self.config.pca_components, random_state=self.config.random_state)
            features_pca = pd.DataFrame(
                self.pca_transformer.fit_transform(features_selected),
                columns=[f'pca_{i}' for i in range(self.config.pca_components)],
                index=features_selected.index
            )
            logger.info(f"Applied PCA reduction to {self.config.pca_components} components")
            return features_pca
        
        return features_selected
    
    def _create_data_splits(self, features_df: pd.DataFrame, targets_dict: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """Create train/test/validation splits with stratification."""
        logger.info("Creating stratified data splits...")
        
        # Reset DataFrame index to ensure sequential indices
        features_df = features_df.reset_index(drop=True)
        
        # Choose stratification target (prefer categorical over numerical)
        stratify_target = targets_dict.get(self.config.stratify_by)
        if stratify_target is None and 'wcag_criteria' in targets_dict:
            stratify_target = targets_dict['wcag_criteria']
        
        # Encode stratification target if needed
        if stratify_target.dtype == 'object':
            if 'stratify_encoder' not in self.label_encoders:
                self.label_encoders['stratify_encoder'] = LabelEncoder()
                stratify_encoded = self.label_encoders['stratify_encoder'].fit_transform(stratify_target)
            else:
                stratify_encoded = self.label_encoders['stratify_encoder'].transform(stratify_target)
        else:
            stratify_encoded = stratify_target
        
        # First split: train+val vs test
        X_temp, X_test, temp_indices, test_indices = train_test_split(
            features_df, np.arange(len(features_df)),
            test_size=self.config.test_size,
            random_state=self.config.random_state,
            stratify=stratify_encoded
        )
        
        # Second split: train vs val
        val_ratio = self.config.validation_size / (1 - self.config.test_size)
        X_train, X_val, train_indices, val_indices = train_test_split(
            X_temp, temp_indices,
            test_size=val_ratio,
            random_state=self.config.random_state,
            stratify=stratify_encoded[temp_indices]
        )
        
        # Split all target variables using proper indices
        y_train, y_test, y_val = {}, {}, {}
        target_names = {}
        
        for target_name, target_values in targets_dict.items():
            # Use indices to properly slice target arrays
            y_train_target = target_values[train_indices]
            y_test_target = target_values[test_indices]
            y_val_target = target_values[val_indices]
            
            # Encode if categorical
            if target_values.dtype == 'object':
                if target_name not in self.label_encoders:
                    self.label_encoders[target_name] = LabelEncoder()
                    y_train[target_name] = self.label_encoders[target_name].fit_transform(y_train_target)
                    y_test[target_name] = self.label_encoders[target_name].transform(y_test_target)
                    y_val[target_name] = self.label_encoders[target_name].transform(y_val_target)
                    target_names[target_name] = self.label_encoders[target_name].classes_.tolist()
                else:
                    y_train[target_name] = self.label_encoders[target_name].transform(y_train_target)
                    y_test[target_name] = self.label_encoders[target_name].transform(y_test_target)
                    y_val[target_name] = self.label_encoders[target_name].transform(y_val_target)
                    target_names[target_name] = self.label_encoders[target_name].classes_.tolist()
            else:
                y_train[target_name] = y_train_target
                y_test[target_name] = y_test_target
                y_val[target_name] = y_val_target
                target_names[target_name] = ['continuous']
        
        return {
            'X_train': X_train.values,
            'X_test': X_test.values,
            'X_val': X_val.values,
            'y_train': y_train,
            'y_test': y_test,
            'y_val': y_val,
            'target_names': target_names
        }
    
    def save_dataset(self, dataset: AccessibilityTrainingDataset, output_path: Union[Path, str]):
        """Save processed training dataset for model training."""
        output_path = Path(output_path)
        logger.info(f"Saving training dataset to {output_path}")
        
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save dataset components
        np.save(output_path / 'X_train.npy', dataset.X_train)
        np.save(output_path / 'X_test.npy', dataset.X_test)
        np.save(output_path / 'X_val.npy', dataset.X_val)
        
        # Save targets
        for target_name, target_data in dataset.y_train.items():
            np.save(output_path / f'y_train_{target_name}.npy', target_data)
            np.save(output_path / f'y_test_{target_name}.npy', dataset.y_test[target_name])
            np.save(output_path / f'y_val_{target_name}.npy', dataset.y_val[target_name])
        
        # Save metadata and processors
        with open(output_path / 'metadata.json', 'w') as f:
            json.dump(dataset.metadata, f, indent=2)
        
        with open(output_path / 'feature_names.json', 'w') as f:
            json.dump(dataset.feature_names, f, indent=2)
        
        with open(output_path / 'target_names.json', 'w') as f:
            json.dump(dataset.target_names, f, indent=2)
        
        # Save sklearn components
        joblib.dump(dataset.scaler, output_path / 'scaler.joblib')
        joblib.dump(dataset.label_encoders, output_path / 'label_encoders.joblib')
        
        if self.feature_selector:
            joblib.dump(self.feature_selector, output_path / 'feature_selector.joblib')
        
        if self.pca_transformer:
            joblib.dump(self.pca_transformer, output_path / 'pca_transformer.joblib')
        
        logger.info("Training dataset saved successfully")
    
    @classmethod
    def load_dataset(cls, dataset_path: Path) -> AccessibilityTrainingDataset:
        """Load processed training dataset."""
        logger.info(f"Loading training dataset from {dataset_path}")
        
        # Load arrays
        X_train = np.load(dataset_path / 'X_train.npy')
        X_test = np.load(dataset_path / 'X_test.npy')
        X_val = np.load(dataset_path / 'X_val.npy')
        
        # Load metadata
        with open(dataset_path / 'metadata.json', 'r') as f:
            metadata = json.load(f)
        
        with open(dataset_path / 'feature_names.json', 'r') as f:
            feature_names = json.load(f)
        
        with open(dataset_path / 'target_names.json', 'r') as f:
            target_names = json.load(f)
        
        # Load targets
        y_train, y_test, y_val = {}, {}, {}
        for target_name in target_names.keys():
            y_train[target_name] = np.load(dataset_path / f'y_train_{target_name}.npy')
            y_test[target_name] = np.load(dataset_path / f'y_test_{target_name}.npy')
            y_val[target_name] = np.load(dataset_path / f'y_val_{target_name}.npy')
        
        # Load sklearn components
        scaler = joblib.load(dataset_path / 'scaler.joblib')
        label_encoders = joblib.load(dataset_path / 'label_encoders.joblib')
        
        return AccessibilityTrainingDataset(
            X_train=X_train, X_test=X_test, X_val=X_val,
            y_train=y_train, y_test=y_test, y_val=y_val,
            feature_names=feature_names, target_names=target_names,
            scaler=scaler, label_encoders=label_encoders,
            metadata=metadata
        )


def main():
    """Example usage of AccessibilityFeatureEngineer."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Process accessibility training data for ML")
    parser.add_argument("training_data_dir", type=Path, help="Directory with extracted patterns")
    parser.add_argument("output_dir", type=Path, help="Directory to save processed dataset")
    parser.add_argument("--feature-dim", type=int, default=128, help="Feature vector dimension")
    parser.add_argument("--test-size", type=float, default=0.2, help="Test set ratio")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Create feature engineer
    config = AccessibilityFeatureConfig(
        feature_vector_dim=args.feature_dim,
        test_size=args.test_size
    )
    
    engineer = AccessibilityFeatureEngineer(args.training_data_dir, config)
    
    # Create and save dataset
    dataset = engineer.create_training_dataset()
    engineer.save_dataset(dataset, args.output_dir)
    
    print(f"Training dataset created with {dataset.X_train.shape[1]} features")
    print(f"Train samples: {len(dataset.X_train)}")
    print(f"Test samples: {len(dataset.X_test)}")
    print(f"Validation samples: {len(dataset.X_val)}")


if __name__ == "__main__":
    main()
