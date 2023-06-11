
data = '{ "text": "\\u9ed1\\u5316\\u80a5\\u4f1a\\u6325\\u53d1,\\u7070\\u5316\\u80a5\\u4f1a\\u53d1\\u9ed1\\u3002" }'

start_marker = '"text": "'
end_marker = '"'

start = data.index(start_marker) + len(start_marker)
end = data.index(end_marker, start)

uni_text = data[start:end]
text = data[start:end].encode('utf-8').decode('unicode_escape')

print(uni_text)
print(text)

