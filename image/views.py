from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from .tasks import process_image
from .models import Product
from django.db.models import Q
from django_celery_results.models import TaskResult
import re


def ocr_image_upload(request):
    if request.method == 'POST' and request.FILES['image']:
        image = request.FILES['image']
        fs = FileSystemStorage()
        filename = fs.save(image.name, image)
        uploaded_file_url = fs.url(filename)

        # Make sure to call the Celery task, not the function directly
        task = process_image.delay(fs.path(filename))

        return redirect('ocr_result', task_id=task.id)
    return render(request, 'upload.html')

def ocr_result(request, task_id):
    result = process_image.AsyncResult(task_id)
    if result.state == 'SUCCESS':
        raw_text = result.result
        text = clean_text(raw_text)

        # Split text into lines for better formatting
        text_lines = text.splitlines()

        products = search_database(text)
        
        # Debugging: Print the query and the products found
        print(f"OCR Text: {text}")
        print(f"Products Found: {products}")

        return render(request, 'ocr_result.html', {'text_lines': text_lines, 'products': products})
    elif result.state == 'PENDING':
        return render(request, 'ocr_result.html', {'text_lines': ['Processing...']})
    elif result.state == 'FAILURE':
        # Fetch the detailed error info from TaskResult
        task_result = TaskResult.objects.get(task_id=task_id)
        error_message = task_result.result
        return render(request, 'ocr_result.html', {'text_lines': [f'An error occurred: {error_message}']})
    else:
        return render(request, 'ocr_result.html', {'text_lines': ['An unexpected state occurred']})



def clean_text(text):
    # Split the text into words
    words = text.split()
    # Join the words with two spaces in between
    clean_text = '  '.join(words)
    return clean_text



def search_database(query):
    words = query.split()
    query_set = Q()
    for word in words:
        query_set |= Q(name__icontains=word) | Q(description__icontains=word)
    
    products = Product.objects.filter(query_set).distinct()

    # Debugging: Print the query and the resulting queryset
    print(f"Search Query: {words}")
    print(f"Products Matched: {products}")

    return products

