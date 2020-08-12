# Generated by Django 3.0.7 on 2020-08-13 02:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BackGroundColor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'background_colors',
            },
        ),
        migrations.CreateModel(
            name='HashTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'hashtags',
            },
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.URLField(max_length=255)),
                ('location', models.CharField(max_length=50, null=True)),
                ('downloads', models.IntegerField(default=0)),
                ('views', models.IntegerField(default=0)),
                ('width', models.IntegerField(null=True)),
                ('height', models.IntegerField(null=True)),
                ('background_color', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='photo.BackGroundColor')),
            ],
            options={
                'db_table': 'photos',
            },
        ),
        migrations.CreateModel(
            name='PhotoHashTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hashtag', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='photo.HashTag')),
                ('photo', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='photo.Photo')),
            ],
            options={
                'db_table': 'photos_hashtags',
            },
        ),
        migrations.CreateModel(
            name='PhotoCollection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('collection', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='account.Collection')),
                ('photo', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='photo.Photo')),
            ],
            options={
                'db_table': 'photos_collections',
            },
        ),
        migrations.AddField(
            model_name='photo',
            name='collection',
            field=models.ManyToManyField(through='photo.PhotoCollection', to='account.Collection'),
        ),
        migrations.AddField(
            model_name='photo',
            name='hashtag',
            field=models.ManyToManyField(through='photo.PhotoHashTag', to='photo.HashTag'),
        ),
        migrations.AddField(
            model_name='photo',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='account.User'),
        ),
    ]