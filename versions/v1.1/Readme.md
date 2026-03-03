# v1.1

Classly hat jetzt eine eigene Flutter-Mobile-Codebasis unter `mobile/`, visuell an `plane-mobile` angelehnt, technisch aber vollstaendig aus Classly-Vertraegen abgeleitet.

Enthalten:

- neue Flutter-App-Shell mit Riverpod, GoRouter, Dio, Freezed/JSON und Secure Storage
- Instanz-Auswahl, Login-Shell, OAuth-Callback-Flow und Session-Bootstrap
- Domain- und DTO-Mapping fuer Events und Faecher aus `/api/events` und `/api/subjects`
- read-only Sync mit Cache-zuerst-Verhalten und Delta-Refresh
- MVP-Screens fuer Kalender, Events, Faecher, Settings und Diagnostics
- Such- und Filterlogik fuer Eventlisten

Bekannte Einschraenkungen:

- produktiver OAuth-Login braucht backendseitig einen registrierten Mobile-Client
- der lokale Event-/Subject-Cache ist aktuell als austauschbare Store-Abstraktion implementiert und sollte fuer vollstaendiges Offline-Verhalten noch auf persistente Speicherung gehaertet werden
