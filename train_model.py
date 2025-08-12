# train_model.py
import pickle
from sklearn.tree import DecisionTreeClassifier

# Features: [filename_length, size_MB, extension_code]
# Extensions: exe=1, txt=2, jpg=3, zip=4, pdf=5
X = [
    [10, 0.5, 2],  # benign txt
    [12, 1.2, 3],  # benign jpg
    [20, 50, 1],   # suspicious exe
    [30, 200, 1],  # suspicious exe
    [8, 0.8, 2],   # benign txt
    [25, 5, 4],    # suspicious zip
    [15, 0.2, 5],  # benign pdf
]

y = [0, 0, 1, 1, 0, 1, 0]  # 0 = benign, 1 = malicious

model = DecisionTreeClassifier()
model.fit(X, y)

with open("ai_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("✅ AI model saved as ai_model.pkl")
