from django.db import migrations

def create_default_categories(apps, schema_editor):
    Category = apps.get_model('majaay', 'Category')
    categories = [
        ('Electronics', 'electronics', 'Electronic products'),
        ('Clothing', 'clothing', 'Clothing products'),
        ('Home & Garden', 'home-garden', 'Home & Garden products'),
        ('Sports & Outdoors', 'sports-outdoors', 'Sports & Outdoors products'),
        ('Books', 'books', 'Books & publications'),
        ('Toys & Games', 'toys-games', 'Toys & Games products'),
        ('Health & Beauty', 'health-beauty', 'Health & Beauty products'),
        ('Automotive', 'automotive', 'Automotive products'),
        ('Food & Beverages', 'food-beverages', 'Food & Beverage products'),
        ('Jewelry & Accessories', 'jewelry-accessories', 'Jewelry & Accessories products'),
    ]
    for name, slug, desc in categories:
        Category.objects.get_or_create(name=name, slug=slug, defaults={'description': desc})

class Migration(migrations.Migration):
    dependencies = [
        ('majaay', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(create_default_categories),
    ]
