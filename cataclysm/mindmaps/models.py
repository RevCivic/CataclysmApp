from django.db import models

class MindMap(models.Model):
    title = models.CharField(max_length=200, verbose_name="Mind Map Title")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class MindMapNode(models.Model):
    mindmap = models.ForeignKey(MindMap, related_name='nodes', on_delete=models.CASCADE)
    label = models.CharField(max_length=200)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)
    notes = models.TextField(blank=True, null=True)
    x = models.FloatField(default=0)
    y = models.FloatField(default=0)

    def __str__(self):
        return self.label
