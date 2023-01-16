# Symmetry454 Calendar in Python

This is a very simple implementation of the Symmetry454 Calendar in Python.

>“The Symmetry454 calendar is a simple perpetual solar calendar that conserves the traditional 7-day week, has symmetrical equal quarters each having 4+5+4 weeks, and starts every month on Monday.”

All information about the calendar, you can get direct from it’s creator’s site:

[http://individual.utoronto.ca/kalendis/symmetry.htm]

    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
    ┃      January, April, July, October      ┃┃      February, May, August, November    ┃┃     March, June, September, December    ┃
    ┣━━━━━┳━━━━━┳━━━━━┳━━━━━┳━━━━━┳━━━━━┳━━━━━┫┣━━━━━┳━━━━━┳━━━━━┳━━━━━┳━━━━━┳━━━━━┳━━━━━┫┣━━━━━┳━━━━━┳━━━━━┳━━━━━┳━━━━━┳━━━━━┳━━━━━┫
    ┃ Mon ┃ Tue ┃ Wed ┃ Thu ┃ Fri ┃ Sat ┃ Sun ┃┃ Mon ┃ Tue ┃ Wed ┃ Thu ┃ Fri ┃ Sat ┃ Sun ┃┃ Mon ┃ Tue ┃ Wed ┃ Thu ┃ Fri ┃ Sat ┃ Sun ┃
    ┡━━━━━╇━━━━━╇━━━━━╇━━━━━╇━━━━━╇━━━━━╇━━━━━┩┡━━━━━╇━━━━━╇━━━━━╇━━━━━╇━━━━━╇━━━━━╇━━━━━┩┡━━━━━╇━━━━━╇━━━━━╇━━━━━╇━━━━━╇━━━━━╇━━━━━┩
    │   1 │   2 │   3 │   4 │   5 │   6 │   7 ││   1 │   2 │   3 │   4 │   5 │   6 │   7 ││   1 │   2 │   3 │   4 │   5 │   6 │   7 │
    ├─────┼─────┼─────┼─────┼─────┼─────┼─────┤├─────┼─────┼─────┼─────┼─────┼─────┼─────┤├─────┼─────┼─────┼─────┼─────┼─────┼─────┤
    │  8  │  9  │  10 │  11 │  12 │  13 │  14 ││  8  │  9  │  10 │  11 │  12 │  13 │  14 ││  8  │  9  │  10 │  11 │  12 │  13 │  14 │
    ├─────┼─────┼─────┼─────┼─────┼─────┼─────┤├─────┼─────┼─────┼─────┼─────┼─────┼─────┤├─────┼─────┼─────┼─────┼─────┼─────┼─────┤
    │  15 │  16 │  17 │  18 │  19 │  20 │  21 ││  15 │  16 │  17 │  18 │  19 │  20 │  21 ││  15 │  16 │  17 │  18 │  19 │  20 │  21 │
    ├─────┼─────┼─────┼─────┼─────┼─────┼─────┤├─────┼─────┼─────┼─────┼─────┼─────┼─────┤├─────┼─────┼─────┼─────┼─────┼─────┼─────┤
    │  22 │  23 │  24 │  25 │  26 │  27 │  28 ││  22 │  23 │  24 │  25 │  26 │  27 │  28 ││  22 │  23 │  24 │  25 │  26 │  27 │  28 │
    └─────┴─────┴─────┴─────┴─────┴─────┴─────┘├─────┼─────┼─────┼─────┼─────┼─────┼─────┤┢━━━━━╈━━━━━╈━━━━━╈━━━━━╈━━━━━╈━━━━━╈━━━━━┪
                                               │  29 │  30 │  31 │  32 │  33 │  34 │  35 │┃  29 ┃  30 ┃  31 ┃  32 ┃  33 ┃  34 ┃  35 ┃
                                               └─────┴─────┴─────┴─────┴─────┴─────┴─────┘┗━━━━━┻━━━━━┻━━━━━┻━━━━━┻━━━━━┻━━━━━┻━━━━━┛
                                                                                             Decemeber’s “leap week” on leap years

For the sake of simplicity, the class is simply called SymmetricDate:

    >>> from symmetric_calendar import SymmetricDate

    >>> sd = SymmetricDate(2023, 1, 15)
    SymmetricDate(2023, 1, 15)

    >>> str(sd)
    '2023-01-15'

    >>> sd.year, sd.month, sd.day, sd.is_leap
    (2023, 1, 15, False)

    >>> sd.gegorian_date
    datetime.date(2023, 1, 16)

    >>> sd.toordina()
    738536

    >>> sd.strftime('%Y %B %d')
    '2023 January 15'

    >>> sd.strftime('%Y %B %d%o')
    '2023 January 15th'

    >>> from datetime import date as GregorianDate

    >>> gd = GregorianDate(2023, 2, 16)
    >>> gd
    datetime.date(2023, 2, 16)

    >>> sd = SymmetricDate(gd)
    >>> sd
    SymmetricDate(2023, 2, 18)

    >>> sd1 = SymmetricDate(2023, 1, 25)
    >>> sd2 = SymmetricDate(2023, 2, 35)
    >>> sd1 > sd2
    False
    >>> sd2 > sd1
    True

    >>> gd = GregorianDate(2023, 3, 5)
    >>> gd == sd2
    True

    >>> SymmetricDate.today()
    SymmetricDate(2023, 1, 15)
