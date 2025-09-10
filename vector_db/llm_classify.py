import json,requests, os
from dotenv import load_dotenv
load_dotenv()
URL = os.getenv("URL")
KEY = os.getenv("KEY")

def llm_classify(user_message):
    prompt = f"""# Personal:
Bạn là 1 agent chuyên nghiệp trong lĩnh vực phân loại câu hỏi chung chung hay không chung chung

# User message:
{user_message}

# Instruction:
- Nhiệm vụ: Chỉ phân loại câu hỏi có phải là "general" hay "non_general".
- Nếu câu hỏi mang tính chung chung (không chỉ rõ chương trình/địa điểm/thời gian cụ thể) → trả về "general".
- Nếu câu hỏi đã rõ ràng (nói đến chương trình cụ thể, địa điểm cụ thể, thời gian cụ thể) → trả về "non_general".
- Chỉ được phép trả về duy nhất một từ trong hai lựa chọn: "general" hoặc "non_general".
- Không giải thích, không thêm ký tự, không thêm văn bản nào khác ngoài hai giá trị trên.

# Exsamples:
+ Trả về "general":
- 'hôm nay có những chương trình khuyến mãi nào?'
- 'hiện tại đang có chương trình khuyến mãi nào bạn'
- 'bên mình có chương trình gì không'
- 'cuối tuần này có chương trình khuyến mãi nào không'
- 'ngày mai có chương trình gì không bạn'
- 'bên mình có giảm giá gì không'
- 'cho tôi xem chương trình khuyến mãi'
- 'Đang có chương trình khuyến mãi gì cho 6 người lớn và 2 trẻ em 6 tuổi không bạn nhỉ'
- Nếu người dùng hỏi chương trình khuyến mãi áp dụng cho xx người nhưng không đề cập đến địa chỉ áp dụng thì là 1 câu hỏi chung.

+ Trả về "non_general":
- 'Khi nào chương trình khuyến mãi cho học sinh bắt đầu'
- 'Chương trình sinh nhật có áp dụng hôm nay không'
- 'Chương trình buffet yatai ở hà nội có đang giảm giá không'
- 'Chương trình giảm 400k ở nguyễn văn lộc đang có giảm sâu không nhỉ'
- Nói rõ về 1 chương trình khuyến mãi

# Answer:
"""
    url = URL
    headers = {
        "Authorization": KEY,
        "Content-Type": "application/json"
    }
    payload = json.dumps({
        "model": "Llama-3.3-70B-Instruct",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 50,
        "temperature": 0.1,
        "top_p": 0.95
    })
    response = requests.post(url=url, headers=headers, data = payload)
    result = response.json().get("choices", [])[0]["message"]["content"].strip()
    return result