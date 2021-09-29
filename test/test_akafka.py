import unittest
from akafka import Akafka

class TestAkafka(unittest.TestCase):
    def setUp(self):
        topics = []
        kafka_options = {}
        topics = ["aminer","logs"]
        kafka_options['bootstrap_servers'] = 'localhost:9092'
        self.akafka = Akafka(*topics, **kafka_options)

    def test_setfilter_with_filters_dictionary(self):
        self.akafka.setfilter("['foo','bar']")
        self.assertIsInstance(self.akafka.filters, list)
        self.assertIn('foo', self.akafka.filters)
        self.assertIn('bar', self.akafka.filters)

    def test_setfilter_with_filters_dict(self):
        self.akafka.setfilter("{'foo': 'foobar'}")
        self.assertIsNone(self.akafka.filters)

    def test_displayfilter_normal_string(self):
        self.assertEqual(self.akafka.displayfilter("hello world"), "hello world")

    def test_displayfilter_with_json_and_filters_is_false(self):
        self.assertEqual(self.akafka.displayfilter("{'foo': 'hello world'}"), "{'foo': 'hello world'}")

    def test_displayfilter_with_json_and_filters(self):
        self.akafka.setfilter('["foo"]')
        self.assertEqual(self.akafka.displayfilter('{"foo": "hello world", "bar": "blah"}'), b'{"foo": "hello world"}')

if __name__ == '__main__':
    unittest.main()
