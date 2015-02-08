# Log Trimmer
Cuts out parts of log files, based on timestamp. Uses binary search to efficiently find bounds.

# Examples:
Cut log with standard timestamp format.

```log_trimmer.py -r "2012-10-09 15:45:38" "2012-10-12 14:34:43" -f bigbig.log```

Custom format (Python notation):

```log_trimmer.py -r "30-01-1999 15:55:09" "02-02-1999 22:01:01" -f file.log -t "%d-%m-%Y %H:%M:%S"```
