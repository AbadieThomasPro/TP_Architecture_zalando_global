from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_id', models.PositiveIntegerField()),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_products', to='orders.order')),
            ],
            options={
                'db_table': 'order_products',
            },
        ),
        migrations.AddConstraint(
            model_name='orderproduct',
            constraint=models.UniqueConstraint(fields=('order', 'product_id'), name='unique_order_product'),
        ),
    ]
