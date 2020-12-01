from django.db import models


class News(models.Model):
    """ novedades internas del sistema """
    priority = models.IntegerField(default=50, help_text='0/100 priority level')
    title = models.CharField(max_length=90)
    description = models.TextField(null=True, blank=True)
    object_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.title} {self.object_created}'

    class Meta:
        ordering = ['-id']