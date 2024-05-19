import os
import google.generativeai as genai
import time

base = "/Users/julieqiu/Downloads/tiktok"
dir_list = os.listdir(base)
for video_file_name in dir_list:
  # video_file_name="/Users/julieqiu/Downloads/tiktok/tiktok.mp4"
  print(f"Uploading file...")
  video_file = genai.upload_file(path=base+"/"+video_file_name)
  print(f"Completed upload: {video_file.uri}")


  while video_file.state.name == "PROCESSING":
      print('.', end='')
      time.sleep(10)
      video_file = genai.get_file(video_file.name)

  if video_file.state.name == "FAILED":
    raise ValueError(video_file.state.name)

  # Create the prompt.
  prompt = "You are creating a NYC bucket list and want a list of places to visit. Tell me the places recommended in this video."

  # Set the model to Gemini 1.5 Pro.
  model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")

  # Make the LLM request.
  print("Making LLM inference request...")
  response = model.generate_content([prompt, video_file],
                                    request_options={"timeout": 600})
  print(response.text)
