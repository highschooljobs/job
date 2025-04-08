#!/usr/bin/env python3

navigator = """
<hr>
<p>
<font size="5">
<b>
<a href="index.html">Home</a>
 | 
<font color="gray">About</font>
</b>
</font>
</p>
<hr>
"""

print("Content-type:text/html")
print("<html>")
print("  <body>")
print("    <h1>About</h1>")
print(navigator)
print("  </body>")
print("</html>")
