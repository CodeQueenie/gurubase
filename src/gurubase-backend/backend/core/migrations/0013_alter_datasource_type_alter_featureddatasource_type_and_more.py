# Generated by Django 4.2.13 on 2025-01-09 13:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_gurutype_has_sitemap_added_questions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datasource',
            name='type',
            field=models.CharField(choices=[('PDF', 'PDF'), ('WEBSITE', 'WEBSITE'), ('YOUTUBE', 'YOUTUBE'), ('GITHUB_REPO', 'GITHUB_REPO')], default='PDF', max_length=50),
        ),
        migrations.AlterField(
            model_name='featureddatasource',
            name='type',
            field=models.CharField(choices=[('PDF', 'Pdf'), ('WEBSITE', 'Website'), ('YOUTUBE', 'Youtube'), ('GITHUB_REPO', 'Github Repo')], default='PDF', max_length=50),
        ),
        migrations.CreateModel(
            name='GitHubFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(max_length=2000)),
                ('content', models.TextField()),
                ('size', models.PositiveIntegerField()),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('data_source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='github_files', to='core.datasource')),
            ],
            options={
                'indexes': [models.Index(fields=['path'], name='core_github_path_2d0006_idx')],
                'unique_together': {('data_source', 'path')},
            },
        ),
    ]
