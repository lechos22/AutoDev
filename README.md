# PlacekAI

## Architektura funkcjonalna

- Pobieranie informacji z plików projektu obsługiwanego przez nasz system.
- Odpowiedź na pytania dotyczące technologii, architektury oraz działania kodu w projekcie
- Integracja z Github i Git poprzez wykorzystanie biblioteki gitpython oraz wbudowanego w langchain toolkitu do reposytoriów GitHub
- Tworzenie i implementowanie nowych funkcjonalności w projekcie

## Architektura techniczna

PlacekAI korzysta z grafowej bazy danych, co pozwala na:

- łatwą skalowalność projectu
- zmianę struktury przechowywanych danych, aby dostosować je do potrzeb modelu językowego
- proste utrzymywanie kodu dzięku zastosowaniu sprawdzonej grafowej bazy danych Neo4j

Nasz projekt jest wyraźnie podzielony na części, dzięki czemu jego utrzymywanie oraz rozwój nie będzie stanowiło problemu.

## Demo

Demo placekAI pozwala na:

- Pobieranie informacji z plików projektu obsługiwanego przez nasz system.
- Odpowiedź na pytania dotyczące technologii, architektury oraz działania kodu w projekcie
- Generowanie fragmentów kodu dotyczące nowych i obecnych funkcjonalności w repozytorium
