from django.db import models

class Giocatore(models.Model):
    nome = models.CharField(max_length=100)
    ruolo = models.CharField(max_length=50)
    squadra = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nome} ({self.ruolo})"

class Partita(models.Model):
    squadra_casa = models.CharField(max_length=100)
    squadra_trasferta = models.CharField(max_length=100)
    arbitro = models.CharField(max_length=100)
    data = models.DateTimeField()

    def __str__(self):
        return f"{self.squadra_casa} vs {self.squadra_trasferta} - {self.data}"