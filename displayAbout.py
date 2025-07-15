#!/usr/bin/env python3
import os.path

phone = "Phone" in os.environ["HTTP_USER_AGENT"]
if phone:
    style = """
    <head>
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-725428PR4P"></script>
    <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());

    gtag('config', 'G-725428PR4P');
    </script>
    <style>
    table {
     margin-top: 20px;
    font-family: arial, sans-serif;
    border-collapse: collapse;
    width: 100%;
    font-size: 140%;
    }

    body{
    font-family: arial, sans-serif;
    font-size: 200%;
`   text-align: center;
    }

    select{
    font-family: arial, sans-serif;
    font-size: 110%;
    }

    td, th {
    border: 1px solid #dddddd;
    text-align: left;
    padding: 18px;
    }

    td:nth-child(2) {
    max-width: 300px;
    word-wrap: break-word;
    }

    tr:nth-child(even) {
    background-color: #dddddd;
    }
    </style>
    </head>
    """
else:
    style = """
<head>
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-725428PR4P"></script>
    <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());

    gtag('config', 'G-725428PR4P');
    </script>
    <style>
body {
  font-family: Arial, sans-serif;
  text-align: center;
  margin: 0;
  padding: 0;
  line-height: 1.6;
  color: #333;
  background-color: #fafafa;
}

p {
  max-width: 800px;
  margin: 20px auto;
  padding: 0 20px;
  font-size: 1.1em;
  text-align: center;
}
hr {
  border: none;
  border-top: 1px solid #ccc;
  margin: 20px 0;
}

.nav {
  font-size: 1em;
  margin-bottom: 10px;
}

.nav a {
  text-decoration: none;
  color: #333;
  margin: 0 10px;
  font-weight: normal;
}

.nav a:hover,
.nav .active {
  font-weight: bold;
  color: #000;
}

table {
  margin: 40px auto;
  border-collapse: collapse;
  width: 90%;
  max-width: 1000px;
  font-size: 1em;
}

td, th {
  border: 1px solid #dddddd;
  text-align: left;
  padding: 10px;
}

tr:nth-child(even) {
  background-color: #f2f2f2;
}

td:nth-child(2) {
  max-width: 300px;
  word-wrap: break-word;
}

select {
  font-family: Arial, sans-serif;
  font-size: 1.1em;
  margin: 10px;
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
print('    <h1 style="text-align: center;">mangohub</h1>')
print(navigator)
print('    <h2 style="text-align: center;">About</h2>')
print('<p>Finding a job as a teen is tough—we get it because we’ve been there too. That’s why we built JobNest, a spot made just for teens under 18 to find real, updated job listings. Whether you’re hunting for your first part-time gig, a summer job, or something flexible after school, we help you easily see who’s hiring and what they need from you. No stress—just straightforward help so you can start gaining experience, making money, and setting up your future.</p>')
print("  </body>")
print("</html>")
