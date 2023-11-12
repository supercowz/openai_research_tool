import argparse
import os

from openai import OpenAI
from newspaper import Article

def file_exists(file_name):
    try:
        with open(file_name, 'r') as file:
            return True
    except FileNotFoundError:
        return False

def read_from_file(file_name):
    with open(file_name, 'r') as file:
        content = file.read()
    return content

def get_list_from_file(file_name):
    with open(file_name, 'r') as file:
        content = file.readlines()
    return content

def save_content_to_file(summary, file_name):
    with open(file_name, 'w') as file:
        content = file.write(summary)

    return True

def get_spr_summaries():
    i = 0
    while True:
        file_name = f"summary_{i}.txt"
        try:
            with open(file_name, 'r') as file:
                content = file.read()
                yield content
                
        except FileNotFoundError:
            break
        i = i + 1

def summarizer():
    ans = ""
    if file_exists("summary_0.txt"):
        ans = input("Would you like to overwrite your existing summaries? Y/N? > ").lower().strip()

        if not (ans.startswith("yes") or ans == "y" or ans.startswith("yea")):
            print("Summaries not generated. Skipped.")
            return

    SPR_GEN_PROMPT = read_from_file("spr_gen.txt")
    URLS = get_list_from_file("urls.txt")

    if len(URLS) <= 0:
        print("Please include at least 1 url in your 'urls.txt' text file.")
        return

    article_text = ""
    i = 0
    print("Generating summaries...")
    for url in URLS:
        #  -- useful statement to add to research if needed.
        article = Article(url)
        article.download()
        article.parse()
        article_text = article.text

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SPR_GEN_PROMPT},
                {"role": "user", "content": article_text},
            ]
        )

        response = response.choices[0].message.content
        save_content_to_file(response, f'summary_{i}.txt')
        i = i + 1
    
    print("------------------------------------------------")
    print("your summaries have been generated. They are saved as 'summary_X.txt'")
    print("------------------------------------------------")

def research_paper_generator():
    ans = ""
    if file_exists("final_research_paper.txt"):
        ans = input("Would you like to overwrite your existing research paper? Y/N? > ").lower().strip()

        if not (ans.startswith("yes") or ans == "y" or ans.startswith("yea")):
            print("Research paper not generated. Skipped.")
            return

    SPR_DECOMP_PROMPT = read_from_file("spr_decomp_research.txt")
    research_about = input("What is the research topic? ie. 'climate change', 'deforestation', 'the effect of animal agriculture on climate change' > ")
    SPR_DECOMP_PROMPT = SPR_DECOMP_PROMPT.replace("{{ABOUT}}", research_about)

    print("Generating research paper...")

    i = 0
    spr_summaries = get_spr_summaries()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": SPR_DECOMP_PROMPT},
            {"role": "user", "content": '\n'.join(spr_summaries)},
        ]
    )

    response = response.choices[0].message.content
    save_content_to_file(response, "final_research_paper.txt")
    print("------------------------------------------------")
    print("your research paper has been generated. It is saved under 'final_research_paper.txt'")
    print("------------------------------------------------")

def wiki_article_generator():
    ans = ""
    if file_exists("final_wiki.txt"):
        ans = input("Would you like to overwrite your existing wiki article? Y/N? > ").lower().strip()

        if not (ans.startswith("yes") or ans == "y" or ans.startswith("yea")):
            print("Wiki article not generated. Skipped.")
            return

    SPR_DECOMP_PROMPT = read_from_file("spr_decomp_wiki.txt")
    wiki_about = input("What is the wiki topic? ie. 'vegan fitness', 'nutrition', 'essential nutrients' > ")
    SPR_DECOMP_PROMPT = SPR_DECOMP_PROMPT.replace("{{ABOUT}}", wiki_about)

    print("Generating wiki article...")

    i = 0
    spr_summaries = get_spr_summaries()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": SPR_DECOMP_PROMPT},
            {"role": "user", "content": '\n'.join(spr_summaries)},
        ]
    )

    response = response.choices[0].message.content
    save_content_to_file(response, "final_wiki.txt")
    print("------------------------------------------------")
    print("your wiki article has been generated. It is saved under 'final_wiki.txt'")
    print("------------------------------------------------")



client = None
if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')

    try:
        api_key = read_from_file("token.txt")
    except FileNotFoundError:
        print("Please create a text file called 'token.txt' that contains your OpenAI API key")
        exit()

    client = OpenAI(
        api_key=api_key
    )

    parser = argparse.ArgumentParser(description="Command-line tool for summarization and wiki generation.")
    parser.add_argument("--summarize", action="store_true", help="Generate summaries to be used later. Must have a 'urls.txt' file in the same file directory to generate from.")
    parser.add_argument("--wiki", action="store_true", help="Generate a wiki article using the generated summaries.")
    parser.add_argument("--research", action="store_true", help="Generate a research paper using the generated summaries")
    
    args = parser.parse_args()
    
    if args.summarize:
        if not file_exists("urls.txt"):
            print("Please create a text file called 'urls.txt', with at least 1 url. Each url should be on it's own line.")
            print("This program will pull content from each url and summarize it.")
            exit()

        summarizer()
    
    if args.wiki:
        if not file_exists("summary_0.txt"):
            print("No summaries have been generated yet, please do that before generating a wiki article. Run this program with the '--summarize' flag.")
            print("Example: python3 summarizer.py --summarize")
            exit()

        wiki_article_generator()

    if args.research:
        if not file_exists("summary_0.txt"):
            print("No summaries have been generated yet, please do that before generating a research paper. Run this program with the '--summarize' flag.")
            print("Example: python3 summarizer.py --summarize")
            exit()

        research_paper_generator()
    
    if not (args.research or args.wiki or args.summarize):
        print("Please specify an action: --summarize or --wiki or --research")
        print("Example: python3 summarizer.py --summarize")
        print("Example: python3 summarizer.py --summarize --wiki --research")
        print("Example: python3 summarizer.py --wiki")