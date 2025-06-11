# Generated manually

from django.db import migrations
import cloudinary.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_userprofile_created_at_userprofile_profile_image_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='profile_image',
            field=cloudinary.models.CloudinaryField(
                blank=True,
                max_length=255,
                null=True,
                verbose_name='image',
                folder='profile_images',
                transformation={
                    'quality': 'auto',
                    'fetch_format': 'auto'
                }
            ),
        ),
    ]