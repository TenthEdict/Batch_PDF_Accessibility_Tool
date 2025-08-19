#!/usr/bin/env python3
"""
Thread-Safe Adaptive ML Enhancement Module

This module provides thread-safe machine learning-enhanced document processing with:
- Concurrent-access-safe knowledge base management
- File locking for knowledge base operations
- Thread-local caching for performance optimization
- Safe document similarity analysis in parallel environments
- Atomic updates to prevent data corruption

Features:
- Thread-safe document similarity analysis using feature vectors
- Concurrent-safe OCR configuration testing and optimization
- Atomic knowledge base updates with file locking
- Thread-local caching for improved parallel performance
- Safe pattern storage and retrieval for similar documents
"""

import logging
import threading
import fcntl
import tempfile
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
import time
import hashlib

# Import the original adaptive ML enhancer
from .adaptive_ml_enhancer import (
    AdaptiveMLEnhancer as BaseAdaptiveMLEnhancer,
    DocumentProfile,
    OCRConfigurationTest,
    ML_DEPS_AVAILABLE
)

logger = logging.getLogger(__name__)


class ThreadSafeKnowledgeBase:
    """
    Thread-safe knowledge base manager with file locking.
    
    Provides safe concurrent access to the ML knowledge base
    with atomic operations and file locking to prevent corruption.
    """
    
    def __init__(self, knowledge_base_dir: Path):
        """
        Initialize thread-safe knowledge base.
        
        Args:
            knowledge_base_dir: Directory for knowledge base storage
        """
        self.knowledge_base_dir = knowledge_base_dir
        self.knowledge_base_dir.mkdir(parents=True, exist_ok=True)
        
        # Lock files for atomic operations
        self.profiles_file = self.knowledge_base_dir / "document_profiles.pkl"
        self.scaler_file = self.knowledge_base_dir / "feature_scaler.pkl"
        self.similarity_model_file = self.knowledge_base_dir / "similarity_model.pkl"
        
        self.profiles_lock_file = self.knowledge_base_dir / ".profiles.lock"
        self.scaler_lock_file = self.knowledge_base_dir / ".scaler.lock"
        self.similarity_lock_file = self.knowledge_base_dir / ".similarity.lock"
        
        # Thread-local cache
        self._local_cache = threading.local()
        self._cache_lock = threading.Lock()
        
        # Cache metadata
        self._cache_timestamps = {}
        self.cache_timeout = 300  # 5 minutes cache timeout
        
        logger.info("Thread-safe knowledge base initialized")
    
    def _get_file_lock(self, lock_file: Path, timeout: float = 10.0):
        """
        Acquire file lock with timeout.
        
        Args:
            lock_file: Path to lock file
            timeout: Maximum time to wait for lock
            
        Returns:
            File object with acquired lock
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                lock_fd = open(lock_file, 'w')
                fcntl.flock(lock_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                return lock_fd
            except (IOError, OSError):
                if 'lock_fd' in locals():
                    lock_fd.close()
                time.sleep(0.1)  # Brief wait before retry
        
        raise TimeoutError(f"Could not acquire lock for {lock_file} within {timeout}s")
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid."""
        if not hasattr(self._local_cache, cache_key):
            return False
        
        timestamp = self._cache_timestamps.get(cache_key, 0)
        return (time.time() - timestamp) < self.cache_timeout
    
    def _set_cache(self, cache_key: str, data: Any):
        """Set data in thread-local cache."""
        setattr(self._local_cache, cache_key, data)
        self._cache_timestamps[cache_key] = time.time()
    
    def _get_cache(self, cache_key: str) -> Any:
        """Get data from thread-local cache."""
        if self._is_cache_valid(cache_key):
            return getattr(self._local_cache, cache_key, None)
        return None
    
    def load_document_profiles(self) -> Dict[str, DocumentProfile]:
        """
        Load document profiles with thread-safe file access.
        
        Returns:
            Dict[str, DocumentProfile]: Document profiles
        """
        cache_key = 'document_profiles'
        
        # Check thread-local cache first
        cached_profiles = self._get_cache(cache_key)
        if cached_profiles is not None:
            return cached_profiles
        
        profiles = {}
        
        if self.profiles_file.exists():
            lock_fd = None
            try:
                # Acquire read lock
                lock_fd = self._get_file_lock(self.profiles_lock_file, timeout=5.0)
                
                # Load profiles
                import pickle
                with open(self.profiles_file, 'rb') as f:
                    profiles = pickle.load(f)
                
                logger.debug(f"Loaded {len(profiles)} document profiles from disk")
                
            except Exception as e:
                logger.warning(f"Could not load document profiles: {e}")
                profiles = {}
            finally:
                if lock_fd:
                    fcntl.flock(lock_fd.fileno(), fcntl.LOCK_UN)
                    lock_fd.close()
        
        # Cache the loaded profiles
        self._set_cache(cache_key, profiles)
        return profiles
    
    def save_document_profiles(self, profiles: Dict[str, DocumentProfile]) -> bool:
        """
        Save document profiles with atomic write operation.
        
        Args:
            profiles: Document profiles to save
            
        Returns:
            bool: True if successful
        """
        lock_fd = None
        try:
            # Acquire write lock
            lock_fd = self._get_file_lock(self.profiles_lock_file, timeout=10.0)
            
            # Atomic write using temporary file
            with tempfile.NamedTemporaryFile(mode='wb', dir=self.knowledge_base_dir, delete=False) as temp_file:
                import pickle
                pickle.dump(profiles, temp_file)
                temp_file.flush()
                temp_filename = temp_file.name
            
            # Atomic move
            shutil.move(temp_filename, self.profiles_file)
            
            # Update cache
            self._set_cache('document_profiles', profiles.copy())
            
            logger.debug(f"Saved {len(profiles)} document profiles to disk")
            return True
            
        except Exception as e:
            logger.error(f"Could not save document profiles: {e}")
            # Clean up temporary file if it exists
            if 'temp_filename' in locals() and Path(temp_filename).exists():
                try:
                    Path(temp_filename).unlink()
                except:
                    pass
            return False
        finally:
            if lock_fd:
                fcntl.flock(lock_fd.fileno(), fcntl.LOCK_UN)
                lock_fd.close()
    
    def load_ml_models(self) -> Tuple[Any, Any]:
        """
        Load ML models (scaler and similarity model) with thread-safe access.
        
        Returns:
            Tuple[Any, Any]: (feature_scaler, similarity_model)
        """
        cache_key_scaler = 'feature_scaler'
        cache_key_similarity = 'similarity_model'
        
        # Check cache first
        cached_scaler = self._get_cache(cache_key_scaler)
        cached_similarity = self._get_cache(cache_key_similarity)
        
        if cached_scaler is not None and cached_similarity is not None:
            return cached_scaler, cached_similarity
        
        feature_scaler = None
        similarity_model = None
        
        # Load feature scaler
        if self.scaler_file.exists():
            lock_fd = None
            try:
                lock_fd = self._get_file_lock(self.scaler_lock_file, timeout=5.0)
                import joblib
                feature_scaler = joblib.load(self.scaler_file)
            except Exception as e:
                logger.warning(f"Could not load feature scaler: {e}")
            finally:
                if lock_fd:
                    fcntl.flock(lock_fd.fileno(), fcntl.LOCK_UN)
                    lock_fd.close()
        
        # Load similarity model
        if self.similarity_model_file.exists():
            lock_fd = None
            try:
                lock_fd = self._get_file_lock(self.similarity_lock_file, timeout=5.0)
                import joblib
                similarity_model = joblib.load(self.similarity_model_file)
            except Exception as e:
                logger.warning(f"Could not load similarity model: {e}")
            finally:
                if lock_fd:
                    fcntl.flock(lock_fd.fileno(), fcntl.LOCK_UN)
                    lock_fd.close()
        
        # Cache the models
        self._set_cache(cache_key_scaler, feature_scaler)
        self._set_cache(cache_key_similarity, similarity_model)
        
        return feature_scaler, similarity_model
    
    def save_ml_models(self, feature_scaler: Any, similarity_model: Any) -> bool:
        """
        Save ML models with atomic write operations.
        
        Args:
            feature_scaler: Scikit-learn feature scaler
            similarity_model: Similarity model
            
        Returns:
            bool: True if successful
        """
        success = True
        
        # Save feature scaler
        if feature_scaler is not None:
            lock_fd = None
            try:
                lock_fd = self._get_file_lock(self.scaler_lock_file, timeout=10.0)
                
                with tempfile.NamedTemporaryFile(mode='wb', dir=self.knowledge_base_dir, delete=False) as temp_file:
                    import joblib
                    joblib.dump(feature_scaler, temp_file.name)
                    temp_filename = temp_file.name
                
                shutil.move(temp_filename, self.scaler_file)
                self._set_cache('feature_scaler', feature_scaler)
                
            except Exception as e:
                logger.error(f"Could not save feature scaler: {e}")
                success = False
                if 'temp_filename' in locals() and Path(temp_filename).exists():
                    try:
                        Path(temp_filename).unlink()
                    except:
                        pass
            finally:
                if lock_fd:
                    fcntl.flock(lock_fd.fileno(), fcntl.LOCK_UN)
                    lock_fd.close()
        
        # Save similarity model
        if similarity_model is not None:
            lock_fd = None
            try:
                lock_fd = self._get_file_lock(self.similarity_lock_file, timeout=10.0)
                
                with tempfile.NamedTemporaryFile(mode='wb', dir=self.knowledge_base_dir, delete=False) as temp_file:
                    import joblib
                    joblib.dump(similarity_model, temp_file.name)
                    temp_filename = temp_file.name
                
                shutil.move(temp_filename, self.similarity_model_file)
                self._set_cache('similarity_model', similarity_model)
                
            except Exception as e:
                logger.error(f"Could not save similarity model: {e}")
                success = False
                if 'temp_filename' in locals() and Path(temp_filename).exists():
                    try:
                        Path(temp_filename).unlink()
                    except:
                        pass
            finally:
                if lock_fd:
                    fcntl.flock(lock_fd.fileno(), fcntl.LOCK_UN)
                    lock_fd.close()
        
        return success
    
    def invalidate_cache(self):
        """Invalidate all cached data."""
        with self._cache_lock:
            self._cache_timestamps.clear()
            # Clear thread-local cache
            for attr in dir(self._local_cache):
                if not attr.startswith('_'):
                    delattr(self._local_cache, attr)


class ThreadSafeAdaptiveMLEnhancer(BaseAdaptiveMLEnhancer):
    """
    Thread-safe version of AdaptiveMLEnhancer for parallel processing.
    
    Provides all capabilities of the base ML enhancer with added
    thread safety for concurrent document processing.
    """
    
    def __init__(self, component_name: str = "thread_safe_adaptive_ml_enhancer", environment: Optional[str] = None):
        """Initialize thread-safe adaptive ML enhancer."""
        # Initialize base class without calling its __init__ completely
        # to avoid conflicts with knowledge base initialization
        if not ML_DEPS_AVAILABLE:
            raise ImportError("ML dependencies not available. Install with: pip install epubs-accessibility[ml]")
        
        # Initialize EnhancerBase
        from .enhancer_base import EnhancerBase
        EnhancerBase.__init__(self, component_name, environment)
        
        # Initialize thread-safe knowledge base
        self.knowledge_base_dir = Path.home() / ".epubs" / "ml_knowledge"
        self.thread_safe_kb = ThreadSafeKnowledgeBase(self.knowledge_base_dir)
        
        # Configuration files (compatibility with base class)
        self.profiles_file = self.knowledge_base_dir / "document_profiles.pkl"
        self.scaler_file = self.knowledge_base_dir / "feature_scaler.pkl"
        self.similarity_model_file = self.knowledge_base_dir / "similarity_model.pkl"
        
        # Thread-safe access lock
        self._processing_lock = threading.Lock()
        
        # Thread-local storage for ML components
        self._thread_local = threading.local()
        
        # Copy configuration from base class
        self.ocr_config_options = {
            'psm': [3, 6, 7, 8, 11, 13],
            'oem': [1, 2, 3],
            'dpi': [150, 200, 300],
            'preprocessing': ['none', 'adaptive', 'otsu', 'gaussian']
        }
        
        # ML components (compatibility with base class)
        self.feature_scaler = None
        self.similarity_model = None
        
        self.similarity_threshold = 0.8
        self.min_quality_threshold = 0.6
        self.max_config_tests = 5
        
        logger.info("Thread-Safe Adaptive ML Enhancer initialized successfully")
    
    @property
    def document_profiles(self) -> Dict[str, DocumentProfile]:
        """
        Access document profiles from thread-local storage.
        
        Returns:
            Dict[str, DocumentProfile]: Thread-safe document profiles
        """
        # Ensure thread-local components are initialized
        _, _, profiles = self._get_thread_local_components()
        return profiles
    
    @document_profiles.setter
    def document_profiles(self, value: Dict[str, DocumentProfile]):
        """
        Set document profiles in thread-local storage.
        
        Args:
            value: Dictionary of document profiles to store
        """
        # Ensure thread-local storage is initialized
        self._get_thread_local_components()
        self._thread_local.document_profiles = value
    
    @property
    def feature_scaler(self):
        """
        Access feature scaler from thread-local storage.
        
        Returns:
            Feature scaler for thread-safe access
        """
        scaler, _, _ = self._get_thread_local_components()
        return scaler
    
    @feature_scaler.setter
    def feature_scaler(self, value):
        """
        Set feature scaler in thread-local storage.
        
        Args:
            value: Feature scaler to store
        """
        self._get_thread_local_components()
        self._thread_local.feature_scaler = value
    
    @property
    def similarity_model(self):
        """
        Access similarity model from thread-local storage.
        
        Returns:
            Similarity model for thread-safe access
        """
        _, model, _ = self._get_thread_local_components()
        return model
    
    @similarity_model.setter
    def similarity_model(self, value):
        """
        Set similarity model in thread-local storage.
        
        Args:
            value: Similarity model to store
        """
        self._get_thread_local_components()
        self._thread_local.similarity_model = value
    
    def _get_thread_local_components(self) -> Tuple[Any, Any, Dict[str, DocumentProfile]]:
        """Get thread-local ML components."""
        if not hasattr(self._thread_local, 'initialized'):
            # Load knowledge base for this thread
            profiles = self.thread_safe_kb.load_document_profiles()
            feature_scaler, similarity_model = self.thread_safe_kb.load_ml_models()
            
            # Store in thread-local storage
            self._thread_local.document_profiles = profiles
            self._thread_local.feature_scaler = feature_scaler
            self._thread_local.similarity_model = similarity_model
            self._thread_local.initialized = True
            
            logger.debug(f"Initialized thread-local ML components for {threading.current_thread().name}")
        
        return (
            self._thread_local.feature_scaler,
            self._thread_local.similarity_model,
            self._thread_local.document_profiles
        )
    
    def _save_thread_local_updates(self):
        """Save thread-local updates back to knowledge base."""
        if hasattr(self._thread_local, 'document_profiles'):
            # Save document profiles
            success = self.thread_safe_kb.save_document_profiles(self._thread_local.document_profiles)
            if success:
                # Save ML models if they exist
                if hasattr(self._thread_local, 'feature_scaler') and hasattr(self._thread_local, 'similarity_model'):
                    self.thread_safe_kb.save_ml_models(
                        self._thread_local.feature_scaler,
                        self._thread_local.similarity_model
                    )
    
    def analyze_document_similarity(self, input_path: Path, force_analysis: bool = False) -> Tuple[str, Dict[str, float], List[Dict[str, Any]]]:
        """
        Thread-safe document similarity analysis.
        
        Args:
            input_path: Path to document for analysis
            force_analysis: Force analysis even if document exists
            
        Returns:
            Tuple[str, Dict[str, float], List[Dict[str, Any]]]: (document_id, features, similar_documents)
        """
        # Get thread-local components
        feature_scaler, similarity_model, document_profiles = self._get_thread_local_components()
        
        # Generate document ID
        document_id = self._generate_document_id(input_path)
        
        # Check if document already analyzed
        if not force_analysis and document_id in document_profiles:
            profile = document_profiles[document_id]
            similar_docs = self._find_similar_documents_thread_safe(profile.features, document_profiles)
            return document_id, profile.features, similar_docs
        
        # Extract features using base class method
        features = self._extract_document_features(input_path)
        
        # Find similar documents
        similar_docs = self._find_similar_documents_thread_safe(features, document_profiles)
        
        return document_id, features, similar_docs
    
    def _find_similar_documents_thread_safe(self, target_features: Dict[str, float], 
                                          document_profiles: Dict[str, DocumentProfile]) -> List[Dict[str, Any]]:
        """Thread-safe similar document finding."""
        if not document_profiles:
            return []
        
        try:
            import numpy as np
            from sklearn.metrics.pairwise import cosine_similarity
            
            # Prepare feature vectors
            target_vector = np.array([list(target_features.values())])
            
            similar_docs = []
            for doc_id, profile in document_profiles.items():
                try:
                    profile_vector = np.array([list(profile.features.values())])
                    
                    # Ensure compatible dimensions
                    if target_vector.shape[1] != profile_vector.shape[1]:
                        continue
                    
                    similarity = cosine_similarity(target_vector, profile_vector)[0][0]
                    
                    if similarity >= self.similarity_threshold:
                        similar_docs.append({
                            'document_id': doc_id,
                            'similarity': float(similarity),
                            'features': profile.features,
                            'optimal_config': profile.optimal_ocr_config,
                            'confidence': profile.confidence_score,
                            'success_rate': profile.success_rate
                        })
                        
                except Exception as e:
                    logger.warning(f"Error calculating similarity for document {doc_id}: {e}")
                    continue
            
            # Sort by similarity
            similar_docs.sort(key=lambda x: x['similarity'], reverse=True)
            return similar_docs[:5]  # Return top 5 similar documents
            
        except Exception as e:
            logger.error(f"Thread-safe similarity analysis failed: {e}")
            return []
    
    def update_document_profile(self, document_id: str, features: Dict[str, float], 
                              optimal_config: Dict[str, Any], quality_metrics: Dict[str, float],
                              success: bool = True) -> bool:
        """
        Thread-safe document profile update.
        
        Args:
            document_id: Document identifier
            features: Document features
            optimal_config: Optimal OCR configuration
            quality_metrics: Quality metrics
            success: Whether processing was successful
            
        Returns:
            bool: True if update successful
        """
        try:
            # Get thread-local components
            _, _, document_profiles = self._get_thread_local_components()
            
            # Update or create profile
            if document_id in document_profiles:
                profile = document_profiles[document_id]
                profile.optimal_ocr_config = optimal_config
                profile.quality_metrics = quality_metrics
                profile.updated_at = time.time()
                profile.total_attempts += 1
                if success:
                    profile.success_count += 1
            else:
                profile = DocumentProfile(
                    document_id=document_id,
                    features=features,
                    optimal_ocr_config=optimal_config,
                    quality_metrics=quality_metrics,
                    processing_history=[],
                    created_at=time.time(),
                    updated_at=time.time(),
                    success_count=1 if success else 0,
                    total_attempts=1
                )
                document_profiles[document_id] = profile
            
            # Add processing history entry
            history_entry = {
                'timestamp': time.time(),
                'config': optimal_config,
                'quality': quality_metrics,
                'success': success
            }
            profile.processing_history.append(history_entry)
            
            # Keep only last 10 history entries
            if len(profile.processing_history) > 10:
                profile.processing_history = profile.processing_history[-10:]
            
            # Save updates
            self._save_thread_local_updates()
            
            logger.debug(f"Updated document profile for {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update document profile: {e}")
            return False
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Get thread-safe processing statistics."""
        try:
            # Get thread-local components
            _, _, document_profiles = self._get_thread_local_components()
            
            if not document_profiles:
                return {
                    'total_document_profiles': 0,
                    'successful_profiles': 0,
                    'average_confidence': 0.0,
                    'average_success_rate': 0.0,
                    'thread_name': threading.current_thread().name
                }
            
            import numpy as np
            
            successful_profiles = sum(1 for p in document_profiles.values() if p.success_rate > 0.5)
            avg_confidence = np.mean([p.confidence_score for p in document_profiles.values()])
            avg_success_rate = np.mean([p.success_rate for p in document_profiles.values()])
            
            return {
                'total_document_profiles': len(document_profiles),
                'successful_profiles': successful_profiles,
                'average_confidence': float(avg_confidence),
                'average_success_rate': float(avg_success_rate),
                'thread_name': threading.current_thread().name,
                'cache_status': 'thread_local'
            }
            
        except Exception as e:
            logger.error(f"Failed to get processing statistics: {e}")
            return {'error': str(e)}
    
    def invalidate_cache(self):
        """Invalidate all caches."""
        self.thread_safe_kb.invalidate_cache()
        
        # Clear thread-local cache
        if hasattr(self._thread_local, 'initialized'):
            delattr(self._thread_local, 'initialized')
