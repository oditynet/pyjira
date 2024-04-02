Аналог jira 
умеет добавлять пользователя, задачи, изменять статус
```
python jira.py -h 
```

build binary:

```
cython jira.py --embed
PYTHONLIBVER=python$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')$(python3-config --abiflags)
gcc -Os $(python3-config --includes) jira.c -o jira $(python3-config --ldflags) -l$PYTHONLIBVER
```
