from transformers import AutoTokenizer, AutoModel
import os

save_path = "./models/multilingual-e5-base"

# Tải và lưu tokenizer
tokenizer = AutoTokenizer.from_pretrained("intfloat/multilingual-e5-base")
tokenizer.save_pretrained(save_path)

# Tải và lưu model
model = AutoModel.from_pretrained("intfloat/multilingual-e5-base")
model.save_pretrained(save_path)

from sentence_transformers import CrossEncoder

save_path = "./models/ms-marco-MiniLM-L-6-v2"

# Tải và lưu về local
model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
model.save(save_path)

