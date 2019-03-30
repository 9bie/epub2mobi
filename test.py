import requests

def string_middle(start_str, end, html):
    try:
        start = html.find(start_str)
        if start >= 0:
            start += len(start_str)
            end = html.find(end, start)
            if end >= 0:
                return html[start:end].strip()
    except:
        return None
wenku8menu = "https://www.wenku8.net/modules/article/reader.php?aid=93"
html = requests.get(wenku8menu).text
print(html)
filename = string_middle('<div id="title">','</div>',html)
print(filename)