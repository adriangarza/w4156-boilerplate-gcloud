from listing import Listing

class User:

    def __init__(self, uni, name, year, interests, school):
        self.uni = uni
        self.name = name
        self.schoolYear = year
        self.interests = interests
        self.school = school
        self.listings = []

    def add_listing(self, listing):
        self.listings.append(self, listing)

    def create_listing(self, expiry_time, place):
        listing = Listing(expiry_time, self.uni, place)
        self.add_listing(listing)


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
        if self.f_name == "" or self.l_name == "" or self.uni == "" or self.pwd == "":
            uChecker = False
            error = "empty"
        return uChecker, error


