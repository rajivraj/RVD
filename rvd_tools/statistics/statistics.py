# -*- coding: utf-8 -*-
#
# Alias Robotics S.L.
# https://aliasrobotics.com

"""
Base statistics class

NOTE: Should be specialized by other subclasses that add functionality
"""

from ..database.base import Base
from ..utils import gray, red, green, cyan, yellow
import sys


class Statistics(Base):
    """
    Base statistics class
    """

    def __init__(self):
        super().__init__()
        # All
        self.issues = []  # stores the name of each one of the issues
        # Open
        self.issues_open = []  # stores the name of each one of the issues
        # Closed
        self.issues_closed = []  # stores the name of each one of the issues

        self.vulnerabilities = []  # open and closed ones
        self.bugs = []  # open and closed ones
        self.init_issues_and_labels()

    def init_issues_and_labels(self):
        """
        Inits the existing issues in the repo by adding their
        names into the class attribute self.issues

        Removes 'invalid' and 'duplicate' tickets
        """
        cyan("Statistics, initializing tickets...")
        # All
        issues = self.repo.get_issues(state="all")
        for issue in issues:
            labels = [l.name for l in issue.labels]
            if "invalid" in labels:
                continue
            if "duplicate" in labels:
                continue
            self.issues.append(issue)

            # Classify as a vunerability or as a bug
            # print(issue)  # debugging purposes
            flaw = self.import_issue(issue.number, issue=issue)
            if "vulnerability" in labels:
                self.vulnerabilities.append(issue)
            elif flaw.type == "vulnerability":
                yellow("Warning, 'type == vulnerability' but no corresponding label found, classifying as vuln")
                self.vulnerabilities.append(issue)
            else:
                self.bugs.append(issue)

        # Closed
        issues = self.repo.get_issues(state="closed")
        for issue in issues:
            labels = [l.name for l in issue.labels]
            if "invalid" in labels:
                continue
            if "duplicate" in labels:
                continue
            self.issues_closed.append(issue)

        # Open
        issues = self.repo.get_issues(state="open")
        for issue in issues:
            labels = [l.name for l in issue.labels]
            if "invalid" in labels:
                continue
            if "duplicate" in labels:
                continue
            self.issues_open.append(issue)

    def statistics_vulnerabilities_historic(self, label, isoption="all"):
        """Produce statististics on the historic discovery and report
        of robot vulnerabilities"""
        cyan("Produce statististics on the historic discovery of flaws...")
        if label:  # account for only filtered tickets
            cyan("Using label: " + str(label))
            importer = Base()
            filtered = []
            if isoption == "all":
                issues = self.issues
            elif isoption == "open":
                issues = self.issues_open
            elif isoption == "closed":
                issues = self.issues_closed
            else:
                red("Error, not recognized isoption: " + str(isoption))
                sys.exit(1)

            # fetch the from attributes itself, see above
            # issues = importer.repo.get_issues(state=isoption)
            for issue in issues:
                all_labels = True  # indicates whether all labels are present
                labels = [l.name for l in issue.labels]
                for l in label:
                    # if l not in labels or "invalid" in labels or "duplicate" in labels:
                    if l not in labels:
                        all_labels = False
                        break
                if all_labels:
                    filtered.append(issue)

            self.historic(filtered)

        else:
            cyan("Using all vulnerabilities...")
            # Consider all tickets, open and close
            self.historic(self.vulnerabilities)

    def historic(self, issues):
        """
        Compile a table with historic data

        :returns table [[]]
        """
        for issue in issues:
            flaw = self.import_issue(issue.number, issue=issue, debug=False)
            print(flaw.date_reported)
            print(flaw.vendor)