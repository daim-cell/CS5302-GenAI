import os
import PyPDF2
import re
import openai
from config import OPEN_AI_KEY


openai.api_key = OPEN_AI_KEY

def generation(summarized_content, query):
    
 
        client = openai.OpenAI(api_key=openai.api_key) 
 
        try:
            content = ''
            for i, summary in enumerate(summarized_content):
                 content += f"Paper Summary {i+1}: {summary['summarized_content']}\n"
            prompt = [ {"role": "system", "content": "You are a AI-powered educational content enhancement tool that enrich user provided content using provided research summaries. Don't mention any papers. Respond in markdown form"},{"role": "user", "content": f"Based on the summaries: {content} Enhance the content '{query}'"}]
            print(prompt[1]['content'])
            model = "gpt-3.5-turbo"
            response = client.chat.completions.create(
                            model= model,
                            messages= prompt,
                            temperature = 0.0 )
    
            generated_content = response.choices[0].message.content #response["choices"][0]["message"]["content"]
            
        
        except Exception as e: 
            print(f"an error occurred while generation: {e}")
        
        
        return generated_content