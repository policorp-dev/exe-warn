#
# Regular cron jobs for the exec-warn package.
#
0 4	* * *	root	[ -x /usr/bin/exec-warn_maintenance ] && /usr/bin/exec-warn_maintenance
