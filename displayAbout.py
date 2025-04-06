#!/usr/bin/env python3

navigator = """
<hr>
<p>
<font size="5">
<b>
<a href="main.html">Home</a>
 | 
<font color="gray">About</font>
</b>
</font>
</p>
<hr>
"""

print("Content-type:text/html")
print("  <body>")
print("    <h1>About</h1>")
print(navigator)
print("  </body>")
