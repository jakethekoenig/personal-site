from subprocess import run

def mathjax(content):
    # Don't want to unnecessarily call node
    if '\[' not in content:
        return content
    # TODO: avoid node dependency, don't hardcode location
    # TODO: cache. I should do this in general.
    p = run(['./node_modules/mathjax-node-page/bin/mjpage', '--output', 'CommonHTML'], input=content.encode(), capture_output=True)
    return p.stdout.decode()


