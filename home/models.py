from django.db import models
from django.contrib.auth.models import AbstractUser

# User Info

class User(AbstractUser):
    BRONZE, SILVER, GOLD, PLATINUM, DIAMOND = "Bronze", "Silver", "Gold", "Platinum", "Diamond"
    MASTER, GRAND_MASTER = "Master", "Grand Master"

    league_choices = (
        (BRONZE, "Bronze"),
        (SILVER, "Silver"),
        (GOLD, "Gold"),
        (PLATINUM, "Platinum"),
        (DIAMOND, "Diamond"),
        (MASTER, "Master"),
        (GRAND_MASTER, "Grand Master"),
    )

    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True, null=True)
    bio = models.TextField(null=True)
    
    avatar = models.ImageField(null=True, default="avatar.svg")
    
    is_email_verified = models.BooleanField(default=False)
    
    current_rating = models.IntegerField(default=500, verbose_name="Current Rating")
    league = models.CharField(max_length=255, choices=league_choices, default=BRONZE, verbose_name="league")
    wons = models.IntegerField(default=0)
    is_online = models.BooleanField(default=False, verbose_name="Is Online")
    xp = models.IntegerField(default=10, verbose_name="XP")

    
    RATING_THRESHOLDS = {
        BRONZE: 800,
        SILVER: 1400,
        GOLD: 2000,
        PLATINUM: 2800,
        DIAMOND: 3800,
        MASTER: 5000,
        GRAND_MASTER: 6400,
    }
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
        

    def get_current_league(self):
        rating = self.current_rating
        if rating < self.RATING_THRESHOLDS[self.BRONZE]:
            return self.BRONZE
        elif rating < self.RATING_THRESHOLDS[self.SILVER]:
            return self.SILVER
        elif rating < self.RATING_THRESHOLDS[self.GOLD]:
            return self.GOLD
        elif rating < self.RATING_THRESHOLDS[self.PLATINUM]:
            return self.PLATINUM
        elif rating < self.RATING_THRESHOLDS[self.DIAMOND]:
            return self.DIAMOND
        elif rating < self.RATING_THRESHOLDS[self.MASTER]:
            return self.MASTER
        elif rating < self.RATING_THRESHOLDS[self.GRAND_MASTER]:
            return self.GRAND_MASTER

    PARTICIPATION_XP, WIN_ROUND_XP, WIN_GAME_XP = 20, 70, 120

    def get_current_level_and_xp_threshold(self):
        current_xp = self.xp
        xp_threshold = 100
        level = 1
        while current_xp > xp_threshold:
            level += 1
            xp_threshold += 1.5 * xp_threshold
        return level, xp_threshold
