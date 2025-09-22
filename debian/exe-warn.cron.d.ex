#
# Regular cron jobs for the exe-warn package.
#
0 4	* * *	root	[ -x /usr/bin/exe-warn_maintenance ] && /usr/bin/exe-warn_maintenance
