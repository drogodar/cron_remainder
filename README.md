cron_remainder by drozdek
============================

<p>This application can tell you when next job execution will be for your current user.</p>

<p>It processes through your crontab file. It doesn't require root privileges.</p>

<h5>Supported features:</h5>
<ul>
<li>'*' - full date range;</li>
<li>'X-Y' - from the X to the Y;</li>
<li>'X,Y' - the X and the Y;</li>
<li>Combination of previous two;</li>
<li>'X/Y' - every Y through the X (can be *)</li>
<li>'Mon-Wed','Jun,Jul,Sep-Dec' - along with numbers for weekdays and months;</li>
</ul>

<h5>The way to use:</h5>
<p>You can just launch the script OR made an alias in the .bashrc for this and launch it manually or along with starting bash.</p>


<h6>CHANGES:</h6>
<ul>
<li><b>19 Nov 2014:</b> Smooth and optimize code. Heal some bugs. Remove unnecessary syslog-thing.</li>
<li><b>17 Nov 2014:</b> Add functionality for week days. Rebuilt next_day_calc(). Fixed some bugs.</li>
<li><b>09 Nov 2014:</b> Expand the functionality. Now you can specify '*/5', '2-10/2' or even 
'1,3,10-23,25,29-30' views for month, day, hour and minute. Also fixed some bugs.
Still don't have compatibility with days of week. Coming soon.</li>
<li><b>08 Nov 2014:</b> The base of future application. Still some bugs and defects, but work.
For now, compatible only with set of rules like this -
"0 12 * 1,3,7,10,12 * echo 'Donate blood.'". (digits, *, ',', any job)
Also you need specify cron logs destination.
For CentOS it will be '/var/log/cron'.</li>
</ul>





