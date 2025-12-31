"""
Batch Processing Engine
Process multiple files at once for OCR, Structure, and VL operations
"""
import os
import tempfile
import json
import concurrent.futures
from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass
from enum import Enum


class BatchStatus(Enum):
    """Status of a batch job"""
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'


@dataclass
class BatchJob:
    """Represents a batch processing job"""
    job_id: str
    job_type: str  # 'ocr', 'structure', 'vl'
    files: List[str]
    status: BatchStatus
    progress: int
    total: int
    results: List[Dict]
    errors: List[Dict]
    options: Dict


class BatchProcessor:
    """Handles batch processing of multiple files"""

    # Maximum concurrent workers
    MAX_WORKERS = 4

    def __init__(self):
        """Initialize batch processor"""
        self._jobs: Dict[str, BatchJob] = {}
        self._job_counter = 0

    def _generate_job_id(self) -> str:
        """Generate unique job ID"""
        self._job_counter += 1
        return f"batch_{self._job_counter}"

    def create_job(self, job_type: str, files: List[str], 
                   options: Dict = None) -> str:
        """
        Create a new batch job

        Args:
            job_type: Type of processing ('ocr', 'structure', 'vl')
            files: List of file paths to process
            options: Processing options

        Returns:
            job_id for tracking
        """
        job_id = self._generate_job_id()
        
        job = BatchJob(
            job_id=job_id,
            job_type=job_type,
            files=files,
            status=BatchStatus.PENDING,
            progress=0,
            total=len(files),
            results=[],
            errors=[],
            options=options or {},
        )
        
        self._jobs[job_id] = job
        return job_id

    def get_job(self, job_id: str) -> Optional[Dict]:
        """Get job status and results"""
        job = self._jobs.get(job_id)
        if not job:
            return None
        
        return {
            'job_id': job.job_id,
            'job_type': job.job_type,
            'status': job.status.value,
            'progress': job.progress,
            'total': job.total,
            'percent': round(job.progress / job.total * 100, 1) if job.total > 0 else 0,
            'results_count': len(job.results),
            'errors_count': len(job.errors),
            'results': job.results,
            'errors': job.errors,
        }

    def process_ocr_batch(self, job_id: str, ocr_engine) -> Dict:
        """
        Process batch OCR job

        Args:
            job_id: Job ID
            ocr_engine: Initialized OCR engine

        Returns:
            Final job status
        """
        job = self._jobs.get(job_id)
        if not job:
            return {'error': 'Job not found'}

        job.status = BatchStatus.PROCESSING

        for i, file_path in enumerate(job.files):
            try:
                result = ocr_engine.detect_text(file_path)
                job.results.append({
                    'file': os.path.basename(file_path),
                    'index': i,
                    'success': True,
                    'data': result,
                })
            except Exception as e:
                job.errors.append({
                    'file': os.path.basename(file_path),
                    'index': i,
                    'error': str(e),
                })
            
            job.progress = i + 1

        job.status = BatchStatus.COMPLETED if not job.errors else BatchStatus.COMPLETED
        return self.get_job(job_id)

    def process_structure_batch(self, job_id: str, structure_engine) -> Dict:
        """
        Process batch structure parsing job

        Args:
            job_id: Job ID
            structure_engine: Initialized Structure engine

        Returns:
            Final job status
        """
        job = self._jobs.get(job_id)
        if not job:
            return {'error': 'Job not found'}

        job.status = BatchStatus.PROCESSING

        for i, file_path in enumerate(job.files):
            try:
                result = structure_engine.parse_document(file_path)
                job.results.append({
                    'file': os.path.basename(file_path),
                    'index': i,
                    'success': True,
                    'data': result,
                })
            except Exception as e:
                job.errors.append({
                    'file': os.path.basename(file_path),
                    'index': i,
                    'error': str(e),
                })
            
            job.progress = i + 1

        job.status = BatchStatus.COMPLETED
        return self.get_job(job_id)

    def process_vl_batch(self, job_id: str, vl_engine) -> Dict:
        """
        Process batch VL parsing job

        Args:
            job_id: Job ID
            vl_engine: Initialized VL engine

        Returns:
            Final job status
        """
        job = self._jobs.get(job_id)
        if not job:
            return {'error': 'Job not found'}

        job.status = BatchStatus.PROCESSING

        for i, file_path in enumerate(job.files):
            try:
                result = vl_engine.parse_document(file_path)
                job.results.append({
                    'file': os.path.basename(file_path),
                    'index': i,
                    'success': True,
                    'data': result,
                })
            except Exception as e:
                job.errors.append({
                    'file': os.path.basename(file_path),
                    'index': i,
                    'error': str(e),
                })
            
            job.progress = i + 1

        job.status = BatchStatus.COMPLETED
        return self.get_job(job_id)

    def cancel_job(self, job_id: str) -> bool:
        """Cancel a pending or running job"""
        job = self._jobs.get(job_id)
        if not job:
            return False
        
        if job.status in [BatchStatus.PENDING, BatchStatus.PROCESSING]:
            job.status = BatchStatus.CANCELLED
            return True
        return False

    def delete_job(self, job_id: str) -> bool:
        """Delete a job from memory"""
        if job_id in self._jobs:
            del self._jobs[job_id]
            return True
        return False

    def list_jobs(self) -> List[Dict]:
        """List all jobs"""
        return [self.get_job(job_id) for job_id in self._jobs.keys()]

    def export_results(self, job_id: str, output_dir: str = None) -> Dict:
        """
        Export batch results to files

        Args:
            job_id: Job ID
            output_dir: Output directory

        Returns:
            Dict with export info
        """
        job = self._jobs.get(job_id)
        if not job:
            return {'error': 'Job not found'}

        if output_dir is None:
            output_dir = tempfile.mkdtemp()

        os.makedirs(output_dir, exist_ok=True)

        # Export combined results
        combined_path = os.path.join(output_dir, f'{job_id}_results.json')
        with open(combined_path, 'w', encoding='utf-8') as f:
            json.dump({
                'job_id': job.job_id,
                'job_type': job.job_type,
                'total_files': job.total,
                'successful': len(job.results),
                'failed': len(job.errors),
                'results': job.results,
                'errors': job.errors,
            }, f, ensure_ascii=False, indent=2)

        # Export individual results
        individual_dir = os.path.join(output_dir, 'individual')
        os.makedirs(individual_dir, exist_ok=True)

        for result in job.results:
            file_name = os.path.splitext(result['file'])[0]
            result_path = os.path.join(individual_dir, f'{file_name}_result.json')
            with open(result_path, 'w', encoding='utf-8') as f:
                json.dump(result['data'], f, ensure_ascii=False, indent=2)

        return {
            'success': True,
            'output_dir': output_dir,
            'combined_file': combined_path,
            'individual_dir': individual_dir,
            'total_exported': len(job.results),
        }
