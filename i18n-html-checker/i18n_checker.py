import os
import re
import json
import shutil
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from collections import Counter
from openai import AzureOpenAI
import streamlit as st
import logging

logging.basicConfig(filename='app.log', level=logging.INFO)


def find_tags_without_i18n_title(html_code):
    # Parse the HTML content
    soup = BeautifulSoup(html_code, 'html.parser')

    # Find all tags with the [title] attribute
    tags_with_title = soup.find_all(lambda tag: tag.has_attr('[title]'))

    # Filter tags that do not have the i18n-title attribute
    tags_without_i18n_title = [str(tag) for tag in tags_with_title if not tag.has_attr('i18n-title')]

    tags_without_i18n_title_output_json = json.dumps({'Missing i18n-title': tags_without_i18n_title}, indent=2)
    
    return tags_without_i18n_title_output_json,tags_without_i18n_title

def extract_label_i18n_map(html_code):
    soup = BeautifulSoup(html_code, 'html.parser')

    label_i18n_map = {}
    tags_with_label = soup.find_all(lambda tag: tag.has_attr('label'))

    for tag in tags_with_label:
        label = tag.get('label')
        i18n_label = tag.get('i18n-label')
        label_i18n_map[label] = i18n_label if i18n_label else None

    filtered_label_i18n_map = {label: i18n_label for label, i18n_label in label_i18n_map.items() if i18n_label is None}
    filtered_json = json.dumps({"Filtered Labels": filtered_label_i18n_map}, indent=2)

    return filtered_json, filtered_label_i18n_map

def write_json_to_file(filtered_json, folder_name, file_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    file_path = os.path.join(os.getcwd(), "Result_Folder", folder_name, file_name)

    with open(file_path, 'w') as file:
        file.write(filtered_json)

def find_missing_text_content(text_content_counts_list, text_with_i18n_tag_counts_list):
    missing_text_content = []
    extracted_dict = dict(text_content_counts_list)
    i18n_dict = dict(text_with_i18n_tag_counts_list)
    for word, count in extracted_dict.items():
        if word in i18n_dict:
            if count != i18n_dict[word]:
                missing_text_content.append(word)
        else:
            missing_text_content.append(word)
    return missing_text_content

def check_i18n_ids(html_code):
    soup = BeautifulSoup(html_code, 'html.parser')
    tags_with_i18n = soup.find_all(attrs={"i18n": True})
    text_with_i18n_tag = [tag.get_text(strip=True) for tag in tags_with_i18n]
    return text_with_i18n_tag

def text_content_extraction(html_code):
    soup = BeautifulSoup(html_code, 'html.parser')
    text_content = soup.get_text()
    text_list = [line.strip().rstrip(',') for line in text_content.split('\n') if line.strip()]
    return text_list

def extract_i18n_matTooltip(html_code):
    pattern = r'<[^>]+\s+i18n-matTooltip="[^"]*"[^>]*>([^<]+)</[^>]+>'
    matches = re.findall(pattern, html_code)
    texts = [match.strip() for match in matches]
    return texts

def extract_placeholder_text(html_code):
    place_holder_regex = r'\[placeHolderText\]="\'(.*?)\'"'
    matches = re.findall(place_holder_regex, html_code)

    if matches:
        placeholder_json = {"[placeHolderText]": matches}
        json_output = json.dumps(placeholder_json, indent=2)
        return json_output,placeholder_json
    else:
        placeholder_json = {"[placeHolderText]":[]}
        json_output = json.dumps(placeholder_json, indent=2)
        return json_output,placeholder_json

def main():
    st.title("MISSING i18n TAG")

    uploaded_file = st.file_uploader("Choose an HTML file", type="html")

    if uploaded_file is not None:
        try:
            html_code = uploaded_file.read().decode('utf-8')

            load_dotenv()

            client = AzureOpenAI(
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version="2024-02-01",
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
            )

            deployment_name = 'langchain-poc'

            source_dir = os.path.join(os.getcwd(), "Result_Folder", "NEW")
            destination_dir = os.path.join(os.getcwd(), "Result_Folder", "OLD")

            os.makedirs(destination_dir, exist_ok=True)

            for filename in os.listdir(source_dir):
                source_file = os.path.join(source_dir, filename)
                destination_file = os.path.join(destination_dir, filename)

                if os.path.isfile(source_file):
                    shutil.move(source_file, destination_file)
                    logging.info(f"Moved: {source_file} -> {destination_file}")

            logging.info("All files have been moved.")

            text_content = text_content_extraction(html_code)
            text_with_i18n_tag = check_i18n_ids(html_code)

            text_content_counts = Counter(text_content)
            text_with_i18n_tag_counts = Counter(text_with_i18n_tag)

            text_content_counts_list = list(text_content_counts.items())
            text_with_i18n_tag_counts_list = list(text_with_i18n_tag_counts.items())

            tag_text__i18n_matTooltip = extract_i18n_matTooltip(html_code)
            tag_text__i18n_matTooltip_counts = Counter(tag_text__i18n_matTooltip)
            tag_text__i18n_matTooltip_counts_lists = list(tag_text__i18n_matTooltip_counts.items())
            changed_text_content_counts_list = [item for item in text_content_counts_list if item not in tag_text__i18n_matTooltip_counts_lists]


            missing_text_content = find_missing_text_content(changed_text_content_counts_list, text_with_i18n_tag_counts_list)

            filtered_json, filtered_label_i18n_map = extract_label_i18n_map(html_code)

            placeholder_text,placeholder_length = extract_placeholder_text(html_code)

            tags_without_i18n_title_output_json,tags_without_i18n_title = find_tags_without_i18n_title(html_code)

            logging.info("filtered_json,filtered_label_i18n_map variable values have assigned successfully.")

            write_json_to_file(filtered_json, 'NEW', 'filtered_labels.json')

            write_json_to_file(placeholder_text, 'NEW', 'placeholder_text.json')

            write_json_to_file(tags_without_i18n_title_output_json, 'NEW', 'missing_i18n_titles.json')



            if missing_text_content:
                prompt_content = f"""

                list of html text content:

                {missing_text_content}

                Html code:

                {html_code}

                Prompt:

                Find the tag which contain the html text content using list of html text content and return the output as json.

                Response:

                {{

                <html text content>:<<tag>text content</tag>>

                }}
                """

                try:
                    response = client.chat.completions.create(messages=[{"role": "system", "content": prompt_content}],
                                                              model=deployment_name, max_tokens=500)

                    data = response.choices[0].message.content
                    result = json.loads(data)

                    file_path = os.path.join(os.getcwd(), "Result_Folder", "NEW", "result.json")

                    keys = result.keys()
                    keys_list = list(keys)

                    if len(keys_list) == len(missing_text_content) and keys_list == missing_text_content:
                        with open(file_path, 'w') as json_file:
                            json.dump(result, json_file, indent=4)
                        logging.info(f"JSON data has been written to {file_path}")
                    else:
                        fallback_file_path = os.path.join(os.getcwd(), "Result_Folder", "NEW", "result.txt")
                        with open(fallback_file_path, 'a') as f:
                            for text in missing_text_content:
                                f.write(f"{text}\n\n")

                except Exception as e:
                    error_message = str(e)
                    fallback_file_path = os.path.join(os.getcwd(), "Result_Folder", "NEW", "result.txt")
                    with open(fallback_file_path, 'a') as f:
                        for text in missing_text_content:
                            f.write(f"{text}\n\n")
                    logging.error(error_message)

                try:
                    base_path = os.path.join(os.getcwd(), "Result_Folder", "NEW")
                    json_file_path = os.path.join(base_path, "result.json")
                    txt_file_path = os.path.join(base_path, "result.txt")

                    if os.path.exists(json_file_path):
                        st.markdown('<span style="color:red;font-size:18px;">MISSING i18n HTML_TEXT_CONTENT WITH TAGS:</span>', unsafe_allow_html=True)
                        with open(json_file_path, 'r', encoding='utf-8') as file:
                            json_data = json.load(file)
                        st.json(json_data)
                    else:
                        st.markdown('<span style="color:red;font-size:18px;">MISSING i18n HTML_TEXT_CONTENT:</span>', unsafe_allow_html=True)
                        with open(txt_file_path, 'r', encoding='utf-8') as file:
                            txt_data = file.read()
                        st.text_area('MISSING i18n HTML_TEXT_CONTENT', txt_data, height=250)

                except Exception as e:
                    st.error(f"Error reading the file: {e}")

            else:
                st.markdown('<span style="color:lightgreen;font-size:20px;">NO MISSING i18n TAGS 😊</span>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error processing the file: {e}")

        try:
            file_path = os.path.join("Result_Folder", "NEW", "filtered_labels.json")

            if len(filtered_label_i18n_map) != 0:
                st.markdown('<span style="color:red;font-size:18px;">MISSING i18n-Label TAGS:</span>', unsafe_allow_html=True)
                with open(file_path, 'r') as file:
                    data = json.load(file)
                st.json(data)
            else:
                st.markdown('<span style="color:lightgreen;font-size:18px;">NO MISSING i18n-Label TAGS 😊</span>', unsafe_allow_html=True)

        except FileNotFoundError:
            st.error(f"File not found: {file_path}")
        except json.JSONDecodeError:
            st.error(f"Error decoding JSON from file: {file_path}")


        try:
            file_path = os.path.join("Result_Folder", "NEW", "missing_i18n_titles.json")

            if len(tags_without_i18n_title) != 0:
                st.markdown('<span style="color:red;font-size:18px;">MISSING i18n-title TAGS:</span>', unsafe_allow_html=True)
                with open(file_path, 'r') as file:
                    data = json.load(file)
                st.json(data)
            else:
                st.markdown('<span style="color:lightgreen;font-size:18px;">NO MISSING i18n-title TAGS 😊</span>', unsafe_allow_html=True)

        except FileNotFoundError:
            st.error(f"File not found: {file_path}")
        except json.JSONDecodeError:
            st.error(f"Error decoding JSON from file: {file_path}")

        try:
            file_path = os.path.join("Result_Folder", "NEW", "placeholder_text.json")

            key = list(placeholder_length.keys())[0]  # Assuming there is only one key in the dictionary
            value_list = placeholder_length[key]
            
            value_list_length = len(value_list)

            if value_list_length != 0:
                st.markdown('<span style="color:red;font-size:18px;">MISSING i18n-placeHolderText TAGS:</span>', unsafe_allow_html=True)
                with open(file_path, 'r') as file:
                    data = json.load(file)
                st.json(data)
            else:
                st.markdown('<span style="color:lightgreen;font-size:18px;">NO MISSING i18n-placeHolderText TAGS 😊</span>', unsafe_allow_html=True)

        except FileNotFoundError:
            st.error(f"File not found: {file_path}")
        except json.JSONDecodeError:
            st.error(f"Error decoding JSON from file: {file_path}")

    else:
        st.warning("Please upload an HTML file.")

if __name__ == "__main__":
    main()
