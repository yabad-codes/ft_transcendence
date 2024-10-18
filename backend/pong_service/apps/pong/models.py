from django.db import models

class PongGame(models.Model):
    from pong_service.apps.authentication.models import Player
    class Status(models.TextChoices):
        PENDING = 'Pending'
        STARTED = 'Started'
        FINISHED = 'Finished'

    id = models.AutoField(primary_key=True, editable=False)
    player1 = models.ForeignKey(Player, related_name='player1', on_delete=models.CASCADE)
    player2 = models.ForeignKey(Player, related_name='player2', on_delete=models.CASCADE)
    winner = models.ForeignKey(Player, related_name='winner', on_delete=models.SET_NULL, null=True, blank=True)
    player1_score = models.PositiveIntegerField(default=0)
    player2_score = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Game {self.id}: {self.player1} vs {self.player2 or 'waiting'} - {self.status}"
    
class GameRequest(models.Model):
    from pong_service.apps.authentication.models import Player
    class Status(models.TextChoices):
        PENDING = 'Pending'
        ACCEPTED = 'Accepted'
        REJECTED = 'Rejected'

    id = models.AutoField(primary_key=True, editable=False)
    requester = models.ForeignKey(Player, related_name='game_requests_sent', on_delete=models.CASCADE)
    opponent = models.ForeignKey(Player, related_name='game_requests_received', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Game Request: {self.requester} vs {self.opponent} - {self.status}"
    
class Tournament(models.Model):
    from pong_service.apps.authentication.models import Player
    class Status(models.TextChoices):
        STARTED = 'Started'
        FINISHED = 'Finished'
        
    id = models.AutoField(primary_key=True, editable=False)
    player1 = models.ForeignKey(Player, related_name='tournament_player1', on_delete=models.CASCADE)
    player2 = models.ForeignKey(Player, related_name='tournament_player2', on_delete=models.CASCADE)
    player3 = models.ForeignKey(Player, related_name='tournament_player3', on_delete=models.CASCADE)
    player4 = models.ForeignKey(Player, related_name='tournament_player4', on_delete=models.CASCADE)
    winner = models.ForeignKey(Player, related_name='tournament_winner', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.STARTED)
    created_at = models.DateTimeField(auto_now_add=True)