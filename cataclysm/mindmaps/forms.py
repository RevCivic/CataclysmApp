from django import forms
from .models import MindMap, MindMapNode

class MindMapForm(forms.ModelForm):
    class Meta:
        model = MindMap
        fields = ['title', 'description']

class MindMapNodeForm(forms.ModelForm):
    class Meta:
        model = MindMapNode
        fields = ['mindmap', 'label', 'parent', 'notes', 'x', 'y']
