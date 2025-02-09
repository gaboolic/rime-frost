from datasets import load_dataset
dataset = load_dataset("liwu/MNBVC", 'law_judgement', split='train', streaming=True)

next(iter(dataset))  # get the first line
