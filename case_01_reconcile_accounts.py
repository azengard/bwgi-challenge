import csv
import datetime
from pathlib import Path
from unittest import TestCase

FOUND = 'FOUND'
MISSING = 'MISSING'


def _prepare_transactions():
    """Helper function to load transactions to test"""
    transactions1 = list(csv.reader(Path('files/transactions1.csv').open()))
    transactions2 = list(csv.reader(Path('files/transactions2.csv').open()))

    return transactions1, transactions2


def _set_missing_values(transaction):
    """If 'FOUND' is not present on a list then sets element value as 'MISSING'"""
    [el.append(MISSING) for el in transaction if el[-1] != FOUND]


def _date_in_margin(date1, date2):
    """Compares two dates and returns true if they are up to one day apart"""
    date1 = datetime.datetime.strptime(date1, '%Y-%m-%d')
    date2 = datetime.datetime.strptime(date2, '%Y-%m-%d')

    margin = datetime.timedelta(days=1)

    return date2 - margin <= date1 <= date2 + margin


def reconcile_accounts(transactions1, transactions2):
    transactions1 = sorted(transactions1)
    transactions2 = sorted(transactions2)

    for i, el1 in enumerate(transactions1):
        for j, el2 in enumerate(transactions2):
            if el1[1:] == el2[1:] and _date_in_margin(el1[0], el2[0]):
                el1.append(FOUND)
                el2.append(FOUND)
                break

    _set_missing_values(transactions1)
    _set_missing_values(transactions2)

    return transactions1, transactions2


class TestReconcileAccounts(TestCase):
    def test_date_in_margin(self):
        self.assertTrue(_date_in_margin('2020-12-02', '2020-12-02'))
        self.assertTrue(_date_in_margin('2020-12-02', '2020-12-03'))
        self.assertTrue(_date_in_margin('2020-12-03', '2020-12-02'))

    def test_date_not_in_margin(self):
        self.assertFalse(_date_in_margin('2020-12-02', '2020-12-04'))
        self.assertFalse(_date_in_margin('2020-12-01', '2020-12-03'))

    def test_set_missing_values(self):
        list_to_proccess = [['2020-12-02', 'Tecnologia', '16.00', 'Bitbucket'],
                            ['2020-12-03', 'Tecnologia', '16.00', 'Bitbucket', 'FOUND'],
                            ['2020-12-04', 'Jurídico', '60.00', 'LinkSquares', 'FOUND'],
                            ['2020-12-04', 'Tecnologia', '16.00', 'Bitbucket'],
                            ['2020-12-05', 'Tecnologia', '50.00', 'AWS']]
        _set_missing_values(list_to_proccess)

        self.assertListEqual(list_to_proccess, [['2020-12-02', 'Tecnologia', '16.00', 'Bitbucket', 'MISSING'],
                                                ['2020-12-03', 'Tecnologia', '16.00', 'Bitbucket', 'FOUND'],
                                                ['2020-12-04', 'Jurídico', '60.00', 'LinkSquares', 'FOUND'],
                                                ['2020-12-04', 'Tecnologia', '16.00', 'Bitbucket', 'MISSING'],
                                                ['2020-12-05', 'Tecnologia', '50.00', 'AWS', 'MISSING']])

    def test_reconcile_accounts_success(self):
        transactions1, transactions2 = _prepare_transactions()
        out1, out2 = reconcile_accounts(transactions1, transactions2)

        self.assertListEqual(out1, [['2020-12-02', 'Tecnologia', '16.00', 'Bitbucket', 'MISSING'],
                                    ['2020-12-03', 'Tecnologia', '16.00', 'Bitbucket', 'FOUND'],
                                    ['2020-12-04', 'Jurídico', '60.00', 'LinkSquares', 'FOUND'],
                                    ['2020-12-04', 'Tecnologia', '16.00', 'Bitbucket', 'MISSING'],
                                    ['2020-12-05', 'Tecnologia', '50.00', 'AWS', 'MISSING']])

        self.assertListEqual(out2, [['2020-12-04', 'Jurídico', '60.00', 'LinkSquares', 'FOUND'],
                                    ['2020-12-04', 'Jurídico', '60.00', 'LinkSquares', 'MISSING'],
                                    ['2020-12-04', 'Tecnologia', '16.00', 'Bitbucket', 'FOUND'],
                                    ['2020-12-05', 'Tecnologia', '49.99', 'AWS', 'MISSING']])
