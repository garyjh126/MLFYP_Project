# Generated by Django 3.0.8 on 2020-07-29 07:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rank', models.CharField(max_length=2)),
                ('suit', models.CharField(max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='CardHolding',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='first', to='poker.Card')),
                ('second', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='second', to='poker.Card')),
            ],
        ),
        migrations.CreateModel(
            name='CommunityCards',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('flop_0', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='flop_0', to='poker.Card')),
                ('flop_1', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='flop_1', to='poker.Card')),
                ('flop_2', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='flop_2', to='poker.Card')),
                ('river', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='river', to='poker.Card')),
                ('turn', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='turn', to='poker.Card')),
            ],
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_pot', models.CharField(max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('community_cards', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='poker.CommunityCards')),
                ('guest_cards', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='guest_cards', to='poker.CardHolding')),
                ('learner_cards', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='learner_cards', to='poker.CardHolding')),
            ],
        ),
    ]