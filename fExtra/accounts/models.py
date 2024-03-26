from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    category = models.ForeignKey(Category, related_name='subcategories', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Expense(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    commentary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.category.name} - {self.cost} on {self.date}"


class ExpenseDocument(models.Model):
    expense = models.ForeignKey(Expense, related_name='documents', on_delete=models.CASCADE)
    document = models.FileField(upload_to='expense_documents/')

    def __str__(self):
        return f"Document for {self.expense.category.name} - {self.expense.date}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    num_telephone = models.CharField(max_length=20, default='+32')
    num_national = models.CharField(max_length=20)
    genre = models.CharField(max_length=1, choices=(('M', 'Male'), ('F', 'Female'), ('X', 'Other')))
    address = models.CharField(max_length=255)
    magistrats = models.ManyToManyField(User, related_name='assigned_parents', blank=True)

    def __str__(self):
        return self.user.username
