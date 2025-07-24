#!/usr/bin/env python3
import os.path

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
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  font-family: Arial, sans-serif;
  display: flex;
  flex-direction: column;
}

main {
  flex-grow: 1;
  text-align: center;
  padding: 20px;
  background-color: #fafafa;
}

p {
  max-width: 800px;
  margin: 20px auto;
  font-size: 1.1em;
}

hr {
  border: none;
  border-top: 1px solid #ccc;
  margin: 20px 0;
}
.nav-link {
  text-decoration: none;
  color: #333;
  margin: 0 10px;
  font-weight: normal;
}

.nav-link:hover,
.active {
  font-weight: bold;
  color: #000;
}

.nav-container {
  text-align: center;
  margin-bottom: 10px;
}


select {
  font-family: Arial, sans-serif;
  font-size: 1.1em;
  margin: 10px;
}

footer {
  font-size: 0.8em;
  color: #777;
  text-align: center;
  padding: 20px 10px;
  background-color: #f0f0f0;
}
        .header-background {
        background-image: url('https://mangohub.app/mangobackground1.png');
        background-size: auto;
        background-repeat: repeat -x;
        background-position: center -50px;
        text-align: center;
        padding: 60px 0;
        color: black;
        }
        .header-background h1, .header-background p {
        margin: 0;
        padding: 0;
        }


@media only screen and (max-width: 1000px) {
  /* Phone-specific styles here */
  body {
    font-size: 250%;
  }
</style>
</head>
"""

navigator = """
<hr>
<div class="nav-container">
  <p>
    <a href="index.html" class="nav-link">Home</a> |
    <a href="about.html" class="active">About</a>
  </p>
</div>
<hr>
"""

footer = """
<footer>
  <p>Contact us at <a href="mailto:support@mangohub.app">support@mangohub.app</a></p>
  <p>&copy; 2025 MangoHub. All rights reserved.</p>
</footer>
"""

print("Content-type:text/html; charset=utf-8\n")
print(style)
print("<html>")
print("<head><meta charset='UTF-8'></head>")
print("<body>")
print('<main>')
print("""
<div class="header-background">
  <h1>mangohub</h1>
</div>
""")
print(navigator)
print('<h2>About</h2>')
print('<p>Finding a job as a teen is tough—we get it because we’ve been there too. That’s why we built mangohub, a spot made just for teens under 18 to find real, updated job listings. Whether you’re hunting for your first part-time gig, a summer job, or something flexible after school, we help you easily see who’s hiring and what they need from you. No stress—just straightforward help so you can start gaining experience, making money, and setting up your future.</p>')
print('</main>')
print(footer)
print("</body>")
print("</html>")

