cron_remainder by drozdek
============================

<p>This application can tell you when next job execution will be for your current user.</p>

<p>It processes through your crontab file and syslogs. It doesn't require root privileges.</p>

<p>I made the alias in the .bashrc for this and launch along with bash or manually.
You can do the same or use it in any other way.</p>

<p>Among other things, you can use any part of this code. I don't mind.</p>

<h4>CHANGES:</h4>
<ul><li><b>08 Nov 2014:</b> the base of future application. Still some bugs and defects, but work.
For now, compatible only with set of rules like this -
"0 12 * 1,3,7,10,12 * echo 'Donate blood.'". (digits, *, ',', any job)
Also you need specify cron logs destination.
For CentOS it will be '/var/log/cron'.</li></ul>
