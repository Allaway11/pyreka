![logo](.images/logo.jpeg)

## :construction::wrench: Installation
```bash
pip install pyreka
```

## :page_with_curl: Usage
`pyreka` can be used to search functions using function names and docstrings in packages and directories.

For example to search in `numpy` the following commands could be issued from the command line.

Firstly, install numpy
```bash
pip install numpy
```

and then from the same environment search the numpy package for keywords:

```bash
pyreka numpy "sort array indices"
```

First you will be asked if you are searching a local directory or for a package in your environment, then you should see a number of functions returned, along with the file that they live in and the line number for each returned function you can also scroll their docstrings.

<center style="font-size: 26px">:confetti_ball:</center>