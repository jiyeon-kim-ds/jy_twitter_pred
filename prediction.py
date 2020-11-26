# 트윗분석
X_1 = ['', 'apple is red', 'orange is orange']

X_2 = ['driving a car', 'riding a bike']

Y_1 = 'fruits'

Y_2 = 'transportation'

classifier = LogisticRegression()

em_X_1 = en.encode(texts=X_1)
em_X_2 = en.encode(texts=X_2)
print('> Complete encoding X values')


def append_to_with_label(to_arr, from_arr, label_arr, label):
    for item in from_arr:
        to_arr.append(item)
        label_arr.append(label)

X = []
y = []

append_to_with_label(X, em_X_1, y, Y_1)
append_to_with_label(X, em_X_2, y, Y_2)

classifier.fit(X, y)

