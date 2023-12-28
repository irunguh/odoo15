from datetime import date
from collections import namedtuple


# separating dates
custom_date = '2021-02-01'
new_date = custom_date.split('-')
print('Split date')
print (int(new_date[1]))

Range = namedtuple('Range', ['start', 'end'])
r1 = Range(start=date(2021,2,1), end=date(2021,4,30))
r2 = Range(start=date(2021,2,1), end=date(2021,4,30))
latest_start = max(r1.start, r2.start)
earliest_end = min(r1.end, r2.end)
overlap = (earliest_end - latest_start).days + 1
overlapping_dates = [] # default
if overlap > 0:
     overlapping_dates = range(latest_start.toordinal(), earliest_end.toordinal() + 1) # as numbers
     overlapping_dates = [ date.fromordinal(x) for x in overlapping_dates ] # back to datetime.date objects

print(overlapping_dates)