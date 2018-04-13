import datetime

class Listing:

    def __init__(self, date, time, uni, place):
        self.date = date
        self.time = time
        self.uni = uni
        self.place = place

class ListForm:

	def __init__ (self, cafeteria, date, time, swipe):
		#type:(object, object, object, boolean)
		self.cafeteria = cafeteria
		self.date = date
		self.time = time
		self.swipe = swipe

	def day_of_week(self):
		#parsing the dateime input
		date = self.date
		y, m, d = [int(i) for i in date.split('-')]
		wkday = datetime.date(y, m, d).weekday()
		return wkday
		#0 = Monday, 1 = Tuesday, 2 = Wednesday, 3 = Thursday, 4 = Friday, 5 = Saturday, 6 = Sunday

	def time_parser(self):
		t = self.time
		h, m = [int(i) for i in t.split(':')]
		time = datetime.time(h, m, 0)
		return time
	
	def time_range (start, end, x):
		if start <= end:
			return start <= x <= end
		else:
			return start<= x or x <= end 

	def listform_dateime_valid(self):
		lChecker = True
		error = ''
		if self.cafeteria == "" or self.date == "" or self.time == "" :
			lChecker = False
			error = "Need to pick a cafeteria"
		else:
			time = time_parser()
			day = day_of_week()
			#Ferris Booth Hours
			if self.cafeteria == "Ferris Booth":
				if day == 6: #Sunday closed
					lChecker = False
				elif day == 5: #Saturday hours
					start = datetime.time (9, 0, 0)
					end = datetime.time(21, 0, 0)
					lChecker = time_range(start, end, time)
				elif day == 4: #Friday hours
					start = datetime.time (7, 30, 0)
					end = datetime.time(21, 0, 0)
					lChecker = time_range(start, end, time)
				else:
					start = datetime.time (7, 30, 0)
					end = datetime.time(20, 0, 0)
					lChecker = time_range(start, end, time)

			# John Jay Hours
			elif self.cafeteria == "John Jay":
				if day == 4 or day == 5: #Friday/Saturday closed
					lChecker = False
				else:
					start = datetime.time (9, 30, 0)
					end = datetime.time(21, 0, 0)
					lChecker = time_range(start, end, time)

			#JJ's Hours
			elif self.cafeteria == "JJs Place":
				start = datetime.time (12, 0, 0)
				end = datetime.time(10, 0, 0)
				lChecker = time_range(start, end, time)

			#Hewitt Hours
			elif self.cafeteria == "Hewitt":
				if day == 6: #Sunday hours
					start = datetime.time (10, 0, 0)
					end = datetime.time(15, 0, 0)
					lChecker = time_range(start, end, time)
					if lChecker == False:
						start = datetime.time (17, 0, 0)
						end = datetime.time(19, 45, 0)
						lChecker = time_range(start, end, time)
				elif day == 5: #Saturday hours
					start = datetime.time (10, 0, 0)
					end = datetime.time(15, 0, 0)
					lChecker = time_range(start, end, time)
					if lChecker == False:
						start = datetime.time (17, 0, 0)
						end = datetime.time(19, 0, 0)
						lChecker = time_range(start, end, time)
				else:
					start = datetime.time (8, 0, 0)
					end = datetime.time(15, 0, 0)
					lChecker = time_range(start, end, time)
					if lChecker == False:
						start = datetime.time (16, 0, 0)
						end = datetime.time(19, 45, 0)
						lChecker = time_range(start, end, time)
			#Diana Hours
			elif self.cafeteria == "Diana":
				if day == 5: #Saturday closed
					lChecker = False
				elif day == 6: #Sunday hours
					start = datetime.time (17, 0, 0)
					end = datetime.time(19, 45, 0)
					lChecker = time_range(start, end, time)
					if lChecker == False:
						start = datetime.time (20, 45, 0)
						end = datetime.time(23, 0, 0)
						lChecker = time_range(start, end, time)
				elif day == 4: #Friday hours
					start = datetime.time (9, 30, 0)
					end = datetime.time(11, 0, 0)
					lChecker = time_range(start, end, time)
					if lChecker == False:
						start = datetime.time (11, 30, 0)
						end = datetime.time(15, 0, 0)
						lChecker = time_range(start, end, time)
				else:
					start = datetime.time (9, 30, 0)
					end = datetime.time(11, 0, 0)
					lChecker = time_range(start, end, time)
					if lChecker == False:
						start = datetime.time (11, 30, 0)
						end = datetime.time(15, 0, 0)
						lChecker = time_range(start, end, time)
						if lChecker == False:
							start = datetime.time (17, 0, 0)
							end = datetime.time(19, 45, 0)
							lChecker = time_range(start, end, time)
							if lChecker == False:
								start = datetime.time (20, 45, 0)
								end = datetime.time(23, 0, 0)
								lChecker = time_range(start, end, time)
			if lChecker == False:
				error = self.cafeteria + "is not open at the time selected"
		return lChecker, error