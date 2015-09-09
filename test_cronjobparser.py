# -*- coding: utf-8 -*-


import logging
log = logging.getLogger(__name__)
import unittest
import os
from cronjobparser import CronJobParser, CronJob

CRONTAB = """
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
SHELL=/bin/sh

#m	h	dom	mon	dow	user	command
17	*	*	*	*	root	cd / && run-parts --report /etc/cron.hourly
25	6	*	*	*	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.daily )
47	6	*	*	7	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.weekly )
52	6	1	*	*	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.monthly )
10	17	*	*	*	privacyidea	/usr/bin/privacyidea-backup
1	10	1	*	*	privacyidea	/usr/bin/privacyidea-backup
"""


class TestCrontabParser(unittest.TestCase):

    def setUp(self):
        pass

    def test_import_from_file(self):
        CP = CronJobParser("./testdata/crontab")
        config_raw = CP.get()
        self.assertEqual(len(config_raw), 8)

        config = CP.config
        self.assertEqual(len(config), 2)
        self.assertTrue("assignments" in config)
        self.assertTrue("cronjobs" in config)

        self.assertEqual(len(config.get("cronjobs")), 6)

        self.assertTrue("PATH" in config.get("assignments"))
        self.assertTrue("SHELL" in config.get("assignments"))

    def test_from_config(self):
        CP = CronJobParser(content=CRONTAB)
        config = CP.config
        self.assertEqual(len(config), 2)
        self.assertTrue("assignments" in config)
        self.assertTrue("cronjobs" in config)

    def test_save(self):
        CP = CronJobParser(content=CRONTAB)
        config = CP.config
        self.assertEqual(len(config.get("cronjobs")), 6)
        cronj = config.get("cronjobs")[0]
        self.assertEqual(cronj.minute, "17")
        self.assertEqual(cronj.dow, "*")

        # now save it to a file

        CP.save(outfile="./testdata/tmpfile")
        # Read the file again!
        CP2 = CronJobParser("./testdata/tmpfile")
        config = CP2.config
        self.assertEqual(len(config.get("cronjobs")), 6)
        cronj = config.get("cronjobs")[0]
        self.assertEqual(cronj.minute, "17")
        self.assertEqual(cronj.dow, "*")
        os.unlink("./testdata/tmpfile")


