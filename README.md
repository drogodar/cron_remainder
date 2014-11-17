cron_remainder by drozdek
============================

<p>This application can tell you when next job execution will be for your current user.</p>

<p>It processes through your crontab file and syslogs. It doesn't require root privileges.</p>

<p>I made the alias in the .bashrc for this and launch along with bash or manually.
You can do the same or use it in any other way.</p>

<p>Among other things, you can use any part of this code. I don't mind.</p>

<h4>CHANGES:</h4>
<ul><li><b>17 Nov 2014:</b> Add functionality for week days. Rebuilt next_day_calc(). Fixed some bugs.</li>
<li><b>09 Nov 2014:</b> Expand the functionality. Now you can specify '*/5', '2-10/2' or even 
'1,3,10-23,25,29-30' views for month, day, hour and minute. Also fixed some bugs.
Still don't have compatibility with '?', 'L', 'M' and days of week. Coming soon.</li>
<li><b>08 Nov 2014:</b> The base of future application. Still some bugs and defects, but work.
For now, compatible only with set of rules like this -
"0 12 * 1,3,7,10,12 * echo 'Donate blood.'". (digits, *, ',', any job)
Also you need specify cron logs destination.
For CentOS it will be '/var/log/cron'.</li></ul>





