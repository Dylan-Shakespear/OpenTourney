class Rounds:
    rounds = []

    def __init__(self, num_rounds):
        while num_rounds > 1:
            num_rounds //= 2
            self.rounds.append(num_rounds)
