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


print("Content-type:text/html; charset=utf-8\n")
print("<html>")
print("<head>")
print("<meta charset='UTF-8'>")
print("</head>")
print("  <body>")
print("    <h1>About</h1>")
print(navigator)
print("Finding a job as a teen isn’t easy — we know because we’ve been there. That’s why we created JobNest, a place dedicated to helping teens under 18 find real, up-to-date job opportunities. Whether you’re looking for your first part-time gig, a summer job, or a flexible position after school, we make it simple to discover who’s hiring and what you’ll need to apply. Our goal is to take the stress out of job hunting and help you take the first step toward building experience, earning money, and growing your future.")
print("  </body>")
print("</html>")
