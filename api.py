from flask import Flask, render_template, jsonify, request
from urllib.parse import unquote
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain
from langchain.memory import ConversationBufferMemory
from langchain.utilities import WikipediaAPIWrapper

from decouple import config

from web import decode_website
# from doc import decoded_doc
from summary import summarize_webpage

import os
import nltk
nltk.data.path.append('nltk_data')

os.environ["OPENAI_API_KEY"] = config('OPENAI_API_KEY')
app = Flask(__name__) 
llm = OpenAI(temperature=0.9)

title_template = PromptTemplate(
    input_variables = ['topic'],
    template = "The synopsis for a book about {topic}.",
)

title_memory = ConversationBufferMemory(input_key='topic', memory_key='chat_history')

title_chain = LLMChain(llm=llm, prompt=title_template, verbose=True, output_key='title', memory=title_memory)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/data', methods=['GET','POST'])
def get_data():
    if request.method == 'GET':
        sample_data = {
            'message': 'Hello, Flask API!',
            'data': [1, 2, 3, 4, 5]
        }
        print ("DEBUG",sample_data)
        return jsonify(sample_data)
    elif request.method == 'POST':
        print ("DEBUG request",request)
        encode_url = unquote(unquote(request.args.get('url')))
        print ("DEBUG encode_url",encode_url)
        if not encode_url:
            return jsonify({'error': 'URL is required'}), 400

        decoded_text = decode_website(encode_url)

        print ("DEBUG decoded_text",decoded_text)

        summary = summarize_webpage(decoded_text)

        print ("body", request.json)

        response = {
            'submitted_url': encode_url,
            'summary': summary,
        }

        return jsonify(response)
        

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, host='0.0.0.0', port=port)


