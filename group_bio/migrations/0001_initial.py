
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_id', models.IntegerField(default=1, unique=True)),
                ('group_name', models.CharField(default='Bismillah Group A', max_length=255)),
                ('class_name', models.CharField(default='Pengantar Keamanan Perangkat Lunak', max_length=255)),
                ('year', models.IntegerField(default=2024)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'Group Info',
            },
        ),
        migrations.CreateModel(
            name='GroupMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nim', models.CharField(max_length=20)),
                ('full_name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(blank=True, max_length=20)),
                ('role', models.CharField(choices=[('ketua', 'Ketua Kelompok'), ('anggota', 'Anggota')], default='anggota', max_length=50)),
                ('bio', models.TextField(blank=True)),
                ('profile_image', models.URLField(blank=True)),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified_at', models.DateTimeField(auto_now=True)),
                ('last_modified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='modified_group_members', to=settings.AUTH_USER_MODEL)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='group_member', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Group Members',
                'ordering': ['-role', 'full_name'],
            },
        ),
        migrations.CreateModel(
            name='GroupTheme',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_id', models.IntegerField(default=1, unique=True)),
                ('primary_color', models.CharField(default='#3498db', max_length=7)),
                ('secondary_color', models.CharField(default='#2c3e50', max_length=7)),
                ('accent_color', models.CharField(default='#e74c3c', max_length=7)),
                ('font_family', models.CharField(choices=[('Arial', 'Arial'), ('Verdana', 'Verdana'), ('Georgia', 'Georgia'), ('Times New Roman', 'Times New Roman'), ('Courier New', 'Courier New'), ('Trebuchet MS', 'Trebuchet MS'), ('Comic Sans MS', 'Comic Sans MS')], default='Arial', max_length=50)),
                ('font_size_base', models.IntegerField(default=16, help_text='Base font size in pixels')),
                ('background_color', models.CharField(default='#ffffff', max_length=7)),
                ('text_color', models.CharField(default='#333333', max_length=7)),
                ('modification_history', models.JSONField(default=list, help_text='Audit trail of all modifications')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('last_modified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='modified_group_themes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Group Themes',
            },
        ),
    ]
