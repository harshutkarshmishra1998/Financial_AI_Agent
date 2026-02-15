import spacy #type: ignore

nlp = spacy.load("en_core_web_sm")
doc = nlp("Why did Tesla stock rise last month?")

print("Entities:", [(e.text, e.label_) for e in doc.ents])