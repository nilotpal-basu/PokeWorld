from django.db import models

# Create your models here.
class Trainer(models.Model):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    trainer_tier = models.CharField(max_length=20, choices=[("Novice", "Novice"), ("Elite", "Elite"), ("Master", "Master")], default="Novice")
    poke_caught = models.IntegerField(default=0)
    img_number = models.IntegerField(default=25)
    def __str__(self):
        return self.username
    
class Pokemon(models.Model):
    label = models.IntegerField(null=False, unique=True)
    name = models.CharField(max_length=50)
    num_caught = models.IntegerField(default=0)

    def __str__(self):
        return self.name
    
class PokemonCaught(models.Model):
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE)
    pokemon = models.ForeignKey(Pokemon, on_delete=models.CASCADE)
    caught_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('trainer', 'pokemon')

    def __str__(self):
        return f"{self.trainer.username} caught {self.pokemon.name}"