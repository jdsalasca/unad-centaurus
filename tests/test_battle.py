import unittest

from app.domain.alignment import Alignment
from app.domain.battle import BattleOutcome, BattleResult


class BattleDomainTestCase(unittest.TestCase):
    def test_battle_outcome_messages(self) -> None:
        self.assertIn("Bien", BattleOutcome.GOOD.message)
        self.assertIn("Mal", BattleOutcome.EVIL.message)
        self.assertIn("empate", BattleOutcome.TIE.message.lower())

    def test_battle_result_outcome_and_winner(self) -> None:
        good_victory = BattleResult(good_power=10, evil_power=5)
        self.assertIs(BattleOutcome.GOOD, good_victory.outcome)
        self.assertIs(Alignment.BENEVOLENT, good_victory.winner_alignment)

        evil_victory = BattleResult(good_power=3, evil_power=6)
        self.assertIs(BattleOutcome.EVIL, evil_victory.outcome)
        self.assertIs(Alignment.MALEVOLENT, evil_victory.winner_alignment)

        tie = BattleResult(good_power=4, evil_power=4)
        self.assertIs(BattleOutcome.TIE, tie.outcome)
        self.assertIsNone(tie.winner_alignment)
