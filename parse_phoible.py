import pandas as pd

df = pd.read_csv('phoible.csv')

df = df[df['LanguageName'] == 'American English']

print(df.columns)
print(df)
print(df['Phoneme'])
