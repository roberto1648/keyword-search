# -*- coding: utf-8 -*-
"""
here are classes that hold different kinds of data, separated from 
functionality files like making the gui or generating pdf invoices.
"""
import json
import time
import os, shutil
#import shutil

#teacher_database = "teacher info"
#students_database = "students database"

########### >>>>>>>> policies:

dname = "ipc/kwSearchDB.json"

def create_ipc_directory():
    if not does_file_exist("ipc"):
        create_directory("ipc")
    elif os.path.isfile("ipc"):
        create_directory("ipc")

def reset_search_database():
    initialize_json_database(dname)
    
def list_database_entries():
    return list_json_entries(dname)
    
def semaphore_on(lock_file="ipc/kwSearchDB_lock"):
    create_file(lock_file)
    # write_json_entry("writing in progress", True, dname)

def semaphore_off(lock_file="ipc/kwSearchDB_lock"):
    if does_file_exist(lock_file):
        delete_file(lock_file)
    # write_json_entry("writing in progress", False, dname)
    
def wait_for_semaphore(lock_file="ipc/kwSearchDB_lock"):
    if not does_file_exist(lock_file):
        done = True
    else:
        done = False
    while not done:
        time.sleep(0.2)
        done = not does_file_exist(lock_file)
    
def read_database(entry):
    wait_for_semaphore()
    # semaphore_on()
    data = read_json_entry(entry, dname)
    # semaphore_off()
    return data

    
def write_database(entry, value):
    wait_for_semaphore()
    semaphore_on()
    write_json_entry(entry, value, dname)
    semaphore_off()
    
def check_pause():
    return does_file_exist("ipc/pause")

def pause_on():
    create_file("ipc/pause")
    # write_database("pause", True)
#    write_json_entry("pause", True, dname)
    
def pause_off():
    if does_file_exist("ipc/pause"):
        delete_file("ipc/pause")
    # write_database("pause", False)
#    write_json_entry("pause", False, dname)


def wait_for_pause():
    if not does_file_exist("ipc/pause"):
        done = True
    else:
        done = False
    while not done:
        time.sleep(1.0)
        done = not does_file_exist("ipc/pause")


def running_on():
    create_file("ipc/running")


def running_off():
    if does_file_exist("ipc/running"):
        delete_file("ipc/running")


def check_running():
    return does_file_exist("ipc/running")
    # entries = list_database_entries()
    # if "running" in entries:
    #     return read_database("running")
    # else:
    #     write_database("running", False)
    #     return False


def stop():
    create_file("ipc/stop")


def unstop():
    if does_file_exist("ipc/stop"):
        delete_file("ipc/stop")


def check_stop():
    return does_file_exist("ipc/stop")


def read_iteration_list(list_name = "keywords",
                        iteration_index = -1):
    try:
        iteration = read_database("iterations")[iteration_index]
        return iteration[list_name]
    except:
        return []


def write_iteration_list(list_name="keywords",
                          list_value=[],
                          iteration_index=-1):
    previously_paused = check_pause()

    if not previously_paused:
        pause_on()

    iterations = read_database("iterations")
    if not iterations: iterations = [{}]
    try:
        iterations[iteration_index][list_name] = list_value
    except:
        print "couldn't write {} to iteration number {}".format(list_name, iteration_index)

    write_database("iterations", iterations)

    if not previously_paused:
        pause_off()


def append_iteration_list(list_name = "keywords",
                          value = "keyword 1",
                          iteration_index = -1):
                              
    previously_paused = check_pause()
    
    if not previously_paused:
        pause_on()

    iterations = read_database("iterations")
    if iterations:
        iteration = iterations[iteration_index]
    else:
        iteration = {}
    
    if list_name in iteration:
        if value not in iteration[list_name]:
            iteration[list_name].append(value)
    else:
        iteration[list_name] = [value]

    if iterations:
        iterations[iteration_index] = iteration
    else:
        iterations = [iteration]

    write_database("iterations", iterations)
    
    if not previously_paused:
        pause_off()
        
def insert_to_iteration_list(list_name = "keywords", 
                              value = "keyword 1",
                              insert_index = 0,
                              iteration_index = -1):
                              
    previously_paused = check_pause()
    
    if not previously_paused:
        pause_on()

    iterations = read_database("iterations")
    if iterations:
        iteration = iterations[iteration_index]
    else:
        iteration = {}
    
    if list_name in iteration:
        if value not in iteration[list_name]:
            iteration[list_name].insert(insert_index, value)
    else:
        iteration[list_name] = [value]

    if iterations:
        iterations[iteration_index] = iteration
    else:
        iterations = [iteration]

    write_database("iterations", iterations)
    
    if not previously_paused:
        pause_off()


def remove_duplicates_from_iteration_list(list_name = "keywords",
                                          iteration_index = -1):
    previously_paused = check_pause()

    if not previously_paused:
        pause_on()

    iterations = read_database("iterations")
    iteration = iterations[iteration_index]

    # remove duplicates from list, keeping the previous order:
    it_list = iteration[list_name]
    unique_it_list = []

    for kwd in it_list:
        if kwd not in unique_it_list:
            unique_it_list.append(kwd)

    iteration[list_name] = unique_it_list
    iterations[iteration_index] = iteration
    write_database("iterations", iterations)

    if not previously_paused:
        pause_off()


def remove_from_iteration_list(list_name = "keywords", 
                              value = "keyword 1",
                              iteration_index = -1):
                              
    previously_paused = check_pause()
    
    if not previously_paused:
        pause_on()
        
    iterations = read_database("iterations")
    iteration = iterations[iteration_index]  
    
    if list_name in iteration:
        if value in iteration[list_name]:
            iteration[list_name].remove(value)

    iterations[iteration_index] = iteration
    write_database("iterations", iterations)
    
    if not previously_paused:
        pause_off()    
        
def database_last_modified_on():
    return file_last_modified_on(dname)

def ipc_folder_last_modified_on():
    return file_last_modified_on("ipc")
        
#def pause_and_append_iteration_list(list_name = "keywords", 
#                                    value = "keyword 1",
#                                    iteration_index = -1):
#    paused_before = check_pause()
#    if not paused_before:
#        write_database("pause", True)
#        
#    append_iteration_list(list_name, value, iteration_index)
#        
#    if not paused_before:
#        write_database("pause", False)

# teacher info:
#def read_teacher_info_entry(entry = ""):
#    fname = teacher_database
#    return read_json_entry(entry, fname)
#    
#def write_teacher_info_entry(entry = "", value = 0):
#    fname = teacher_database
#    write_json_entry(entry, value, fname)
#    
# student info:
#def read_student_info_entry(entry = "", student_name = ""):
#    if is_student_in_database(student_name):
#        fname = students_database
#        data = read_json_entry(student_name, fname)
#        if entry in data:
#            return data[entry]
#        else:
#            return None
#    
#    
#def write_student_info_entry(entry = "", value = 0, 
#                             student_name = ""):
#    fname = students_database
#    if is_student_in_database(student_name):
#        st = read_json_entry(student_name, fname)
#    else:
#        st = {}
#    st[entry] = value
#    write_json_entry(student_name, st, fname)
#    
#def list_of_students():
#    return list_json_entries(students_database)
#    
#def is_student_in_database(student_name = ""):
#    if student_name in list_json_entries(students_database):
#        st = read_json_entry(student_name, students_database)
#        return isinstance(st, dict)
#        
#def delete_student(student_name = ""):
#    delete_json_entry(student_name, students_database)
#    
#def todays_lessons():
#    date = todays_date()
#    today = day_of_the_week(date).lower()
#    todays_list = []
##    lesson_day = s.lesson_weekday.lower()
#    for student_name in list_of_students():
#        lesson_day =\
#        read_student_info_entry("Lesson Day", student_name).lower()
#        if lesson_day == today:
#            lesson_time =\
#            read_student_info_entry("Lesson Time", 
#                                    student_name).lower()
#            todays_list.append((student_name, lesson_time))
#    # sort the list according to lesson time:        
#    def getKey(item):
#        return item[1]
#    todays_list = sorted(todays_list, key=getKey)
#    return todays_list

###### >>>>>>>> mechanisms:
###### database functions:

def initialize_json_database(database = "temp.json"):
    dir_name = os.path.dirname(database)
    if not does_directory_exist(dir_name):
        os.makedirs(dir_name)
    fp = open(database, "w+")
    json.dump({}, fp)
    fp.close()

def write_json_entry(entry_name = "entry", value = "", 
                     database = "temp.json"):
    """
    Read entire contents, modify entry name, and dump the result.
    
    It might be possible to instead modify only the entry without 
    having to load the whole thing (using open(name, 'r+')), but 
    couldn't make it work here (added an extra "{" or left other text) 
    in some cases (worked for "stop": false, but not true or 1)
    """
    if not does_file_exist(database):
        initialize_json_database(database)
    data = read_json_contents(database)

    if type(data) == dict:
        data[str(entry_name)] = value
        f = open(database, 'w')
        json.dump(data, f, indent=4)
        f.close()
    else:
        print "error in DatabaseFunctions.write_json_entry"
        print "couldn't write entry {} to database {}".format(entry_name, database)
#    if not does_file_exist(database):
#        initialize_json_database(database)
##    with open(database, 'r+') as f:
#    f = open(database, 'w')
#    try:
#        data = json.load(f)
#        if not isinstance(data, dict):
#            data = {}
#    except:
#        data = {}
#    data[str(entry_name)] = value 
##    f.seek(0)        # <--- should reset file position to the beginning.
#    json.dump(data, f, indent=4)
#    f.close()

def read_json_entry(entry_name = "entry", 
                    database= "temp.json"):
    if does_file_exist(database):
        f = open(database, 'r')
        
        try:
            data = json.load(f)
            return data[entry_name]
        except:
            print "no entry {} in database {}".format(entry_name, database)
        f.close()
    else:
        print "file {} doesn't exist".format(database)
        
def read_json_contents(database= "temp.json"):
    data = {}
    if does_file_exist(database):
        f = open(database, 'r')
        
        try:
            data = json.load(f)
        except:
            print "no valid data in database {}".format(database)
        f.close()
    else:
        print "file {} doesn't exist".format(database)
    return data
        
def list_json_entries(database= "temp.json"):
    entries = []
    if does_file_exist(database):
        f = open(database, 'r')
        
        try:
            data = json.load(f)
            for key in data.iterkeys():
                entries.append(key)
#            return entries
        except:
            print "no valid data in database {}".format(database)
        f.close()
    else:
        print "file {} doesn't exist".format(database)
    return entries
        
def list_json_entries_at_nested_address(address = "one/two/three",
                                        database = "temp.json"):
    if does_file_exist(database):
        f = open(database, 'r')        
        try:
            data = json.load(f)
            addr_list = address.split("/")
            nested_entry = data
            for name in addr_list:
                nested_entry = nested_entry[name]
            entries = []
            for key in nested_entry.iterkeys():
                entries.append(key)
            return entries
        except:
            print "no valid data in database {}".format(database)
        f.close()
    else:
        print "file {} doesn't exist".format(database)
        
def delete_json_entry(entry = "entry", database = "temp.json"):
    dic = json.load(open(database, 'r'))
    dic2 =\
    {key: value for key, value in dic.items() if key != entry}
    json.dump(dic2, open(database, 'w'), indent=4)

###### utilities

def copy_class_attributes(source_instance = object, 
                          destination_instance = object):
        for attr, value in source_instance.__dict__.iteritems():
            setattr(destination_instance, attr, value)

            
#def is_database(database_name = 'students'):
#    result = False
#    if does_file_exist(relative_folder = '', 
#                       file_name = database_name):
#        try:
#            import shelve
#            db = shelve.open(database_name)
#            db.close()
#            result = True
#        except:
#            pass
#    return result

    
def does_file_exist(file_name = 'student.txt'):
    """
    relative folder starts at the current working directory (i.e., the 
    directory where the application resides).
    """
    import os.path
    folder = os.getcwd()
#    folder = os.path.join(folder, relative_folder)
    file_path = os.path.join(folder, file_name)
    return os.path.isfile(file_path)
    
def does_directory_exist(directory_name = 'folder/'):
    """
    relative folder starts at the current working directory (i.e., the 
    directory where the application resides).
    """
    import os.path
    folder = os.getcwd()
#    folder = os.path.join(folder, relative_folder)
    dir_path = os.path.join(folder, directory_name)
    return os.path.isdir(dir_path)

def create_directory(dir_name="ipc"):
    if not does_directory_exist(dir_name):
        os.makedirs(dir_name)

def create_file(file_name = "name", data=""):
    dir_name = os.path.dirname(file_name)
    if not does_directory_exist(dir_name):
        os.makedirs(dir_name)
    fp = open(file_name, "w+")
    fp.write(data)
    fp.close()

def delete_file(file_name = "name"):
    os.remove(file_name)

def clear_file_contents(file_name = "database.json"):
    fp = open(file_name, 'w')
    fp.close()

def clear_directory_contents(folder = ""):
    if does_directory_exist(folder):
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path): shutil.rmtree(file_path)
            except Exception as e:
                print(e)
    else:
        print "directory {} doesn't exist".format(folder)
        
def file_last_modified_on(file_path):
    return os.stat(file_path).st_mtime

def time_stamp_to_date(time_stamp = 1404070344.345):
    import time
    return time.strftime('%m/%d/%Y', time.localtime(time_stamp))    

def date_to_time_stamp(date = '08/15/2014'):
    import time
    date_tuple = time.strptime(date,'%m/%d/%Y')
    return time.mktime(date_tuple)
    
def day_of_the_week(date = '06/16/1973'):
    import datetime
    month, day, year = (int(x) for x in date.split('/'))
    ans = datetime.date(year, month, day)
    return ans.strftime("%A")
    
def todays_date():
    import datetime
    d = datetime.datetime.today()
    date = "{}/{}/{}".format(d.month, d.day, d.year)
    return date
    