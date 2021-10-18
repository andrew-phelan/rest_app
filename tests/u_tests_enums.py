import unittest

from lib.enums import Status, Outcome, EventType


class EnumUnitTests(unittest.TestCase):

    def test_status_enum__return_correctly(self):
        values = [val for val in list(Status)]
        for expected, _ in zip(values, range(len(values))):
            status = Status(_)
            self.assertEqual(str(status), str(expected))

    def test_outcome_enum__return_correctly(self):
        values = [val for val in list(Outcome)]
        for expected, _ in zip(values, range(len(values))):
            outcome = Outcome(_)
            self.assertEqual(str(outcome), str(expected))

    def test_event_type_enum__return_correctly(self):
        values = [val for val in list(EventType)]
        for expected, _ in zip(values, range(len(values))):
            status = EventType(_)
            self.assertEqual(str(status), str(expected))


if __name__ == '__main__':
    unittest.main(verbosity=2)
