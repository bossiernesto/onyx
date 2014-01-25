from logger.coloredLogger import ColoredLogger, AbstractLogger
from logger.MockLoggingHandler import MockLoggingHandler
from unittest import TestCase
import logging


class testLogger(TestCase):
    TEST_LOGGER = 'test'

    def setUp(self):
        self.logger = ColoredLogger(self.TEST_LOGGER)
        self.handler = MockLoggingHandler()
        self.logger.addHandler(self.handler)

    def testCallLogger(self):
        self.assertIsInstance(logging.getLogger(self.TEST_LOGGER), ColoredLogger)

    def testLogInfo(self):
        self.logger.info('Info Test')
        self.failUnless('Info Test' in self.handler.messages['info'])

    def testAbstractLogger(self):
        with self.assertRaises(NotImplementedError):
            AbstractLogger(name='abstract')

    def testMessageQueue(self):
        self.handler.reset() #reset Mock lists
        self.logger.warning('Warning 1')
        self.logger.error('Error 1')
        self.logger.error('Error 2')
        self.assertEqual(len(self.handler.messages['error']), 2)
        self.assertEqual(len(self.handler.messages['warning']), 1)
