My Website
----------

This is source code for my personal site. I have templates for consistent headers and a content folder with my writing. Below is a sketch of what is in each directory followed by a brief todo list.

blogs
-----
JSON files describing metadata for my blog posts

content
-------
html files which correspond to the actual writing of my blog posts. Its injected into $Content in the template file

nongenerated
------------
In this directory there are html, js, css and assets that appear as is on my site. As opposed to the blogs and index files which are generated from a combination of template and content. The folder is organized exactly as my final site is with generated files missing.

scripts
-------
An ad hoc and personal reimplementation of what I imagine angular is. There's a script to sync my local copy of the website to where it is hosted on AWS

templates
---------
In this folder are .temp files which encode partial html files which are completed by including $Content and filling in data specified by <$ $> tags.

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
* Make site better for mobile
* Add latex to the site. For Z^5
