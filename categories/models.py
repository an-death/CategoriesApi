from django.db import models, IntegrityError


class NameConflictError(Exception):
    def __init__(self, category_name: str):
        self._category_name = category_name

    def __repr__(self):
        return f'Name field should be unique. ' \
               f'Category with name "{self._category_name}" already exist'

    def json(self):
        return {'error': repr(self), 'name': self._category_name}


class Category(models.Model):
    name = models.CharField(max_length=600, unique=True)
    # is that required to be a OneToMany?
    # if it is, so that this field should be extracted to a
    # ManyToMany-RelationMapping table
    parent = models.ForeignKey('Category', null=True, on_delete=models.CASCADE)

    def get_children(self):
        return Category.objects.filter(parent=self)

    def get_siblings(self):
        return Category.objects \
            .filter(parent=self.parent)\
            .exclude(id=self.id)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        try:
            super().save(
                force_insert=force_insert,
                force_update=force_update,
                using=using,
                update_fields=update_fields)
        except IntegrityError as e:
            raise NameConflictError(self.name) from e
