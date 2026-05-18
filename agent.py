import json, os, time
from typing import Optional
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

class AIAgent:
    def __init__(self, model="llama-3.3-70b-versatile"):
        self.model = model

    def run(self, task, system_prompt=None):
        if system_prompt is None:
            system_prompt = "You are a helpful assistant. Always respond in valid JSON with a 'result' key and a 'confidence' key as a float between 0 and 1. No markdown or backticks."
        start = time.time()
        try:
            r = client.chat.completions.create(
                model=self.model, max_tokens=512,
                messages=[{"role":"system","content":system_prompt},{"role":"user","content":task}]
            )
            ms = round((time.time()-start)*1000)
            raw = r.choices[0].message.content.strip()
            try:
                parsed = json.loads(raw)
            except:
                parsed = {"result": raw, "confidence": None}
            return {"status":"success","task":task,"output":parsed,"raw":raw,"latency_ms":ms,"model":self.model,"timestamp":time.strftime("%Y-%m-%dT%H:%M:%S")}
        except Exception as e:
            return {"status":"error","task":task,"output":None,"raw":str(e),"latency_ms":round((time.time()-start)*1000),"model":self.model,"timestamp":time.strftime("%Y-%m-%dT%H:%M:%S")}