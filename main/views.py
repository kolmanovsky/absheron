from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.http import Http404
from urllib.parse import unquote as urlunquote


from core.models import Text, Image, Node


# ── Главная: последние тексты и изображения ─────────────────────────────────────
def index(request):
    latest_texts = (
        Text.objects
        .select_related("created_by")
        .prefetch_related("tags")
        .order_by("-created_at")[:10]
    )
    latest_images = (
        Image.objects
        .select_related("uploaded_by")
        .prefetch_related("tags")
        .order_by("-uploaded_at")[:12]
    )
    return render(request, "main/index.html", {
        "latest_texts": latest_texts,
        "latest_images": latest_images,
    })


# ── Списки с пагинацией и фильтром по тегу ──────────────────────────────────────
def text_list(request):
    tag = request.GET.get('tag')
    qs = Text.objects.select_related("created_by").prefetch_related("tags").order_by('-created_at')
    if tag:
        qs = qs.filter(tags__name=tag)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'main/text_list.html', {
        'page_obj': page_obj,
        'tag': tag,
    })


def image_list(request):
    tag = request.GET.get('tag')
    qs = Image.objects.select_related("uploaded_by").prefetch_related("tags").order_by('-uploaded_at')
    if tag:
        qs = qs.filter(tags__name=tag)
    paginator = Paginator(qs, 24)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'main/image_list.html', {
        'page_obj': page_obj,
        'tag': tag,
    })


# ── Детальные страницы ─────────────────────────────────────────────────────────
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


# ── Дерево узлов ────────────────────────────────────────────────────────────────
def _resolve_node_by_path(path: str):
    """
    Разбирает путь вида "root/child/subchild" → возвращает найденный Node или None для корня.
    Бросает Http404, если какой-то сегмент не найден.
    """
    path = (path or "").strip("/")
    if not path:
        return None  # корень дерева
    parts = [p for p in path.split("/") if p]
    parent = None
    node = None
    for slug in parts:
        try:
            node = Node.objects.get(parent=parent, slug=slug, is_published=True)
        except Node.DoesNotExist:
            raise Http404("Node not found")
        parent = node
    return node


def node_by_path(request, path=""):
    """
    /tree/ → список корневых узлов
    /tree/a/b/c → страница узла c (подразделы + прикреплённые тексты/картинки)
    """
    path = urlunquote(path)
    node = _resolve_node_by_path(path)

    if node is None:
        roots = Node.objects.filter(parent__isnull=True, is_published=True).order_by('position', 'title')
        return render(request, "main/node_root.html", {"nodes": roots})

    children = node.children.filter(is_published=True).order_by('position', 'title')
    texts = node.texts.select_related("created_by").prefetch_related("tags").all()
    images = node.images.select_related("uploaded_by").prefetch_related("tags").all()

    return render(request, "main/node_detail.html", {
        "node": node,
        "children": children,
        "texts": texts,
        "images": images,
    })
