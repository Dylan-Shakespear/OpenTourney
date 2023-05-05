from django.test import TestCase
from django.contrib.auth.models import User
from .models import TournamentObject, Match, Team, UserSettings
from .utils import calculate_next_round, calculate_double_next_round, calculate_loser_next_round

# Model Tests


class TournamentObjectTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='password'
        )
        TournamentObject.objects.create(name="Test Tourney", description="Test Desc", num_teams=8,
                                        tournament_type='single', user=self.user)
        TournamentObject.objects.create(name="Test Tourney 2", num_teams=16,
                                        tournament_type='double', user=self.user)

    def test_tourney(self):
        test1 = TournamentObject.objects.get(name="Test Tourney", user=self.user)
        test2 = TournamentObject.objects.get(name="Test Tourney 2", user=self.user)
        self.assertEqual(test1.name, "Test Tourney")
        self.assertEqual(test1.num_teams, 8)
        self.assertEqual(test1.tournament_type, "single")
        self.assertEqual(test2.name, "Test Tourney 2")
        self.assertEqual(test2.num_teams, 16)
        self.assertEqual(test2.tournament_type, "double")


class MatchObjectTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='password'
        )
        self.tourney = TournamentObject.objects.create(name="Test Match", description="Test Desc", num_teams=8,
                                        tournament_type='single', user=self.user)
        Match.objects.create(name="Test Match 1", tournament=self.tourney, round=5)
        Match.objects.create(name="Test Match 2", tournament=self.tourney, round=12)

    def test_match(self):
        test1 = Match.objects.get(tournament=self.tourney, round=5)
        test2 = Match.objects.get(tournament=self.tourney, round=12)
        self.assertEqual(test1.name, "Test Match 1")
        self.assertEqual(test2.name, "Test Match 2")


class TeamObjectTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='password'
        )
        self.tourney = TournamentObject.objects.create(name="Test Match", description="Test Desc", num_teams=8,
                                        tournament_type='single', user=self.user)
        Team.objects.create(name="Test Team 1", tournament=self.tourney, user=self.user)
        Team.objects.create(name="Test Team 2", tournament=self.tourney)

    def test_team(self):
        test1 = Team.objects.get(name="Test Team 1", tournament=self.tourney)
        test2 = Team.objects.get(name="Test Team 2", tournament=self.tourney)
        self.assertEqual(test1.name, "Test Team 1")
        self.assertEqual(test2.name, "Test Team 2")
        self.assertEqual(test1.user, self.user)


class SettingsObjectTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='password'
        )
        UserSettings.objects.create(user=self.user, tourney_display="Test Display")

    def test_settings(self):
        test1 = UserSettings.objects.get(user=self.user)
        self.assertEqual(test1.tourney_display, "Test Display")


# Test Finding Text Round for SE
class NextRoundTestsSE(TestCase):
    def test_next_round(self):
        self.assertEqual(calculate_next_round(1, 4), 3)
        self.assertEqual(calculate_next_round(1, 8), 5)
        self.assertEqual(calculate_next_round(6, 8), 7)
        self.assertEqual(calculate_next_round(1, 16), 9)
        self.assertEqual(calculate_next_round(2, 16), 9)
        self.assertEqual(calculate_next_round(13, 16), 15)
        self.assertEqual(calculate_next_round(11, 16), 14)
        self.assertEqual(calculate_next_round(26, 32), 29)
        self.assertEqual(calculate_next_round(24, 32), 28)
        self.assertEqual(calculate_next_round(30, 32), 31)


# Test Finding Text Round for DE
class NextRoundTestsDE(TestCase):
    def test_next_round(self):
        self.assertEqual(calculate_double_next_round(1, 4), 3)
        self.assertEqual(calculate_double_next_round(4, 4), 5)
        self.assertEqual(calculate_double_next_round(5, 4), 6)
        self.assertEqual(calculate_double_next_round(3, 4), 6)
        self.assertEqual(calculate_double_next_round(12, 8), 13)
        self.assertEqual(calculate_double_next_round(8, 8), 10)
        self.assertEqual(calculate_double_next_round(6, 8), 7)
        self.assertEqual(calculate_double_next_round(24, 16), 26)
        self.assertEqual(calculate_double_next_round(54, 32), 57)
        self.assertEqual(calculate_double_next_round(57, 32), 59)
        self.assertEqual(calculate_double_next_round(61, 32), 62)


# Test Finding Text Round for Loser in DE
class NextRoundLoserTestsDE(TestCase):
    def test_next_round(self):
        self.assertEqual(calculate_loser_next_round(3, 4), 5)
        self.assertEqual(calculate_loser_next_round(5, 4), -1)
        self.assertEqual(calculate_loser_next_round(2, 4), 4)
        self.assertEqual(calculate_loser_next_round(15, 16), 29)
        self.assertEqual(calculate_loser_next_round(23, 16), -1)
        self.assertEqual(calculate_loser_next_round(30, 32), 59)
