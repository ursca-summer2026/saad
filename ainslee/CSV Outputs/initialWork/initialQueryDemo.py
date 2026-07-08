import ollama

model = input(" Enter the model you want to use (e.g. 'llama3' or 'phi3') : ")
prompt = input(" Enter the prompt you want to use (e.g. 'Explain what Apple Corporation does.') : ")


def modelQuery(model, prompt) -> str:
    stream = ollama.chat(
        model=model,
        messages=[{'role': 'user', 'content': prompt}],
        stream=True,
    )
    return stream
# end of model_query function()


def playBackResponse(stream) -> None:
    text_limit_size = 10
    for chunk in stream:
        if 'message' in chunk and 'content' in chunk['message']:
            content = chunk['message']['content']
            if len(content) < text_limit_size:
                content = content[:text_limit_size]
            else:
                print("__end of response__")
                break
            # print(content, end='', flush=True)
            print(f"{content}", end='', flush=True)
# end of play_back_response()


def main(model=model, prompt=prompt):
    # model = 'phi3'
    # prompt = 'a nurse walks into a bar ...'
    number_of_times_to_run = 2
    for i in range(number_of_times_to_run):
        print(f"\n --- response number {i+1} --- \n")
        stream = modelQuery(model, prompt)
        playBackResponse(stream)
# end of main()

if __name__ == "__main__":
    main()