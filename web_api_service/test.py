picture_rudiments = ['‘', '"']

test_w = 'go " to""""" ai"""'
for i in picture_rudiments:
    test_w = test_w.replace(i, '')
    print(i)

print(test_w)