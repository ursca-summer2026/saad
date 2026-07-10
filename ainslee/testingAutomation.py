import argparse
import csv
import re
import time
import ollama # type: ignore
import os


def queryModel(model, prompt):
    # attempt to load in the input model and query it with the prompt
    # raise an error if the model is not found or the query fails
    try:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
    except Exception as e:
        raise RuntimeError(f"Model query failed. Double-check the model name and try again: {e}")
    
    # seperate the content of the model query and store only the first two sentences in the response
    try:
        text = (response.get("message", {}).get("content")or response.get("content", "")).strip()
    except Exception as e:
        raise RuntimeError(f"Invalid model response format: {e}")

    sentences = re.split(r'(?<=[.!?])\s+', text)
    return ". ".join(sentences[:2]).strip()
# end of queryModel()


def runBatch(model, keyword, prompts, csvFile="results.csv", runs=1, writeHeader=False, startIndex=1):
    rows = []
    currentIndex = startIndex

    # iterate through each prompt and run the model query the specified number of times
    for p in prompts:
        for _ in range(runs):
            answer = queryModel(model, p)
            time.sleep(0.05)
            rows.append({"rowIndex": currentIndex, "keyword": keyword, "prompt": p, "response": answer})
            currentIndex += 1

    # write the results to a CSV file
    # raise an error if the file cannot be written to
    try:
        # mode "write" or "append" depending on whether there is a header
        mode = "w" if writeHeader else "a"
        with open(csvFile, mode, newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["rowIndex", "keyword", "prompt", "response"])
            if writeHeader:
                writer.writeheader()
            writer.writerows(rows)
    except OSError as e:
        raise RuntimeError(f"Could not write to file '{csvFile}': {e}")
    
    return currentIndex
# end of runBatch()


def main():
    parser = argparse.ArgumentParser(description="A sample argparse script for running multiple keyword queries with Ollama.")
    parser.add_argument("-m", "--model", type=str, required=True, help="Model name to use")
    parser.add_argument("-k", "--keywords", type=str, required=True, help="Comma-separated keywords to use")
    parser.add_argument("-r", "--runs", type=int, default=1, help="Number of times to run each prompt (default: 1)")
    parser.add_argument("-o", "--outfile", default="results.csv", help="Output CSV filename")
    parser.add_argument("-f", "--folder", default="output", help="Folder to save the CSV file")
    parser.add_argument("-p", "--prompt", type=str, required=True, help="Prompt to use")

    # separate the user-given termincal command and store the pieces separately
    args = parser.parse_args()
    
    # prase the keyword list
    keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]

    # build the path to the CSV file based on the provided folder and output filename
    csvPath = os.path.join(args.folder, args.outfile)

    # load in the prompts from the provided prompt file
    # replace the {keyword} placeholder in each prompt with the user-provided keyword
    # raise an error if the file is invalid or cannot be read
    try:
        with open(args.prompt, "r", encoding="utf-8") as f:
            basePrompts = [line.rstrip("\n") for line in f]
    except OSError as e:
        print(f"Could not find file. Double-check the file name and try again: {e}")
        return
    
    # validate the model
    try:
        ollama.chat(model=args.model, messages=[{"role": "user", "content": "test"}])
    except Exception as e:
        print(f"Model query failed. Double-check the model name and try again: {e}")
        return

    # ensure the output folder exists
    os.makedirs(args.folder, exist_ok=True)

    # process each keyword & write to a CSV file
    try:
        first = True
        rowIndex = 1
        for keyword in keywords:
            prompts = [p.replace("{keyword}", keyword) for p in basePrompts]
            rowIndex = runBatch(
                args.model,
                keyword,
                prompts,
                csvFile=csvPath,
                runs=args.runs,
                writeHeader=first,
                startIndex=rowIndex
            )
            first = False

    #if any runtime errors occur during the process, print the error message
    except RuntimeError as e:
        print(f"Runtime error: {e}")
# end of main()


if __name__ == "__main__":
    main()
