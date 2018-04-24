import datetime
from datetime import timedelta


class Listing:

    def __init__(self, sql_dateTime, uni, place, needSwipe):
        self.expiryDate = self.dt_to_date(sql_dateTime)
        self.expiryDateTime = sql_dateTime
        self.uni = uni
        self.place = place
        self.needSwipe = needSwipe

    # copied code from ListForm -- is there a way to consolidate?
    def parse_date(self):
        month = self.expiryDate.strftime("%b")
        listing_date = "{}. {}".format(month, self.expiryDate.day)
        return listing_date

    def parse_time(self):
        time_no_military = self.dt_to_time(self.expiryDateTime).strftime("%I:%M%p")
        return time_no_military

    def list_day_of_week(self):
        # parsing the datetime input
        wkday = self.expiryDate.weekday()
        return wkday
        # 0 = Monday, 1 = Tuesday, 2 = Wednesday, 3 = Thursday, 4 = Friday, 5 = Saturday, 6 = Sunday

    def week_day_name(self):
        day = self.list_day_of_week()
        if day == 0:
            day = 'Monday'
        if day == 1:
            day = 'Tuesday'
        if day == 2:
            day = 'Wednesday'
        if day == 3:
            day = 'Thursday'
        if day == 4:
            day = 'Friday'
        if day == 5:
            day = 'Saturday'
        if day == 6:
            day = 'Sunday'
        return day

    def dt_to_date(self, dt_string):
        """
        gets an SQL DATETIME string and returns a datetime.date
        1997-07-18 14:00:00 -> [1997, 7, 18]
        delightfully devilish, seymour
        """
        l = [int(x) for x in str(dt_string).split(" ")[0].split("-")]
        return datetime.date(l[0], l[1], l[2])

    def dt_to_time(self, dt_string):
        """
        gets an SQL DATETIME string and returns a datetime.time
        1997-07-18 14:00:00 -> [14, 0, 0]
        """
        l = [int(x) for x in str(dt_string).split(" ")[1].split(":")]
        return datetime.time(l[0], l[1], l[2])

class ListingPost:

    def __init__(self, listing, user):
        """

        :type listing: object
        """
        # type:(Listing, User)
        self.listing = listing
        self.user = user

    def week_day(self):
        day = self.listing.week_day_name()
        return day

    def get_date(self):
        # returns date as a string in the format "Jan. 1"
        #date = self.listing.parse_date()
        #y, m, d = [int(i) for i in date.split('-')]
        #month= datetime.date(y, m, d).strftime("%b")
        #listing_date = "{}. {}".format(month, d)
        date = self.listing.parse_date()
        return date

    def get_time(self):
        # returns time in the format 01:00pm or 11:00am
        # time = self.listing.parse_time()
        # h, m = [int(i) for i in time.split(':')]
        # time_no_military = datetime.time(h,m,0).strftime("%I:%M%p")
        time_no_military = self.listing.parse_time()
        return time_no_military

    def get_place(self):
        place = self.listing.place
        return place

    def get_named_time(self):
        hour = self.listing.dt_to_time(self.listing.expiryDateTime).hour
        if hour < 3:
            return "dinner"
        elif hour < 11:
            return "breakfast"
        elif hour < 16:
            return "lunch"
        else:
            return "dinner"


class ListForm:

    def __init__(self, cafeteria, date, time, swipe):
        # type:(object, object, object, bool) -> object
        self.cafeteria = cafeteria
        self.date = date
        self.time = time
        self.swipe = swipe

    def day_of_week(self):
        # parsing the dateime input
        date = self.date
        y, m, d = [int(i) for i in date.split('-')]
        wkday = datetime.date(y, m, d).weekday()
        return wkday

    # 0 = Monday, 1 = Tuesday, 2 = Wednesday, 3 = Thursday, 4 = Friday, 5 = Saturday, 6 = Sunday

    def time_parser(self):
        t = self.time
        h, m = [int (i) for i in t.split (':')]
        time = datetime.time (h, m, 0)
        return time

    def time_range(self, start, end, x):
        if start <= end:
            return start <= x <= end
        else:
            return start <= x or x <= end

    def listform_datetime_valid(self):
        lChecker = True
        error = ''
        if self.cafeteria == "" or self.date == "" or self.time == "":
            lChecker = False
            error = "empty"
        elif lChecker == True:
            time = self.time_parser()
            day = self.day_of_week()
            # Ferris Booth Hours
            if self.cafeteria == "Ferris Booth":
                if day == 6:  # Sunday closed
                    lChecker = False
                elif day == 5:  # Saturday hours
                    start = datetime.time(9, 0, 0)
                    end = datetime.time(21, 0, 0)
                    lChecker = self.time_range(start, end, time)
                elif day == 4:  # Friday hours
                    start = datetime.time(7, 30, 0)
                    end = datetime.time(21, 0, 0)
                    lChecker = self.time_range(start, end, time)
                else:
                    start = datetime.time(7, 30, 0)
                    end = datetime.time(20, 0, 0)
                    lChecker = self.time_range(start, end, time)

            # John Jay Hours
            elif self.cafeteria == "John Jay":
                if day == 4 or day == 5:  # Friday/Saturday closed
                    lChecker = False
                else:
                    start = datetime.time(9, 30, 0)
                    end = datetime.time(21, 0, 0)
                    lChecker = self.time_range(start, end, time)

            # JJ's Hours
            elif self.cafeteria == "JJs Place":
                start = datetime.time(12, 0, 0)
                end = datetime.time(10, 0, 0)
                lChecker = self.time_range(start, end, time)

            # Hewitt Hours
            elif self.cafeteria == "Hewitt":
                if day == 6:  # Sunday hours
                    start = datetime.time(10, 0, 0)
                    end = datetime.time(15, 0, 0)
                    lChecker = self.time_range(start, end, time)
                    if lChecker == False:
                        start = datetime.time(17, 0, 0)
                        end = datetime.time(19, 45, 0)
                        lChecker = self.time_range(start, end, time)
                elif day == 5:  # Saturday hours
                    start = datetime.time(10, 0, 0)
                    end = datetime.time(15, 0, 0)
                    lChecker = self.time_range(start, end, time)
                    if lChecker == False:
                        start = datetime.time(17, 0, 0)
                        end = datetime.time(19, 0, 0)
                        lChecker = self.time_range(start, end, time)
                else:
                    start = datetime.time(8, 0, 0)
                    end = datetime.time(15, 0, 0)
                    lChecker = self.time_range(start, end, time)
                    if lChecker == False:
                        start = datetime.time(16, 0, 0)
                        end = datetime.time(19, 45, 0)
                        lChecker = self.time_range(start, end, time)
            # Diana Hours
            elif self.cafeteria == "Diana":
                if day == 5:  # Saturday closed
                    lChecker = False
                elif day == 6:  # Sunday hours
                    start = datetime.time(17, 0, 0)
                    end = datetime.time(19, 45, 0)
                    lChecker = self.time_range(start, end, time)
                    if lChecker == False:
                        start = datetime.time(20, 45, 0)
                        end = datetime.time(23, 0, 0)
                        lChecker = self.time_range(start, end, time)
                elif day == 4:  # Friday hours
                    start = datetime.time(9, 30, 0)
                    end = datetime.time(11, 0, 0)
                    lChecker = self.time_range(start, end, time)
                    if lChecker == False:
                        start = datetime.time(11, 30, 0)
                        end = datetime.time(15, 0, 0)
                        lChecker = self.time_range(start, end, time)
                else:
                    start = datetime.time(9, 30, 0)
                    end = datetime.time(11, 0, 0)
                    lChecker = self.time_range(start, end, time)
                    if lChecker == False:
                        start = datetime.time(11, 30, 0)
                        end = datetime.time(15, 0, 0)
                        lChecker = self.time_range(start, end, time)
                        if lChecker == False:
                            start = datetime.time(17, 0, 0)
                            end = datetime.time(19, 45, 0)
                            lChecker = self.time_range(start, end, time)
                            if lChecker == False:
                                start = datetime.time(20, 45, 0)
                                end = datetime.time(23, 0, 0)
                                lChecker = self.time_range(start, end, time)
            if lChecker == False:
                error = "bad time"
            else:
                now =  datetime.datetime.now() - timedelta(hours=4)
                exp = self.date + ' ' + self.time
                exp = datetime.datetime.strptime(exp, '%Y-%m-%d %H:%M')
                print(now, exp)
                if exp < now:
                    lChecker = False
                    error = "past time"
                     
        return lChecker, error
