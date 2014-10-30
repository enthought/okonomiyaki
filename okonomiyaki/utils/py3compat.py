import six

if six.PY2:
    long = long
else:
    long = int
