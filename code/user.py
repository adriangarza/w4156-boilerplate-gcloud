from listing import Listing
import datetime


class User:

    def __init__(self, uni, name, year, interests, school):
        self.uni = uni
        self.name = name
        self.year = year
        self.interests = interests
        self.school = school
        self.listings = []
        if school == "Barnard":
            self.email = self.uni + "@barnard.edu"
        else:
            self.email = self.uni + "@columbia.edu"

    def add_listing(self, listing):
        self.listings.append(self, listing)

    def create_listing(self, expiry_time, place):
        listing = Listing (expiry_time, self.uni, place)
        self.add_listing (listing)

    def first_name(self):
        name = self.name.partition (" ")
        firstName = name[0]
        return firstName

    def class_name(self):
        class_name = ''

        now = datetime.datetime.now()
        current_year = now.year
        current_month = now.month

        if current_month <= 5:
            if self.year - current_year == 0:
                class_name = 'Senior'
            elif self.year - current_year == 1:
                class_name = 'Junior'
            elif self.year - current_year == 2:
                class_name = 'Sophomore'
            elif self.year - current_year == 3:
                class_name = 'Freshman'
            else:
                class_name = 'Alum'

        elif current_month > 5:
            if self.year - current_year == 1:
                class_name = 'Senior'
            elif self.year - current_year == 2:
                class_name = 'Junior'
            elif self.year - current_year == 3:
                class_name = 'Sophomore'
            elif self.year - current_year == 4:
                class_name = 'Freshman'
            else:
                class_name = 'Alum'

        return class_name


class Form:

    def __init__(self, f_name, l_name, uni, school, year, interests):
        # type: (object, object, object, object, object, object) -> object
        self.uni = uni
        self.f_name = f_name
        self.l_name = l_name
        self.year = year
        self.interests = interests
        self.school = school

    def form_input_valid(self):
        uChecker = True
        error = ''
        if self.f_name == "" or self.l_name == "" or self.uni == "":
            uChecker = False
            error = "empty"
            
        return uChecker, error
