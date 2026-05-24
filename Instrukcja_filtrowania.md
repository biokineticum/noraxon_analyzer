# Instrukcja i Dobre Praktyki Filtrowania Sygnałów Biomechanicznych

Niniejszy dokument zawiera wskazówki dotyczące stosowania filtrów cyfrowych (takich jak filtr Butterwortha) na danych z platform tensometrycznych, czujników inercyjnych (akcelerometrów) oraz EMG.

## Standardy i Rekomendacje (np. Noraxon)

Wybór odpowiednich parametrów filtru zależy od specyfiki badanego ruchu oraz użytego sprzętu. Przykładowo, zgodnie ze standardami zalecanymi przez firmę **Noraxon** dla sygnałów biomechanicznych często stosuje się:

- **Filtr górnoprzepustowy (High-pass): 1 Hz**  
  Pomaga wyeliminować tzw. *baseline drift* (pływanie linii izoelektrycznej), wolne artefakty ruchowe oraz wpływ grawitacji lub zmian temperatury na czujniki.
  
- **Filtr dolnoprzepustowy (Low-pass): 250 Hz**  
  Usuwa szum o wysokiej częstotliwości (np. zakłócenia z sieci elektrycznej 50/60 Hz, jeśli używamy też odpowiedniego filtru pasmowo-zaporowego, lub szum elektroniczny urządzeń), zachowując przy tym użyteczne pasmo sygnału.

- **Typ filtru:** Najczęściej rekomendowany jest **filtr Butterwortha** (zazwyczaj 2. lub 4. rzędu). Zaletą filtru Butterwortha jest płaska charakterystyka w paśmie przepustowym, co minimalizuje zniekształcenia amplitudy.

> [!TIP]
> W programie PhysioSim zaimplementowane są filtry z zerowym przesunięciem fazowym (tzw. `filtfilt` w Pythonie), co oznacza, że po przefiltrowaniu sygnału nie następuje jego przesunięcie w czasie. Dzięki temu piki (np. moment maksymalnego uderzenia) na wykresie przefiltrowanym idealnie pokrywają się w czasie z wykresem surowym.

## Złota Zasada: Zawsze weryfikuj wyniki!

Samo wpisanie "standardowych" wartości do filtru nie gwarantuje sukcesu. Analiza sygnałów biologicznych i mechanicznych bywa nieprzewidywalna.

> [!WARNING]
> **Zawsze porównuj wzrokowo sygnał przefiltrowany z sygnałem surowym!** Należy bezwzględnie weryfikować, czy otrzymane po filtracji wyniki są **realne i mają fizyczny sens**.

### Na co zwracać szczególną uwagę?

1. **Ucinanie pików (Over-smoothing):** Jeśli ustawisz zbyt niską częstotliwość odcięcia filtru dolnoprzepustowego (np. 10 Hz dla bardzo dynamicznego uderzenia), filtr "zetnie" rzeczywiste maksima siły lub przyspieszenia. W efekcie program wskaże znacznie mniejszą siłę uderzenia niż w rzeczywistości.
2. **Dodatkowe oscylacje (Ringing):** Zbyt strome filtry (bardzo wysoki rząd filtru) mogą powodować sztuczne "falowanie" sygnału w miejscach nagłych skoków (np. w momencie zderzenia z tarczą).
3. **Pływanie sygnału po filtracji górnoprzepustowej:** Upewnij się, że po usunięciu niskich częstotliwości sygnał w fazie spoczynku faktycznie oscyluje wokół zera, a sama filtracja nie zniekształciła użytecznej, wolniejszej fazy ruchu (np. przygotowania do ciosu).

## Jak dobrać filtry w praktyce?

1. Zostaw sygnał surowy jako punkt odniesienia na jednym z wykresów.
2. Zastosuj wyżej wymienione ustawienia wyjściowe (Low-pass 250 Hz, High-pass 1 Hz).
3. Przybliż (zoom) moment uderzenia/akcji.
4. Oceń, czy szum został stłumiony w stopniu pozwalającym na łatwą analizę, i jednocześnie czy maksymalna amplituda (pik) nie została zredukowana w nienaturalny sposób.
5. Dopasuj parametry, jeśli wyniki wydają się zniekształcone. Dla bardzo dynamicznych uderzeń konieczne może być podniesienie progu filtru dolnoprzepustowego.
