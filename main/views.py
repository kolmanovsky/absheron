from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from core.models import Text, Image  # если app не core — поправь

def index(request):
    latest_texts = (
        Text.objects.select_related("created_by")
        .prefetch_related("tags").order_by("-created_at")[:10]
    )
    latest_images = (
        Image.objects.select_related("uploaded_by")
        .prefetch_related("tags").order_by("-uploaded_at")[:12]
    )
    return render(request, "main/index.html", {
        "latest_texts": latest_texts,
        "latest_images": latest_images,
    })

def text_detail(request, pk):
    text = get_object_or_404(
        Text.objects.select_related("created_by").prefetch_related("tags"),
        pk=pk,
    )
    return render(request, "main/text_detail.html", {"text": text})

def image_detail(request, pk):
    image = get_object_or_404(
        Image.objects.select_related("uploaded_by").prefetch_related("tags"),
        pk=pk,
    )
    return render(request, "main/image_detail.html", {"image": image})

def text_list(request):
    tag = request.GET.get('tag')
    qs = Text.objects.select_related("created_by").prefetch_related("tags").order_by('-created_at')
    if tag:
        qs = qs.filter(tags__name=tag)
    paginator = Paginator(qs, 10)  # 10 на страницу
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    return render(request, 'main/text_list.html', {
        'page_obj': page_obj,
        'tag': tag,
    })

def image_list(request):
    tag = request.GET.get('tag')
    qs = Image.objects.select_related("uploaded_by").prefetch_related("tags").order_by('-uploaded_at')
    if tag:
        qs = qs.filter(tags__name=tag)
    paginator = Paginator(qs, 24)  # 24 миниатюры на страницу
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    return render(request, 'main/image_list.html', {
        'page_obj': page_obj,
        'tag': tag,
    })
    

