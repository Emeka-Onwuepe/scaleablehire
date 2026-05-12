from django.db import models
from user.models import User



class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    team_lead = models.ForeignKey(User,related_name='team_lead', 
                                  blank=True,null=True,
                                  on_delete=models.CASCADE)


    def __str__(self):
        return self.name


class Idea(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.title} by {self.author.full_name}'

class Feedback(models.Model):
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, related_name='feedbacks')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Feedback by {self.author.full_name} on {self.idea.title}'

    def visible_to(self, user):
        User = getattr(user, 'User', None)
        if User is None:
            return False
        author_role = self.author.User.role
        if author_role == User.ROLE_MANAGER:
            return User.role == User.ROLE_TEAM_LEAD and self.idea.team == User.team
        if author_role == User.ROLE_TEAM_LEAD:
            if User.role == User.ROLE_STAFF:
                return self.idea.author == user
            return self.idea.team == User.team
        return False
