My Website
----------

This is source code for my personal site. I have templates for consistent headers and a content folder with my writing. Below is a sketch of what is in each directory followed by a brief todo list.

scripts
-------
An ad hoc and personal reimplementation of what I imagine angular is. There's a script to sync my local copy of the website to where it is hosted on AWS

blogs
-----
JSON files describing metadata for my blog posts

content
-------
html files which correspond to the actual writing of my blog posts. Its injected into $Content in the template file

live
----
This is the actual website. Right now it is a mix of written files at the top level, assets and blogs derived from running a script which takes in the JSON metadata and the content. In the future I will try to derive experiments, about me and updates from templates as well and get this directory to a state where it is completely derived from source. When that is achieved I will remove it from version control.

TODO
----
* Make this todo list more professional. Maybe use JIRA or make it a page on my site
* More Experiments:
- Random Partition
- Random Polygon
- Make some of the links which go to blog posts which describe their motivation
* Nicer Index Style
* Make site homepage my most recent blog, or something nicer than my index.
* Use cookies to offer user customization?
- Dark Mode
- Browser Notifications
* Make a video game
* Make CSS more maintainable 
