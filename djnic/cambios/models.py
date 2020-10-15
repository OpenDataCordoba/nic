from django.db import models


class CambiosDominio(models.Model):
    dominio = models.ForeignKey('dominios.Dominio', on_delete=models.CASCADE, related_name='cambios')
    momento = models.DateTimeField()

    # def __str__(self):
    #     dominio = self.dominio if self.dominio is not None else ''
    #     momento = self.momento if self.momento is not None else ''
    #     return f'{dominio} {momento}'

class CampoCambio(models.Model):
    """ Cada uno de los campos que cambio 
        Todos string por mas que haya fechas. 
        Problemas con el DNS porque el sistema anterior tenia 5 
            campos separads y ahora esta bien hecho.
        """
    cambio = models.ForeignKey(CambiosDominio, on_delete=models.CASCADE, related_name='campos')
    campo = models.CharField(max_length=240, null=True, db_index=True)
    anterior = models.CharField(max_length=240, null=True)
    nuevo = models.CharField(max_length=240, null=True)

    uid_anterior = models.IntegerField(default=0, db_index=True, help_text="to be deleted after migration")

    # def __str__(self):
    #     campo = self.campo or ''
    #     anterior = self.anterior or ''
    #     nuevo = self.nuevo or ''
    #     return f'{campo} from {anterior} to {nuevo}'