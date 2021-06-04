import sys
import time
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# To control logging level for various modules used in the application:
import logging

# Ubuntu
# logging.basicConfig(filename='headline.log', level=logging.DEBUG)

logging.basicConfig(filename='headline.log', level=logging.DEBUG)


def filter_beams(titles):
    filtered_titles = []
    for titles_groups in titles:
        filtered_titles_groups = []
        for title in titles_groups:
            if ('?' not in title and
                    '!' not in title and
                    '.' not in title and
                    ',' not in title and
                    ' we ' not in title.lower() and
                    ' is ' not in title.lower() and
                    ' are ' not in title.lower() and
                    ' can ' not in title.lower() and
                    ' have ' not in title.lower() and
                    "we'" not in title.lower() and
                    "i'" not in title.lower() and
                    "it'" not in title.lower() and
                    "ing" not in title.lower() and
                    "get " not in title.lower() and
                    "welcome " not in title.lower() and
                    len(title) > 10 and
                    ('all ' != title.lower()[:4] and ' all ' not in title.lower())):
                filtered_titles_groups.append(title.strip())
        if len(filtered_titles_groups) == 0:
            filtered_titles.append([t for t in titles_groups[:1]][0])
        else:
            filtered_titles.append(sorted(
                filtered_titles_groups,
                key=lambda x: abs(len(x) - np.mean([len(l) for l in filtered_titles_groups]))
            )[0])
    return filtered_titles


def generate_titles(segments):
    titles = []
    for block in segments:
        clean_text = '\n'.join(block)
        start_time = time.time()
        inputs = tokenizer.encode(clean_text, return_tensors="pt", truncation='longest_first', max_length=1024)
        beam_outputs = model.generate(inputs.to(device), max_length=64, length_penalty=0.5, repetition_penalty=2.5,
                                    early_stopping=True, num_return_sequences=13, num_beams=13)
        title = [tokenizer.decode(beam_output, skip_special_tokens=True, clean_up_tokenization_spaces=True)
                  for beam_output in beam_outputs]
        
        end_time = time.time()
        logging.info(f'Time taken : {end_time - start_time}')

        titles.append(title)
    titles = filter_beams(titles)
    return titles


if __name__ == "__main__":
    st_time = time.time()
    
    if len(sys.argv) > 2:
        if torch.cuda.is_available():
            logging.info("Using GPU for inference acceleration")
            device = torch.device('cuda')
        else:
            logging.info("GPU not detected, using CPU for inference")
            device = torch.device('cpu')
        model = AutoModelForSeq2SeqLM.from_pretrained("Michau/t5-base-en-generate-headline", max_length=1024).to(device)
        tokenizer = AutoTokenizer.from_pretrained("Michau/t5-base-en-generate-headline")

        segments = []
        f = open(sys.argv[1], 'r', encoding='utf-8')
        state = False
        paragraphs = []
        for x in f:
            if "-----" in x:
                if len(paragraphs) > 0:
                    segments.append(paragraphs)
                paragraphs = []
            else:
                paragraphs.append(x)

        if len(paragraphs) > 0:
            segments.append(paragraphs)

        titles = generate_titles(segments)

        f = open(sys.argv[2], 'w', encoding='utf-8')
        for i, block in enumerate(segments):
            title = titles[i]
            text = "\n".join(block)
            f.write('-----\n')
            f.write(title + '\n')
            f.write(text + '\n')
        f.close()
    else:
        logging.error("Please provide input and output filename")

    logging.info("Ended.....{}".format(time.time() - st_time))
