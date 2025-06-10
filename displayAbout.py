#!/usr/bin/env python3
style = """
<head>
<style>
table {
  margin-top: 20px;
  font-family: arial, sans-serif;
  border-collapse: collapse;
  width: 100%;
}

body {
  font-family: arial, sans-serif;
}

select {
  font-family: arial, sans-serif;
  font-size: 110%;
}

td, th {
  border: 1px solid #dddddd;
  text-align: left;
  padding: 8px;
}

td:nth-child(2) {
  max-width: 300px;
  word-wrap: break-word;
}

tr:nth-child(even) {
  background-color: #dddddd;
}

/* Add this class for centering text */
.centered {
  text-align: center;
}
</style>
</head>
"""
navigator = """
<hr>
<style>
  .nav-link {
    text-decoration: none;
    font-weight: normal;
    color: black;
  }

  .nav-link:hover {
    font-weight: bold;
  }

  .active {
    font-weight: bold;
    color: black;
    text-decoration: none;
  }

  .nav-container {
    text-align: center;
  }
</style>

<div class="nav-container">
  <p>
    <a href="index.html" class="nav-link">Home</a> |
    <a href="about.html" class="active">About</a>
  </p>
</div>
<hr>
"""

print("Content-type:text/html; charset=utf-8\n")
print(style)
print("<html>")
print("<head>")
print("<meta charset='UTF-8'>")
print("</head>")
print("  <body>")
print('    <h1 style="text-align: center;">About</h1>')
print(navigator)
print("Finding a job as a teen isn’t easy — we know because we’ve been there. That’s why we created JobNest, a place dedicated to helping teens under 18 find real, up-to-date job opportunities. Whether you’re looking for your first part-time gig, a summer job, or a flexible position after school, we make it simple to discover who’s hiring and what you’ll need to apply. Our goal is to take the stress out of job hunting and help you take the first step toward building experience, earning money, and growing your future.")
print("  </body>")
print("</html>")
