import os

import google.generativeai as genai

genai.configure(api_key='xxxxxx')

def upload_to_gemini(path, mime_type=None):

  file = genai.upload_file(path, mime_type=mime_type)
  return file

generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}
safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
]

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  safety_settings=safety_settings,
  generation_config=generation_config,
)

image_drive0 = upload_to_gemini(r"D:\captcha\Screenshot 2024-05-29 192324.png", mime_type="image/png")

chat_session = model.start_chat(
  history=[
    {
      "role": "user",
      "parts": [
        image_drive0,
      ],
    },
  ]
)

response = chat_session.send_message("Extract the text from given image.")

print(response.text)
