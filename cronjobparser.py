# -*- coding: utf-8 -*-
import codecs

from pyparsing import White, Word, alphanums, CharsNotIn
from pyparsing import Forward, Group, OneOrMore
from pyparsing import pythonStyleComment


class CronJob(object):

    def __init__(self, command, minute, user="root", hour="*", dom="*",
                 month="*", dow="*"):
        self.command = command
        self.minute = minute
        self.user = user
        self.hour = hour
        self.dom = dom
        self.month = month
        self.dow = dow

    def __str__(self):
        """
        This simply returns the CronJob so that it can be added to the crontab
        """
        cronjob = "%s\t%s\t%s\t%s\t%s\t%s\t%s" % (self.minute, self.hour,
                                                  self.dom, self.month,
                                                  self.dow, self.user,
                                                  self.command)
        return cronjob


class CronJobParser(object):
    
    dtime = Word("0123456789-*")
    command = CharsNotIn("{}\n#,")
    username = Word(alphanums)
    key = Word(alphanums)
    value = command
    space = White().suppress()
    comment = Word("#")
    equals = Word("=")
    assignment = Forward()
    assignment << Group(key
                        + equals.suppress()
                        + value)
    entry_block = Forward()
    entry_block << Group(dtime
                         + space.suppress()
                         + dtime
                         + space.suppress()
                         + dtime
                         + space.suppress()
                         + dtime
                         + space.suppress()
                         + dtime
                         + space.suppress()
                         + username
                         + space.suppress()
                         + command
                         )
    cron_file = OneOrMore(entry_block | assignment).ignore(pythonStyleComment)
    
    file_header = """# File parsed and saved by crontabparser.\n\n"""
    
    def __init__(self, infile="/etc/crontab", content=None):
        self.file = None
        if content:
            self.content = content
        else:
            self.file = infile
            f = codecs.open(self.file, "r", "utf-8")
            self.content = f.read()
            f.close()

        data = self.get()
        self.assignments = {}
        self.cronjobs = []
        for entry in data:
            if len(entry) == 2:
                self.assignments[entry[0]] = entry[1]
            elif len(entry) == 7:
                self.cronjobs.append(CronJob(entry[6], entry[0],
                                        user=entry[5], hour=entry[1],
                                        dom=entry[2], month=entry[3],
                                        dow=entry[4]))

    def get(self):
        """
        return the grouped config
        
        """
        # reread the file from dist
        if self.file:
            f = codecs.open(self.file, "r", "utf-8")
            self.content = f.read()
            f.close()
        config = self.cron_file.parseString(self.content)
        return config
    
    def format(self):
        """
        :return: The formatted data as it would be written to a file
        """
        output = ""
        output += self.file_header
        # write the assignments
        assignments = self.assignments
        for assignment in assignments:
            output += "%s=%s\n" % (assignment,
                                   assignments.get(assignment))
        # write the cronjobs
        output += "\n#m\th\tdom\tmon\tdow\tuser\tcommand\n"
        for cronjob in self.cronjobs:
            output += "%s\n" % cronjob
        return output

    def save(self, outfile):
        output = self.format()
        f = codecs.open(outfile, 'w', 'utf-8')
        for line in output.splitlines():
            f.write(line + "\n")
        f.close()
