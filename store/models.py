from django.db import models
from django.contrib.auth.models import User
import os


from dotenv import load_dotenv
import cloudinary

# load .env file
load_dotenv()

cloudinary.config( 
  cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"), 
  api_key=os.getenv("CLOUDINARY_API_KEY"), 
  api_secret=os.getenv("CLOUDINARY_API_SECRET"),
  secure=True
)
 
class Address(models.Model):
    user = models.ForeignKey(User, verbose_name="User", on_delete=models.CASCADE)
    locality = models.CharField(max_length=150, verbose_name="Nearest Location")
    city = models.CharField(max_length=150, verbose_name="City")
    state = models.CharField(max_length=150, verbose_name="State")

    def __str__(self):
        return self.locality


class Category(models.Model):
    title = models.CharField(max_length=50, verbose_name="Category Title")
    slug = models.SlugField(max_length=55, verbose_name="Category Slug", blank=True)
    description = models.TextField(blank=True, verbose_name="Category Description")
    
    category_image = models.ImageField(upload_to='', blank=True, null=True, verbose_name="Category Image")
    
    is_active = models.BooleanField(verbose_name="Is Active?")
    is_featured = models.BooleanField(verbose_name="Is Featured?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created Date")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated Date")

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ('-created_at', )

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Auto-generate slug if not provided
        if not self.slug:
            self.slug = slugify(self.title)

        # If category_image is a file, upload to Cloudinary
        if self.category_image and hasattr(self.category_image, "file"):
            upload_result = cloudinary.uploader.upload(
                self.category_image.file,
                folder="categories",
                public_id=self.slug,
                overwrite=True,
                resource_type="image"
            )
            self.category_image = upload_result.get("secure_url")

        super().save(*args, **kwargs)

class Product(models.Model):
    title = models.CharField(max_length=150, verbose_name="Product Title")
    slug = models.SlugField(max_length=160, verbose_name="Product Slug", blank=True)
    sku = models.CharField(max_length=255, unique=True, verbose_name="Unique Product ID (SKU)")
    short_description = models.TextField(verbose_name="Short Description")
    detail_description = models.TextField(blank=True, null=True, verbose_name="Detail Description")
    
    product_image = models.ImageField(upload_to='', blank=True, null=True, verbose_name="Product Image")
    
    price = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.ForeignKey("Category", verbose_name="Product Category", on_delete=models.CASCADE)
    is_active = models.BooleanField(verbose_name="Is Active?")
    is_featured = models.BooleanField(verbose_name="Is Featured?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created Date")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated Date")

    class Meta:
        verbose_name_plural = 'Products'
        ordering = ('-created_at', )

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Auto-generate slug if not provided
        if not self.slug:
            self.slug = slugify(self.title)

        # If product_image is a file, upload it to Cloudinary
        if self.product_image and hasattr(self.product_image, "file"):
            upload_result = cloudinary.uploader.upload(
                self.product_image.file,
                folder="products",
                public_id=self.slug,
                overwrite=True,
                resource_type="image"
            )
            # Replace local file reference with Cloudinary URL
            self.product_image = upload_result.get("secure_url")

        super().save(*args, **kwargs)


class Cart(models.Model):
    user = models.ForeignKey(User, verbose_name="User", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name="Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, verbose_name="Quantity")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created Date")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated Date")

    def __str__(self):
        return str(self.user)
    
    # Creating Model Property to calculate Quantity x Price
    @property
    def total_price(self):
        return self.quantity * self.product.price


STATUS_CHOICES = (
    ('Pending', 'Pending'),
    ('Accepted', 'Accepted'),
    ('Packed', 'Packed'),
    ('On The Way', 'On The Way'),
    ('Delivered', 'Delivered'),
    ('Cancelled', 'Cancelled')
)

class Order(models.Model):
    user = models.ForeignKey(User, verbose_name="User", on_delete=models.CASCADE)
    address = models.ForeignKey(Address, verbose_name="Shipping Address", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name="Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name="Quantity")
    ordered_date = models.DateTimeField(auto_now_add=True, verbose_name="Ordered Date")
    status = models.CharField(
        choices=STATUS_CHOICES,
        max_length=50,
        default="Pending"
        )
