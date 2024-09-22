from django.db import models
from pong_service.apps.authentication.models import Player

class PongGame(models.Model):
    STATUS = [
		('pending', 'Game Pending'),
		('started', 'Game Started'),
		('finished', 'Game Finished'),
	]
    id = models.AutoField(primary_key=True)
    player1 = models.ForeignKey(Player, related_name='player1', on_delete=models.CASCADE)
    player2 = models.ForeignKey(Player, related_name='player2', on_delete=models.CASCADE)
    winner = models.ForeignKey(Player, related_name='winner', on_delete=models.CASCADE)
    player1_score = models.PositiveIntegerField(default=0)
    player2_score = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Game {self.id}: {self.player1} vs {self.player2 or 'waiting'} - {self.status}"