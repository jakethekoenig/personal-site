import json
import os
import shutil
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from content import generate_content, generate_comments
from config import config

# From a websites template and its specified data (which has a link to the content)
# create a filled out webpage.
def replaceTags(template, data, index):
    data = dict(data)
    tags = { "$", "[", ":", "??" }
    # TODO: Make this method robust to tags inside tags
    # replace content
    content = generate_content(data, index, config["content"])
    template = template.replace("<[Content]>", content)
    if "Commentsource" in data.keys() and data["Commentsource"] == "github":
        comments = generate_comments(data, index)
    else:
        data["Commentsource"] = "lambda"
        comments = "<:comp/commentiframe:>" # TODO: switch it around so this is what it is by default.
    template = template.replace("<[Comments]>", comments)
    # replace components
    while template.find("<:") != -1:
        start = template.find("<:")
        end   = template.find(":>")+2
        tag = template[start:end]
        comp_path = tag[2:-2]
        with open(os.path.join(config["templates"],comp_path)) as c:
            comp = c.read()
        template = template.replace(tag, comp)
    # replace tags
    for tag in data.keys():
        if type(data[tag]) == type(""):
            template = template.replace("<$"+tag+"$>", data[tag])
    # Delete all tags with no corresponding data
    while template.find("<$") != -1 and template.find("$>") != -1:
        start = template.find("<$")
        end   = template.find("$>")+2
        if start>end:
            break
        template = template[:start] + template[end:]
    # delete optional tags
    while template.find("<??") != -1:
        start = template.find("<??")
        mid   = template.find("???")
        end   = template.find("??>")+3
        remove = eval(template[start+3:mid])
        if remove:
            template = template[:start] + template[end:]
        else:
            template = template[:start]+template[mid+3:end-3]+template[end:]
    return template

# More complicated than it should be for legacy reasons
def file_name(data):
    if "URL" in data:
        url = data["URL"]
    else:
        url = data["Title"].replace(" ","").replace(",","").replace("'","")
    return url


def parse_date(value):
    for date_format in ("%Y-%m-%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(value, date_format)
        except ValueError:
            pass
    raise ValueError(f"Unsupported date format: {value}")


# From the data directory create an index of the site. It'll be a list of tuples. Each with
# first parameter the name of the page or directory and second parameter another list if it
# was a directory else the associated data object. The lists will be sorted by date if one is
# present else alphabetically.
def make_index(index_path="."):
    index = []
    defaults = {}
    default_file = os.path.join(index_path, 'default.json')
    if os.path.exists(default_file):
        with open(default_file) as data_file:
            defaults = json.load(data_file)
    for page in os.listdir(index_path):
        if page=='default.json' or  page.find("swp")!=-1:
            continue
        new_index_path = os.path.join(index_path,page)
        if os.path.isdir(new_index_path):
            index+=[(page, make_index(new_index_path))]
        else:
            with open(new_index_path) as data_file:
                data = json.load(data_file)
                data["relative_path"] = os.path.join(index_path, file_name(data))
                data["comment_path"] = os.path.join("comments/", os.path.splitext(data["relative_path"])[0])
                if "permalink" not in data.keys():
                    data["permalink"] = os.path.join(config.get("base_url", "/"), data["relative_path"]).replace("/./","/")
                data1 = dict(defaults)
                data1.update(data)
                index+=[(page,data1)]
    index.sort(key=lambda t: parse_date(t[1]["Date"] if "Date" in t[1] else "2000-01-01"), reverse=True)
    return index


def collect_pages(target_dir, index):
    sequential_pages = []
    parallel_pages = []

    for (path, data) in index:
        if isinstance(data, list):
            child_sequential, child_parallel = collect_pages(target_dir, data)
            sequential_pages.extend(child_sequential)
            parallel_pages.extend(child_parallel)
        else:
            destination = os.path.join(target_dir, data["relative_path"])
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            if os.path.splitext(data["Content"])[1] == ".py":
                sequential_pages.append((destination, data, index))
            else:
                parallel_pages.append((destination, data))

    return sequential_pages, parallel_pages


def configured_jobs():
    default_jobs = min(8, os.cpu_count() or 1)
    value = os.environ.get("BUILD_JOBS")
    if value is None:
        return default_jobs
    try:
        jobs = int(value)
    except ValueError as error:
        raise ValueError("BUILD_JOBS must be a positive integer") from error
    if jobs < 1:
        raise ValueError("BUILD_JOBS must be a positive integer")
    return jobs


def initialize_worker(worker_config, working_directory):
    config.clear()
    config.update(worker_config)
    os.chdir(working_directory)


def make_parallel_page(page):
    path, data = page
    make_page(path, data, None)


def make_site(target_dir, index):
    sequential_pages, parallel_pages = collect_pages(target_dir, index)

    for path, data, local_index in sequential_pages:
        make_page(path, data, local_index)

    jobs = min(configured_jobs(), len(parallel_pages))
    if jobs <= 1:
        for page in parallel_pages:
            make_parallel_page(page)
        return

    print("Rendering %d pages with %d workers..." % (len(parallel_pages), jobs))
    with ProcessPoolExecutor(
        max_workers=jobs,
        initializer=initialize_worker,
        initargs=(dict(config), os.getcwd()),
    ) as executor:
        for _ in executor.map(make_parallel_page, parallel_pages, chunksize=32):
            pass


def make_page(path, data, index):
    with open(os.path.join(config["templates"], data["Template"]), 'r') as f:
        temp = f.read()
    with open(path, "w") as out:
        out.write(replaceTags(temp, data, index))


def copy_html_aliases(target_dir):
    for directory, _, files in os.walk(target_dir):
        for file_name in files:
            if "." in file_name:
                continue
            source = os.path.join(directory, file_name)
            shutil.copyfile(source, source + ".html")


def main():
    if os.path.exists("config.json"):
        with open("config.json") as config_file:
            config.update(json.load(config_file))

    source_directory = os.getcwd()
    try:
        os.chdir(config["pages"])
        index = make_index()
    finally:
        os.chdir(source_directory)

    make_site(config["live"], index)
    copy_html_aliases(config["live"])


if __name__ == "__main__":
    main()
