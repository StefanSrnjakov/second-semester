# Podrobnejši povzetek eksperimentov klasifikacije novic

Ta dokument povzema pet eksperimentov klasifikacije novic iz datoteke `news_categories.json`, kjer je bil cilj klasificirati naslove v več kategorij.

---

## 🔬 Poskus 1: LinearSVC + TF-IDF + Porter Stemmer

- **Model**: OneVsRestClassifier z LinearSVC (max_iter=5000, class_weight='balanced')
- **Preprocesiranje**: 
  - Mala začetnica
  - Odstranitev posebnih znakov
  - Tokenizacija
  - Uporaba PorterStemmer
  - Odstranitev stop besed
- **TF-IDF**: n-grami (1,2), `min_df=5`, `max_df=0.9`, `sublinear_tf=True`
- **Natančnost**: `accuracy = 0.54`
- **Opombe**:
  - Model se je dobro obnesel na bolj zastopanih kategorijah (npr. ENTERTAINMENT, FOOD & DRINK)
  - Težave z bolj subtilnimi kategorijami (npr. FIFTY, GOOD NEWS)
  - Stemming verjetno preagresiven za kompleksnejši kontekst

---

## ⚙️ Poskus 2: Prilagojen LS-TWSVM + TF-IDF + Porter Stemmer

- **Model**: Ročno implementiran Least Squares Twin SVM, ovit v OneVsRestClassifier
- **Preprocesiranje**: Enako kot Poskus 1
- **TF-IDF**: Enako kot Poskus 1
- **Natančnost**: `accuracy = 0.32`
- **Opombe**:
  - Zelo slabi rezultati, predvsem zaradi neefektivnosti LS-TWSVM v večrazrednem okolju
  - Algoritem ni robusten za visoko dimenzionalne vhodne podatke iz TF-IDF
  - Veliko podkategorij napačno klasificiranih

---

## ⚖️ Poskus 3: RidgeClassifier (LS-SVM Approx.) + TF-IDF + Stemming

- **Model**: RidgeClassifier (alpha=1.0), OneVsRest
- **Preprocesiranje**: Enako kot Poskus 1
- **Natančnost**: `accuracy = 0.59`
- **Opombe**:
  - Preprosta linearna rešitev (LS-SVM približek) se izkaže kot robustna
  - Bistveno izboljšani F1-scores
  - Dobro ravnotežje med preciznostjo in pokritostjo

---

## 🧠 Poskus 4: RidgeClassifier + Lemmatization (namesto stemming)

- **Model**: RidgeClassifier
- **Preprocesiranje**: 
  - Lemmatizacija z WordNetLemmatizer
  - Brez POS filtriranja
- **Natančnost**: `accuracy = 0.59` (primerljivo s Poskus 3)
- **Opombe**:
  - Lemmatizacija ohrani več semantične informacije kot stemming
  - Rezultati so skoraj identični Poskusu 3 → vpliv vrste normalizacije ni ključen

---

## 🧪 Poskus 5: RidgeClassifier + Lemmatization + POS Filter

- **Model**: RidgeClassifier
- **Preprocesiranje**:
  - Lemmatizacija + POS filtriranje (samo imenovalniki, glagoli, pridevniki)
- **TF-IDF**: Dodana `max_features=10000`
- **Natančnost**: `accuracy = 0.56`
- **Opombe**:
  - Pos POS filtriranju model izgubi pomembne informacije
  - Rahlo slabši rezultati, F1 manj konsistenten
  - Primeren za bolj ciljno klasifikacijo, ne pa za splošne novice

---

## 📌 Sklep

- **Najboljši rezultati**: RidgeClassifier (Poskusa 3 in 4)
- **Najslabši rezultati**: Eksperimentalni LSTWSVM (Poskus 2)
- **Najbolj stabilen pipeline**:
  - Preprocesiranje z lematizacijo ali stemming
  - TF-IDF s parametri (min_df=5, max_df=0.9, ngram_range=(1,2))
  - OneVsRestClassifier z RidgeClassifier
- **Opombe za prihodnje delo**:
  - Raziskati uporabo globokih modelov (BERT ipd.)
  - Uporaba več podatkov ali boljše uravnoteženje kategorij
  - Integracija dodatnih metapodatkov (datum, avtor, itd.)

