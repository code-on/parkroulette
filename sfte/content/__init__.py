from django.utils.datastructures import SortedDict

HOURS_DICT = SortedDict((
    (0, '12AM'), (1, '1AM'), (2, '2AM'), (3, '3AM'), (4, '4AM'), (5, '5AM'),
    (6, '6AM'), (7, '7AM'), (8, '8AM'), (9, '9AM'), (10, '10AM'), (11, '11AM'),
    (12, '12PM'), (13, '1PM'), (14, '2PM'), (15, '3PM'), (16, '4PM'), (17, '5PM'),
    (18, '6PM'), (19, '7PM'), (20, '8PM'), (21, '9PM'), (22, '10PM'), (23, '11PM'),
    (24, '0PM'),
))

WEEK_DAYS = (
    ('1', 'Sunday'),
    ('2', 'Monday'),
    ('3', 'Tuesday'),
    ('4', 'Wednesday'),
    ('5', 'Thursday'),
    ('6', 'Friday'),
    ('7', 'Saturday'),
)

WEEK_DAYS_DICT = dict(WEEK_DAYS)

DISTANCE_DICT = dict((
    ('0.0001', '10'), ('0.0002', '20'), ('0.0003', '30'),
    ('0.0004', '40'), ('0.0005', '50'), ('0.001', '100'),
))
