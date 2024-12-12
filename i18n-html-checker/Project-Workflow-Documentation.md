The Python code analyzes HTML code to identify missing internationalization (i18n) tags and attributes. 

Architecture:

1. File Upload (Streamlit):

Input: User uploads an HTML file through the Streamlit file uploader.

Process: The HTML file's contents are read and decoded into a UTF-8 string.

Output: html_code (string containing the HTML content).

2. i18n Tag and Attribute Analysis:

Input: html_code

Process: Several functions analyze the HTML for different i18n aspects:

find_tags_without_i18n_title(): Finds tags with the [title] attribute but missing the i18n-title attribute.

extract_label_i18n_map(): Extracts label and i18n-label attributes, identifies missing i18n-label values.

check_i18n_ids(): Extracts text within tags that have the i18n attribute.

text_content_extraction(): Extracts all text content from the HTML.

extract_i18n_matTooltip(): Extracts text within tags having the i18n-matTooltip attribute.

extract_placeholder_text(): Extracts text within tags having the [placeHolderText] attribute.

find_missing_text_content(): Compares text content with i18n-tagged text to identify potentially missing i18n tags.

Output: JSON strings or Python dictionaries containing the analysis results (e.g., lists of missing tags, labels without i18n counterparts).

3. LLM Integration (for missing text content):

Input: missing_text_content (list of text strings potentially needing i18n), html_code

Process:

If missing_text_content is not empty, a prompt is constructed for an Azure OpenAI LLM.

The prompt asks the LLM to identify the HTML tags enclosing the missing text content.

The LLM's JSON response is parsed.

If the LLM response is valid (matches the expected format), it's saved as result.json.

If the LLM response is invalid or an error occurs, the missing text content is written to result.txt as a fallback.

Output: result.json (if successful LLM interaction) or result.txt (fallback).

4. Output and Display (Streamlit):

Input: Analysis results from step 2 and LLM results from step 3.

Process:

The code checks for the existence of result.json and displays its contents as formatted JSON in Streamlit. If the file doesn't exist (LLM error or invalid response), it displays the contents of result.txt.

It displays the results of other i18n analyses (filtered_labels.json, missing_i18n_titles.json, placeholder_text.json) in Streamlit, using formatted JSON or text areas as appropriate.

Informative messages (success or error messages) are displayed to the user in Streamlit based on the analysis outcomes. Files are moved to an OLD folder after upload.

Output: Streamlit display of analysis results and messages.


Architecture Diagram:

![image](https://github.com/user-attachments/assets/d3d428ea-6f7d-435b-9926-e08edf0e269e)

