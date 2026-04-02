
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group_bio', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupmember',
            name='profile_image',
            field=models.ImageField(blank=True, null=True, upload_to='profile_images/'),
        ),
    ]
