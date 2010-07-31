<html>
<head>
<title>Quickfort</title>
<style>
	body { font-family: Segoe UI,Trebuchet MS,sans-serif; margin: 1em }
	pre { margin-left: 2em; }
	#pagebody { max-width: 55em }
</style>
</head>
<body>

<script type="text/javascript">
var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");
document.write(unescape("%3Cscript src='" + gaJsHost + "google-analytics.com/ga.js' type='text/javascript'%3E%3C/script%3E"));
</script>
<script type="text/javascript">
try {
var pageTracker = _gat._getTracker("UA-4298456-1");
pageTracker._trackPageview();
} catch(err) {}</script>

<div id="pagebody">
<h1>Quickfort</h1>
A construction tool for Dwarf Fortress
<BR><BR>
<B>
	<img src="minihammer.gif">&nbsp;<a href="Quickfort.zip" onClick="javascript: pageTracker._trackPageview('/quickfort/Quickfort.zip');">Download latest version of Quickfort here</a> (<a href="#changelog">changelog</a>)
	<BR><BR>
	<img src="x.gif" width=16 height=16>&nbsp;<a href="http://www.bay12games.com/forum/index.php?topic=35931.0">Bay12 forum thread</a>
	<BR><BR>
	<img src="x.gif" width=16 height=16>&nbsp;<a href="mailto:quickfort@joelpt.net">Contact author</a>
</B>
<HR>

With Quickfort, you can turn .CSV files like these<BR>
<img src="http://imgur.com/8tpp6.png" alt="" class="bbc_img" /> <img src="http://imgur.com/ohxc7.png" alt="" class="bbc_img" /> <img src="http://imgur.com/5obn9.png" alt="" class="bbc_img" />
<BR><BR>
into something like this.
<BR><BR>
<img src="http://imgur.com/437t2.png" alt="" class="bbc_img" /><BR>

<?php

include_once "markdown.php";

$filename = "readme.txt";
$fh = fopen($filename, 'r');
$text = fread($fh, filesize($filename));
fclose($fh);
echo Markdown($text);

?>
</div>
</body>
</html>

<?

exit()

?>


