#!/usr/bin/env python 

# Test input 
# each meeting will be described by a dict with 2 fields a 
# title and duration in minutes { title:"BlaBlaBla", dur:30}

test_input = [{ 'title' : 'All Hands meeting', 'dur': 60},
              { 'title' : 'Marketing presentation', 'dur':30},
              { 'title' : 'Product team sync', 'dur': 30},
              { 'title' : 'Ruby vs Go presentation', 'dur': 45}, 
              { 'title' : 'New app design presentation', 'dur':45},
              { 'title' : 'Customer support sync', 'dur': 30},
              { 'title' : 'Front-end coding interview', 'dur': 60},
              { 'title' : 'Skype Interview A', 'dur':30},
              { 'title' : 'Skype Interview B', 'dur':30},
              { 'title' : 'Project Bananaphone Kickoff', 'dur':45},
              { 'title' : 'Developer talk', 'dur':60},
              { 'title' : 'API Architecture planning', 'dur':45},
              { 'title' : 'Android app presentation', 'dur':45},
              { 'title' : 'Back-end coding interview A',  'dur':60},
              { 'title' : 'Back-end coding interview B',  'dur':60},
              { 'title' : 'Back-end coding interview C',  'dur':60},
              { 'title' : 'Sprint planning', 'dur':45},
              { 'title' : 'New marketing campaign presentation', 'dur':30}]

from datetime import datetime
# from datetime import timedelta

class WorkingDay:
    def __init__(self, date = datetime.now().date() , 
                 start_core_hours = "09:00", end_core_hours="17:00",
                 start_lunch_time = "12:00", end_lunch_time = "13:00"):
        def format_date_time(date_, time_str):
            """a helper function to return  datetime from times""" 
            return datetime.strptime('{} {}'.format(date_.strftime('%d/%m/%y'),
                                             time_str), '%d/%m/%y %H:%M')
        # init varibales
        self.date = date  # optional place holder (can be also initilized with a date)
        self.start_core_hours = format_date_time(self.date, start_core_hours)
        self.end_core_hours = format_date_time(self.date, end_core_hours)
        self.start_lunch_time = format_date_time(self.date, start_lunch_time)
        self.end_lunch_time = format_date_time(self.date, end_lunch_time)

    def get_lunch_pause_in_minutes(self):
        return (self.end_lunch_time - self.start_lunch_time).seconds/60.

    def core_day_minutes(self):
        return  (self.end_core_hours - self.start_core_hours).seconds/60.

    def get_schedulable_minutes(self):
        """ Returns the number of schedulable minutes within the day """
        return self.core_day_minutes() - self.get_lunch_pause_in_minutes() 

    def get_schedulable_minutes_bl(self):
        """ Returns the number of schedulable minutes before lunch"""
        return (self.start_lunch_time - self.start_core_hours).seconds/60. 

    def get_schedulable_minutes_al(self):
        """ Returns the number of schedulable minutes after lunch"""
        return (self.end_core_hours - self.end_lunch_time).seconds/60. 



class Room:
    """ The class room also tries to help/check Scheduling if the Scheduler is stupid
    (or the scheduling is in fifo with no knowledge about the future or all the day meetings), 
    they are working together :) """

    def __init__(self, id_=0, date = datetime.now().date() , 
                 start_core_hours = "09:00", end_core_hours="17:00",
                 start_lunch_time = "12:00", end_lunch_time = "13:00"):
        self.working_day = WorkingDay(date, start_core_hours, end_core_hours,
                                      start_lunch_time, end_lunch_time)
        # we can opt to keep all the meeting in the same list 
        # but it is better for efficiency to not test if we are after or 
        # before lunch but with insuring it and store them separately

        self.meetings  = { 'bl':[], 'al':[]}
        self.id_=id_ 

    def clear(self):
        """ Removes the scheduled meetings from the room """
        self.meetings  = { 'bl':[], 'al':[]}

    def __str__(self):
        str_ = "Room {}:\n".format(self.id_)
        if self.meetings.get('bl'):
            # str_ +="Before lunch:\n"
            for meeting in self.meetings.get('bl'):
                str_ +="{}, {} min.\n".format(meeting.get('title', 'Blablabla'), meeting.get('dur', 0) )
        str_ +="{} Lunch\n".format(datetime.strftime(self.working_day.start_lunch_time,'%H:%M'))

        if self.meetings.get('al'):
            # str_ +="after lunch:\n"
            for meeting in self.meetings.get('al'):
                str_ +="{}, {} min.\n".format(meeting.get('title', 'Blablabla'), meeting.get('dur', 0) )
        str_+= "{} min. available within the day:  {} min. before lunch and {} after lunch.\n".\
               format(self.day_availability(), self.bl_availability(), self.al_availability())
        return str_

    def agg_duration(self):
        """ Simply returns the global duration of all the meetings scheduled
        until now in the room """ 
        return  sum([ meeting.get('dur', 0) for meeting in self.meetings.get('al', [])+self.meetings.get('bl', []) ])

    def agg_before_lunch(self):
        """ Sum-up the before lunch meetings duration"""
        return  sum([meeting.get('dur', 0) for meeting in self.meetings.get('bl', [])])

    def agg_after_lunch(self):
        """ Sum-up the after lunch meetings duration"""
        return  sum([ meeting.get('dur', 0) for meeting in self.meetings.get('al', [])])

    def day_availability(self):
        """ Simple day availability (in not contiguous minutes)  """
        return self.working_day.get_schedulable_minutes() - self.agg_duration() 

    def bl_availability(self):
        """ Simple before lunch availability (in not contiguous minutes)  """
        return self.working_day.get_schedulable_minutes_bl() - self.agg_before_lunch() 

    def al_availability(self):
        """ Simple after lunch availability (in not contiguous minutes)  """
        return self.working_day.get_schedulable_minutes_al() - self.agg_after_lunch() 

    def get_max_bl_al_availability(self):
        if self.bl_availability() >= self.al_availability():
            return {'slot':'bl', 'avail':self.bl_availability()}
        return {'slot':'al', 'avail':self.al_availability()}

    def check_slot(self, meeting, verbose=False):
        """ Check availability for the meeting. and returns back dictionary with
        the possible configurations (and after config as (inversed cost, metric to maximise) if 
        we allow the room to schedule internally, but here also for check the code """
        check_dict = {}
        check_str = ''
        # simply do we have enough available time for the
        if meeting.get('dur', 0) <= self.day_availability():
            check_str +="seems likely we have a slot for {} :".\
                    format(meeting.get('title', 'Blablabla'))
            # That suppose that your meeting can be splitted to a before lunch, after lunch  (halftimes)
            # in a worst case you might have lunch pause in the middle
            check_dict['day'] = {'chk' : True}
            # We will try to avoid this prioritarily if we have not enough 
            # slot before lunch try to schedule after lunch
        
            # Check if we can schedule the meeting before lunch
            if meeting.get('dur', 0) <= self.bl_availability():
                check_str += "it could be scheduled BEFORE lunch"
                # print "Before lunch avail {}".format(self.bl_availability())
                check_dict['bl'] = {'chk':True, 'after': self.bl_availability() - meeting.get('dur', 0) }
            # Check "with full stomach"
            if meeting.get('dur', 0) <= self.al_availability():
                check_str += ", could be scheduled AFTER lunch".\
                        format(meeting.get('title', 'Blablabla'))
                check_dict['al'] = {'chk':True, 'after': self.al_availability() - meeting.get('dur', 0) }
        else:
            check_dict['day_slot'] = False
            check_str += " :( not enough time slot today for {}  ".\
                    format(meeting.get('title', 'Blablabla'))
        check_str += "\n"
        if verbose:
            print check_str
        return check_dict

    def add_meeting(self, meeting, bl_al='bl'):
        assert bl_al in self.meetings.keys()
        check_dict = self.check_slot(meeting)
        # print check_dict
        if check_dict.get(bl_al, {}).get('chk', False):
            # print 'SCHEDULED Meeting .... '
            self.meetings[bl_al].append(meeting)
            return True
        else:
            print 'Check Scheduler (problem) no slot available for {}'.format(bl_al)
            print check_dict
            return False

    def collect_garbage(self):
        """ Try to re-arrange to collect small slots for bigger contigious space
        before or after lunch. """
        pass
        

    def schedule_to_the_biggest_available_slot(self, meeting):
        bl_al = self.get_max_bl_al_availability()['slot']
        return self.add_meeting(meeting, bl_al=bl_al)

    def schedule_to_the_best_fit(self, meeting):
        check_dict = self.check_slot(meeting)
        return self.add_meeting(meeting, bl_al=sorted([(key, val) for key, val in check_dict.iteritems() if key != 'day' ], key=lambda item:item[1])[0]) 
        # there is a redundancy of verification (but also some code factorization)
        

class Scheduler:
    def __init__(self, meetings, room_nbr):
        self.meetings = meetings
        self.rooms = [Room(id_=id_+1) for id_ in range(room_nbr)]

    def clear_rooms(self):
        """ Removes all the sheduled meetings from the rooms """
        for room in self.rooms:
            room.clear()

    def global_check(self):
        meetings_duration = sum([meeting.get('dur', 0) for meeting in self.meetings])
        rooms_availability = sum([room.day_availability() for room in self.rooms])
        print 'trying to schedule {} min. of meetings in global rooms availability of {} min.'.\
            format(meetings_duration, rooms_availability)
        if meetings_duration > rooms_availability:
            print 'sorry but one or more meeting will not be possible today'
        
    def schedule_to_the_biggest_available_slot(self):

        """ Starting with the longer meetings 
        (meetings are sorted form the longest to the shortest),
        here the scheduler will choose the room with the biggest available slot,
        and within this room will chose before/after lunch with also the biggest
        available slot, that tends 
        (I say tends: within the ideal/hypothetical condition of equal 
        duration meetings :) )  to balance the rooms, if no room for the 
        current meeting try the longest meeting one wich might fit """
        print "-- Schedule_to_the_biggest_available_slot : "
        scheduling_report = {'to_delay': []}        
        for meeting in sorted(self.meetings, key=lambda mt: mt.get('dur', 0), reverse=True):
            # print '{}, {} min'.format(meeting.get('title'), meeting.get('dur'))
            # get the room with the biggest availability 
            most_free_room = sorted(self.rooms, key=lambda rm:rm.get_max_bl_al_availability()['avail'], reverse=True)[0]
            scheduled = most_free_room.schedule_to_the_biggest_available_slot(meeting)
            if not scheduled:
                scheduling_report['to_delay'].append(meeting)

        return scheduling_report 
            

    def schedule_to_the_best_fit(self):
        
        print "-- Schedule_to_the_best_fit"
        scheduling_report = {'to_delay': []}        
        for meeting in sorted(self.meetings, key=lambda mt: mt.get('dur', 0), reverse=True):
            # print '{}, {} min'.format(meeting.get('title'), meeting.get('dur'))
            # get the room with the biggest availability 
            most_free_room = sorted(self.rooms, key=lambda rm:rm.get_max_bl_al_availability()['avail'], reverse=True)[0]
            scheduled = most_free_room.schedule_to_the_biggest_available_slot(meeting)
            if not scheduled:
                scheduling_report['to_delay'].append(meeting)

        return scheduling_report 
    
    def display(self):
        for room in self.rooms:
            print room
        
        

def main():
    sc = Scheduler(test_input, 2)
    sc.global_check()
    print sc.schedule_to_the_biggest_available_slot()
    sc.display()

    sc.clear_rooms()
    print sc.schedule_to_the_best_fit()
    sc.display()

if __name__ == "__main__":
    main()
