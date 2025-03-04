from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from .models import UploadedFile
from tasks.tasks import process_file
from tasks.models import ProcessingTask

# Create your views here.

@login_required
def file_upload(request):
    if request.method == 'POST':
        if 'file' not in request.FILES:
            if request.headers.get('Accept') == 'application/json':
                return JsonResponse({
                    'status': 'error',
                    'message': 'No file was uploaded'
                }, status=400)
            messages.error(request, 'No file was uploaded.')
            return redirect('file_upload')

        file = request.FILES['file']
        try:
            uploaded_file = UploadedFile.objects.create(
                user=request.user,
                file=file,
                upload_status='uploading'
            )
            
            # Update status to uploaded after successful save
            uploaded_file.upload_status = 'uploaded'
            uploaded_file.save()
            
            # Return JSON if client accepts JSON
            if request.headers.get('Accept') == 'application/json':
                return JsonResponse({
                    'status': 'success',
                    'message': 'File uploaded successfully',
                    'file_id': uploaded_file.id,
                    'original_filename': uploaded_file.original_filename,
                    'upload_status': uploaded_file.upload_status,
                    'processing_status': uploaded_file.processing_status
                })
            
            messages.success(request, 'File uploaded successfully. You can now trigger processing.')
            return redirect('file_list')
        except Exception as e:
            if 'uploaded_file' in locals():
                uploaded_file.upload_status = 'upload_failed'
                uploaded_file.error_message = str(e)
                uploaded_file.save()
                
            if request.headers.get('Accept') == 'application/json':
                return JsonResponse({
                    'status': 'error',
                    'message': str(e)
                }, status=500)
                
            messages.error(request, f'Error uploading file: {str(e)}')
            return redirect('file_upload')

    context = {
        'max_upload_size': settings.MAX_UPLOAD_SIZE,
        'allowed_extensions': settings.ALLOWED_UPLOAD_EXTENSIONS,
    }
    return render(request, 'files/upload.html', context)

@login_required
def file_list(request):
    files = UploadedFile.objects.filter(user=request.user)
    return render(request, 'files/list.html', {'files': files})

@login_required
def file_detail(request, pk):
    file = get_object_or_404(UploadedFile, pk=pk, user=request.user)
    return render(request, 'files/detail.html', {'file': file})

@login_required
def file_delete(request, pk):
    file = get_object_or_404(UploadedFile, pk=pk, user=request.user)
    if request.method == 'POST':
        file.delete()
        messages.success(request, 'File deleted successfully.')
        return redirect('file_list')
    return render(request, 'files/confirm_delete.html', {'file': file})

@login_required
def file_status(request, pk):
    file = get_object_or_404(UploadedFile, pk=pk, user=request.user)
    return JsonResponse({
        'upload_status': file.upload_status,
        'processing_status': file.processing_status,
        'error_message': file.error_message
    })

@csrf_exempt
@require_http_methods(['POST'])
@login_required
def process_uploaded_file(request, pk):
    try:
        # Get the file
        file = get_object_or_404(UploadedFile, pk=pk, user=request.user)
        
        # Check if file was uploaded successfully
        if file.upload_status != 'uploaded':
            return JsonResponse({
                'status': 'error',
                'message': 'File must be successfully uploaded before processing'
            }, status=400)
            
        # Parse the JSON parameters
        try:
            params = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON parameters'
            }, status=400)
            
        # Store the processing parameters
        file.processing_parameters = params
        file.processing_status = 'processing'
        file.save()
        
        # Start the processing task
        task = process_file.delay(file.id)
        ProcessingTask.objects.create(
            user=request.user,
            file=file,
            task_id=task.id
        )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Processing started',
            'task_id': task.id
        })
        
    except Exception as e:
        if 'file' in locals():
            file.processing_status = 'failed'
            file.error_message = str(e)
            file.save()
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
