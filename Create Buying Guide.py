import openai
import base64
from requests import post
import os
from dotenv import load_dotenv
load_dotenv()

api_endpoints = os.getenv('api_endpoints')
openai.api_key = os.getenv('openai.api_key')

wp_user = os.getenv('wp_user')
wp_password = os.getenv('wp_password')
wp_credential = os.getenv('wp_credential')
wp_token = base64.b64encode(wp_credential.encode())
wp_header = {'Authorization': 'Basic ' + wp_token.decode('utf-8')}


def openai_answer(my_prompt):
    """
  We can get the openai answer of questions.
  param my_prompt: It represents my command which I want to get from openai.
  :return: This will return the answer of all questions.
  """
    response = openai.Completion.create(
        model="text-davinci-002",
        prompt=my_prompt,
        temperature=0.7,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    data = response.get('choices')[0].get('text').strip('\n')
    return data


SelectedProduct = open('SelectedProduct.txt', 'r')
keyword_list = []
for product in SelectedProduct:
    keyword = product.strip('\n')
    keyword_list.append(keyword)
keyword = keyword_list[0]  # You can change the index number (among 0,1 & 3) to work with different product name.
SelectedProduct.close()

intro = openai_answer(f'Write an intro about {keyword}')
questions = openai_answer(f'Write 3 questions about buying {keyword}')
conclusion = openai_answer(f'Write an conclusion about {keyword}')

number_list = ['1. ', '2. ', '3. ']
for number in number_list:
    questions = questions.replace(number, '')

question = questions.split('\n')
while '' in question:
    question.remove('')

que_ans_dict = {}
for que in question:
    answer = openai_answer(que)
    que_ans_dict[que] = answer


def wp_heading_two(text):
    """
  This function is for creating heading two (h2) of WordPress.
  :param text: It accepts a text.
  :return: It will return heading two (h2).
  """
    heading_two = f'<!-- wp:heading --><h2>{text}</h2><!-- /wp:heading -->'
    return heading_two


def wp_paragraph(text):
    """
  This function is for creating paragraph (p) of WordPress.
  :param text: It accepts a text.
  :return: It will return paragraph (p).
  """
    paragraph = f'<!-- wp:paragraph --><p>{text}</p><!-- /wp:paragraph -->'
    return paragraph


title = f'Best {keyword} Buying Guide'  # Title Section

content = wp_paragraph(intro)  # Intro Section
for key, value in que_ans_dict.items():  # Question-Answer Section
    h2 = wp_heading_two(key)
    p = wp_paragraph(value)
    content += h2 + p

conclusion_heading = wp_heading_two('Conclusion')  # Conclusion Section
conclusion_paragraph = wp_paragraph(conclusion)
conclusions = f'{conclusion_heading}{conclusion_paragraph}'

final_content = f'{content}{conclusions}'

# Making Slug
slug = title.strip().lower().replace(' ', '-')

data = {
    'title': title,
    'slug': slug,
    'content': final_content,
    'status': 'publish'
}

res = post(api_endpoints, data=data, headers=wp_header, verify=False)

if res.status_code == 201:
    print('Posted Successfully!')
