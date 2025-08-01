# Generated by Django 5.2.3 on 2025-07-27 12:56

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('submit', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Problem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('input_format', models.TextField()),
                ('output_format', models.TextField()),
                ('constraints', models.TextField()),
                ('sample_input', models.TextField()),
                ('sample_output', models.TextField()),
                ('time_limit', models.IntegerField(default=1000)),
                ('memory_limit', models.IntegerField(default=256)),
                ('difficulty', models.CharField(choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')], default='easy', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='codesubmission',
            name='input_data',
        ),
        migrations.RemoveField(
            model_name='codesubmission',
            name='output_data',
        ),
        migrations.AddField(
            model_name='codesubmission',
            name='execution_time',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='codesubmission',
            name='memory_used',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='codesubmission',
            name='passed_tests',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='codesubmission',
            name='total_tests',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='codesubmission',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='codesubmission',
            name='verdict',
            field=models.CharField(choices=[('AC', 'Accepted'), ('WA', 'Wrong Answer'), ('TLE', 'Time Limit Exceeded'), ('RTE', 'Runtime Error'), ('CE', 'Compilation Error'), ('MLE', 'Memory Limit Exceeded'), ('PENDING', 'Pending')], default='PENDING', max_length=10),
        ),
        migrations.AddField(
            model_name='codesubmission',
            name='problem',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='submit.problem'),
        ),
        migrations.CreateModel(
            name='TestCase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('input_data', models.TextField()),
                ('expected_output', models.TextField()),
                ('is_sample', models.BooleanField(default=False)),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='test_cases', to='submit.problem')),
            ],
        ),
        migrations.CreateModel(
            name='TestResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_output', models.TextField()),
                ('verdict', models.CharField(choices=[('AC', 'Accepted'), ('WA', 'Wrong Answer'), ('TLE', 'Time Limit Exceeded'), ('RTE', 'Runtime Error'), ('CE', 'Compilation Error'), ('MLE', 'Memory Limit Exceeded'), ('PENDING', 'Pending')], max_length=10)),
                ('execution_time', models.IntegerField(blank=True, null=True)),
                ('memory_used', models.IntegerField(blank=True, null=True)),
                ('submission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='test_results', to='submit.codesubmission')),
                ('test_case', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='submit.testcase')),
            ],
        ),
    ]
