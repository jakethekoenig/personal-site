import plotly.graph_objects as go
from url_tools import url
from datetime import datetime, timedelta
import json
import os

def check_widget():
    total = 0
    for log in os.listdir('/home/jaek/personal-site/logs'):
        with open(os.path.join('/home/jaek/personal-site/logs', log)) as c:
            content = c.read()
        if 'GET /exp/party' in content:
            total+=1
    return total
print(check_widget())

def total():
    total = 0
    for log in os.listdir('/home/jaek/personal-site/logs'):
        with open(os.path.join('/home/jaek/personal-site/logs', log)) as c:
            content = c.read()
        if 'GET /blog' in content:
            total+=1
    return total
print(total())


# OSes to check: Windows, Linux, iPhone, Chrome, Macintosh
# Browsers: Chrome, Safari, Firefox
def visits_histogram(name):
    name = url(dat)
    start = datetime.strptime(dat["Date"],"%m/%d/%Y")
    dates = []
    for log in os.listdir('/home/jaek/personal-site/logs'):
        with open(os.path.join('/home/jaek/personal-site/logs', log)) as c:
            content = c.read()
        if 'GET /blog/' +name in content:
            OSes = {'Windows','Linux','iPhone','Chrome','Macintosh'}
            good = True #todo: figure out which logs are from people?
            for OS in OSes:
                if OS in content:
                    good = True
            if good:
                dates.append(datetime.strptime(log[:16], "%Y-%m-%d-%H-%M"))
    dates = sorted(dates)
    weeksSince = {}
    for date in dates:
        weeksSince[(date - start).days//7] = weeksSince.get((date - start).days//7,0) + 1

    weekOne = [0]*7
    for date in dates:
        if (date - start).days < 7:
            weekOne[(date - start).days] += 1
    return (weekOne, weeksSince, dates)


data_dir = '/home/jaek/personal-site/src/data/blog'
week_one_graph = go.Figure()
week_by_week_graph = go.Figure()
colors = {
        "magic": "red",
        "personal": "blue",
        "review": "green",
        "guest": "yellow",
        "programming": "orange",
        "guest": "cyan"
        }
for blog in os.listdir(data_dir):

    with open(os.path.join(data_dir, blog)) as f:
        dat = json.load(f)
    date = datetime.strptime(dat["Date"],"%m/%d/%Y")

    if date < datetime.strptime("02/12/2020", "%m/%d/%Y"):
        continue

    hist = visits_histogram(dat)
    color = colors.get(dat["Categories"][0],"grey")

    week_one_graph.add_trace(go.Scatter(x=list(range(0,7)) , y=hist[0] , mode='lines', name=dat["Title"], line=dict(color=color)))

    num_weeks = (datetime.now() - date).days//7
    counts = [0]*(num_weeks)
    for i in range(len(counts)):
        counts[i] = hist[1].get(i,0)
    counts=counts[1:]
    week_by_week_graph.add_trace(go.Scatter(x=list(range(1,num_weeks)) , y=counts , mode='lines', name=dat["Title"], line=dict(color=color)))

week_one_graph.update_layout(title='Page Visits of Blogs in First Week', xaxis_title='days since publication', yaxis_title='Page Views (in ones)')
week_one_graph.show()
week_one_graph.write_html("week_one_graph.html", full_html=False)

week_by_week_graph.update_layout(title='Page views per week', xaxis_title='weeks since publication', yaxis_title='Page Views (in ones)')
week_by_week_graph.show()
week_by_week_graph.write_html("week_by_week_graph.html", full_html=False)
# TODO: graph of page views during first and and per week over blogs lifetime. 
# Total views for each blog post
