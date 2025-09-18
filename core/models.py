from django.db import models
from django.contrib.auth.models import User
import bleach
from bleach.sanitizer import Cleaner
from bleach.css_sanitizer import CSSSanitizer


ALLOWED_TAGS = [
    "p", "br", "span", "strong", "em", "ul", "ol", "li", "a",
]
ALLOWED_ATTRS = {
    "a": {"href", "title", "target", "rel"},
    "span": {"style"},
}
ALLOWED_PROTOCOLS = {"http", "https", "mailto"}

CSS_ALLOWED_PROPERTIES = [
    "color", "background-color", "font-size", "font-weight",
    "font-style", "text-decoration",
]

css_sanitizer = CSSSanitizer(allowed_css_properties=CSS_ALLOWED_PROPERTIES)

cleaner = Cleaner(
    tags=ALLOWED_TAGS,
    attributes=ALLOWED_ATTRS,
    protocols=ALLOWED_PROTOCOLS,
    strip=True,
    css_sanitizer=css_sanitizer,
)


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Text(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag, blank=True)
    
    def clean(self):
        if self.body:
            # 1) чистим HTML от лишних тегов/атрибутов/стилей
            sanitized = cleaner.clean(self.body)
            # 2) превращаем «голые» URL в ссылки (а теги <a> из шага 1 остаются)
            sanitized = bleach.linkify(
                sanitized,
                skip_tags=["pre", "code"],  # не линковать внутри кода
            )
            self.body = sanitized

    def __str__(self):
        return self.title


class Image(models.Model):
    file = models.ImageField(upload_to='images/')
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return f"Image {self.id} ({', '.join(t.name for t in self.tags.all())})"
    
class Node(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    parent = models.ForeignKey('self', null=True, blank=True,
                               related_name='children', on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    position = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # контент, прикреплённый к узлу (многие-ко-многим через through)
    texts = models.ManyToManyField('Text', through='NodeText', blank=True, related_name='nodes')
    images = models.ManyToManyField('Image', through='NodeImage', blank=True, related_name='nodes')

    class Meta:
        unique_together = [('parent', 'slug')]
        ordering = ['position', 'title']

    def __str__(self):
        return self.title

    @property
    def path_slugs(self):
        # список слагов от корня до текущего
        chain = []
        node = self
        while node is not None:
            chain.append(node.slug)
            node = node.parent
        return list(reversed(chain))

    def get_absolute_url(self):
        # /tree/<slug1>/<slug2>/...
        return "/tree/" + "/".join(self.path_slugs) + "/"

class NodeText(models.Model):
    node = models.ForeignKey(Node, on_delete=models.CASCADE)
    text = models.ForeignKey('Text', on_delete=models.CASCADE)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = [('node', 'text')]
        ordering = ['position', 'text__title']

class NodeImage(models.Model):
    node = models.ForeignKey(Node, on_delete=models.CASCADE)
    image = models.ForeignKey('Image', on_delete=models.CASCADE)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = [('node', 'image')]
        ordering = ['position', 'image__uploaded_at']
