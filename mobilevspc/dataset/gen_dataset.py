import collections
import csv
import datetime
import os
import sys
import pprint
import cPickle as pickle

import apache_log_parser
import MySQLdb
from user_agents import parse as parse_ua

class DSEntry():
    def __init__(self):
        self.logs, self.user = [], []
        self.user_agent, self.ip = None, None
        
db_name = sys.argv[1]
fname = "../dataset%s.csv" % ['cafe_demo1', 'crc_spanish'].index(db_name)

db = MySQLdb.connect("localhost", "root", "root", db_name)
c1 = db.cursor(MySQLdb.cursors.DictCursor)
c2 = db.cursor()

parser = apache_log_parser.make_parser("%h %l %u %t \"%r\" %>s %O \"%{Referer}i\" \"%{User-Agent}i\"")

# Load up the IP db file
ip_file = open("ip_db/ip_db.txt").read().splitlines()
ip_db = {}
for line in ip_file:
    parts = line.split()
    if len(parts) <= 2 or parts[1] != 'CA':
        continue
    ip = parts[0]
    state = parts[1]
    zipc = parts[-1]
    city = ' '.join(parts[2:len(parts)-1])
    #print ip, state, zipc, city
    ip_db[ip] = (city, state, zipc)

#===========================

none_dict = collections.defaultdict(lambda: None)

def get_user_info(user_id):
    c = c1
    c.execute("SELECT * FROM auth_user WHERE id=%s", [user_id])
    results = c.fetchone()
    if results:
        c.execute("select count(c.rater_id) as num_rated from auth_user u inner join comment_rating c on (u.id=c.rater_id) where u.id = {}".format(results['id']))
        x = c.fetchone()
        results.update(x)            
        c.execute("select count(d.user_id) as num_comments from auth_user u inner join discussion_comment d on (u.id=d.user_id) where u.id = {}".format(results['id']))
        results.update(c.fetchone())
        c.execute("select z.code as zipcode, z.city as city, z.state as state from opinion_core_zipcode z join opinion_core_zipcodelog l on (z.id = l.location_id) join auth_user u on (u.id = l.user_id) where u.id = {};".format(results['id']))
        res = c.fetchone()
        if res: results.update(res)
        return results
    return none_dict

#============================

c2.execute("SELECT DISTINCT logger_id, is_visitor FROM log_user_events;")
visitors = c2.fetchall() 

logs = collections.OrderedDict()

# Populate the logs dictionary
for x in visitors: logs[x] = DSEntry()

for x in logs.keys():
    logger_id, is_visitor = x
    c1.execute("SELECT * FROM log_user_events "
               "WHERE logger_id=%s AND is_visitor=%s", [logger_id, is_visitor])
    logs[x].logs.extend(c1.fetchall())


# Merge the entries for registered users
c1.execute("SELECT id, logger_id, is_visitor, created FROM log_user_events WHERE details = 'register' ORDER BY id ASC")
registered_users = c1.fetchall()
for x in registered_users:
    entry = logs.get((x['logger_id'], x['is_visitor']))
    if not entry:
        continue

    try:
        c2.execute("SELECT DISTINCT logger_id FROM log_user_events WHERE details='login'"
               "AND created BETWEEN %s AND %s ORDER BY id ASC", [x['created'],
                                                                 x['created'] + datetime.timedelta(seconds=5)])
    except:
        print(c2._last_executed)
        raise

    
    reg_log_ids = c2.fetchall()
    print >> sys.stderr, "Found {} reg_ids for {}: {}".format(len(reg_log_ids), x['logger_id'], reg_log_ids) 

    for reg_id in reg_log_ids:
        reg_id = reg_id[0]
        existing = logs.pop( (reg_id, 0), None )
        if existing:
            print >> sys.stderr, "Merging {} into {}".format(x['logger_id'], reg_id) 
            entry.logs.extend(existing.logs)
            entry.user.append(reg_id)
            break
        else:
            print >> sys.stderr, "Did not merge {} into {}".format(x['logger_id'], reg_id) 


def get_most_likely(user, field):
    td = [datetime.timedelta(seconds=0),
          datetime.timedelta(seconds=1)]
    candidates = collections.Counter()
    for log in logs[user].logs:
        for time_delta in td:
            tmp = apache.get(log['created'] + time_delta)
            if tmp:
                tmp = map(lambda x: x.get(field), tmp)
                candidates.update(tmp)
    # print candidates
    mc = candidates.most_common(1)
    try:
        return mc[0][0]
    except:
        return None

apache = collections.defaultdict(list)

# Load up Apache logs
if os.path.exists("apache.pickle"):
    apache = pickle.load(open("apache.pickle"))
else:
    for i, line in enumerate(open("apache.log").read().splitlines()):
         if i % 10000 == 0: print >> sys.stderr, "Parsed", i, "apache logs"
         log = parser(line)
         t = log['time_received_datetimeobj']
         apache[t].append(log)
    pickle.dump(apache, open("apache.pickle", "w+"))
     
for user in logs:
    logs[user].user_agent = get_most_likely(user, 'request_header_user_agent')
    logs[user].ip = get_most_likely(user, 'remote_host')

# Generate the dataset

outfile = csv.writer(open(fname, "w+"))
events =[ 'first time',
          'slider_set 1', 'slider_set 2', 'slider_set 3', 'slider_set 4', 'slider_set 5', 'slider_set 6',
          'sliders finished',
          'dialog 1', 'dialog 2', 'dialog 3', 'dialog 4',
          'rated',
          'comment cancelled', 'comment submitted', 'login', 'logout', 'register', 'session end',
          'translate en', 'translate es']

header = ['IP Address',
          'User Agent',
          'OS',
          'Device',
          'Browser',
          'IsMobile',
          'IsPC',
          'NumUsers',
          'RegistrationDate',
          'UserID',
          'Email',
          'ReportedZipcode',
          'ReportedCity',
          'ReportedState',
          'IPZipcode',
          'IPCity',
          'IPState',
          'ResolvedZip',
          'ResolvedCity',
          'ResolvedState',
          'Num Ratings Given',
          'Num Comments Written',
          # 'Event'
] + ["Event: " + e for e in events]
          #     ] + ["Event: " + e for e in events] # + ['Total number of slider actions']

outfile.writerow(header)

# def get_formatted_user_info(userids):
#     res = []
#     for u in userids:
#         ui = get_user_info(u)
#         res.append([
#             ui['date_joined'],
#             ui['id'],
#             ui['email'],
#             ui.get('zipcode', ''),
#             ui.get('city', ''),
#             ui.get('state', ''), ## insert
#             ui['num_rated'],
#             ui['num_comments'],                   
#         ])
#     if not res:
#         return []    
#     length = len(res[0])
#     fres = []
#     for i in range(length):
#         fres.append(','.join(map(str, (map(lambda x: x[i], res)))))
#     return fres

def get_event_counts(entry):
    result = []
    for e in events:        
        ename = e.replace("Event: ", "")
        count = len(filter(lambda x: x['details'] != None and x['details'].startswith(ename),
                           entry.logs))
        result.append(count)
    return result
        

for key in logs:
    entry = logs[key]
    if not entry.user_agent or key[1] == 0 or len(entry.user) > 1: 
        continue
    ua = parse_ua(entry.user_agent)

    row = [entry.ip,
           entry.user_agent,
           ua.os.family,
           ua.device.family,
           ua.browser.family,
           int(ua.is_mobile or ua.is_tablet or ua.is_touch_capable),
           int(ua.is_pc),
           len(entry.user),
    ]

    if len(entry.user) == 1:
        u = entry.user[0]
    else:
        u = none_dict
        
    ui = get_user_info(u)

    ip_log = ip_db.get(entry.ip)

    rcity, rstate, rzip = map(lambda x: ui.get(x, None), ['city', 'state', 'zipcode'])
    icity, istate, izip = ip_log or (None, None, None)
    fcity, fstate, fzip = (rcity or icity), (rstate or istate), (rzip or izip)

    # print icity, istate, izip
    if fstate != 'CA':
        continue

    row.extend([
        ui['date_joined'],
        ui['id'],
        ui['email'],
        ui.get('zipcode', ''),
        ui.get('city', ''),
        ui.get('state', ''), ## insert
        izip,
        icity,
        istate,
        fzip,
        fcity,
        fstate,
        ui['num_rated'],
        ui['num_comments'],
        # str(entry.logs),
    ])

    row.extend(get_event_counts(entry))

    # extend = get_formatted_user_info(entry.user)
    exclude = ['allen', 'patel', 'sanjay', 'tanja','crittenden', 'goldberg', 'nonnecke', 'matti']
    # email = len(extend) > 2 and extend[2]
    email = ui['email']
    if email and any([e.lower() in email.lower() for e in exclude]):
        continue

    # row.extend(extend)
        
    outfile.writerow(row)
    # print entry.ip, len(entry.user_agent), len(entry.logs), len(entry.user)

os.system("wc -l " + fname)

UNMATCHED = filter(lambda x: x[1] == 0, logs.keys())
print "# unmatched entries", len(UNMATCHED)
# pprint.pprint(UNMATCHED)
