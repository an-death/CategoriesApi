from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=600, unique=True)
    # is that required to be a OneToMany?
    parent = models.ForeignKey('Category', null=True, on_delete=models.CASCADE)

    def get_children(self):
        return Category.objects.filter(parent=self)

    def get_siblings(self):
        return Category.objects \
            .filter(parent=self.parent)\
            .exclude(id=self.id)
