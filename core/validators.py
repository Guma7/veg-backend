from django.core.exceptions import ValidationError
import os
from PIL import Image

def validate_image(value):
    max_size = 5 * 1024 * 1024  # 5MB
    if value.size > max_size:
        raise ValidationError('Imagem deve ser menor que 5MB')
    
    valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in valid_extensions:
        raise ValidationError('Formato de imagem inválido. Use JPG, PNG ou WebP')
    
    img = Image.open(value)
    if img.width > 2000 or img.height > 2000:
        raise ValidationError('A imagem deve ter no máximo 2000x2000 pixels')

def validate_youtube_link(value):
    if value and not ('youtube.com' in value or 'youtu.be' in value):
        raise ValidationError('Invalid YouTube link format')
