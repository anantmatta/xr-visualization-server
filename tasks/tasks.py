from celery import shared_task
from django.core.files import File
from files.models import UploadedFile
from .models import ProcessingTask
from .sionnaRT.preprocessing import preprocess_zip_file
from .sionnaRT.simulation import run_simulation
from django.conf import settings
import time
import os
from pathlib import Path

@shared_task(bind=True)
def process_file(self, file_id):
    try:
        file_instance = UploadedFile.objects.get(id=file_id)
        
        file_instance.processing_status = 'processing'
        file_instance.save()

        task, created = ProcessingTask.objects.get_or_create(
            task_id=self.request.id,
            defaults={
                'user': file_instance.user,
                'file': file_instance,
                'status': 'running'
            }
        )

        if not created:
            task.status = 'running'
            task.save()

        params = file_instance.processing_parameters or {}
        
        if file_instance.file.name.lower().endswith('.zip'):
            preprocess_result = preprocess_zip_file(file_instance.file.path, file_id)
            if preprocess_result['status'] == 'error':
                raise Exception(f"Preprocessing failed: {preprocess_result['message']}")

            params['extracted_path'] = preprocess_result['extracted_path']
            file_instance.processing_parameters = params
            file_instance.save()

            simulation_result = run_simulation(params['extracted_path'], file_instance)

            if simulation_result['status'] == 'error':
                raise Exception(f"Simulation failed: {simulation_result['message']}")
            
            params['simulation_result'] = simulation_result
            file_instance.processing_parameters = params
            file_instance.save()

        file_instance.processing_status = 'completed'
        file_instance.error_message = ""
        file_instance.save()

        task.status = 'completed'
        task.save()

        return {
            'status': 'success',
            'file_id': file_id,
            'message': 'Simulation completed successfully',
            'simulation_result': params.get('simulation_result')
        }

    except UploadedFile.DoesNotExist:
        return {
            'status': 'error',
            'message': f'File with id {file_id} does not exist'
        }
    except Exception as e:
        file_instance.processing_status = 'failed'
        file_instance.error_message = str(e)
        file_instance.save()

        task.status = 'failed'
        task.error_message = str(e)
        task.save()

        return {
            'status': 'error',
            'message': str(e)
        } 