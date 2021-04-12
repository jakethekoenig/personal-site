Exhibit, a Static Site Generator
----------

This is a collection of scripts I build concurrently with my [personal website!](https://ja3k.com) whose source code can be seen [here!](https://github.com/jakethekoenig/personal-site). At the moment it's no in a state where it'd be easy for anyone else to use. I've decoupled it from the website content to make it easier to move towards that goal. Below is a brief description of the file format this SSG expects to turn into a website.

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

