import unittest
import grabber

grabber.logger.setLevel(grabber.logging.ERROR)

class TestReturnType(unittest.TestCase):
    def setUp(self):
        soup = grabber.run(test=True)
        self.soup = soup

    def test_snapshot(self):
        snapshot = grabber.get_snapshot(soup=self.soup)
        self.assertIsInstance(snapshot, dict)
    
    def test_trades(self):
        trades = grabber.get_trades(soup=self.soup)
        self.assertIsInstance(trades, list)
    
    def test_advancers(self):
        advancers = grabber.get_advancers(soup=self.soup)
        self.assertIsInstance(advancers, list)
    
    def test_decliners(self):
        decliners = grabber.get_decliners(soup=self.soup)
        self.assertIsInstance(decliners, list)

if __name__ == "__main__":
    unittest.main()