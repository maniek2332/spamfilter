.. include:: coverpage.rst

.. raw:: pdf

    PageBreak oneColumn

.. contents:: Spis treści
   :depth: 2

.. sectnum::
   :depth: 2

.. raw:: pdf

    PageBreak

.. footer::

   .. class:: center

    ###Page###


Wstęp
=====

.. note::

  Kilka słów wstępu, krótkie opisanie problemu spamu

Cel pracy
---------

Celem pracy jest stworzenie systemu antyspamowego. Zadaniem systemu
jest:

#. Poprawne wczytanie i przetworzenie dowolnej wiadomości e-mail.
#. Nauka klasyfikacji spamu na podstawie danych treningowych
#. Udostępnienie interfejsu pozwalającego zewnętrznym aplikacjom na
   sklasyfikowanie e-maili.

Przy klasyfikacji system skupiać się będzie przede wszystkim na treści
wiadomości. Informacje takie jak adres nadawcy lub adres serwera,
z którego wiadomość nadeszła nie będą brane pod uwagę.

Uczenie maszynowe
-----------------

Uczenie maszynowe jest dziedziną sztucznej inteligencji. Polega ono
na tworzeniu systemów, które na podstawie przykładów są w stanie uczyć
się, to znaczy zyskiwać wiedzę poprzez gromadzenie doświadczenia. [#]_

..
    Uczenie się systemu oznacza wprowadzenie zmian dotyczących działania
    systemu wraz z napływem nowych informacji. Zmiany te umożliwiają
    bardziej efektywne wykonywanie tych samych lub podobnych zadań
    w przyszłości. [#]_

.. [#] Bolc L., Zaremba P., Wprowadzenie do uczenia się maszyn,
   Akademicka Oficyna Wydawnicza, 1993

Uczenie maszynowe ma szerokie zastosowanie w różnych aspektach
życia, stosuje się je między innymi do:

* rozpoznawania mowy i pisma,
* automatycznego sterowania samochodami,
* klasyfikacji obiektów astronomicznych,
* wykonywania analiz rynkowych.

Biblioteka scikit-learn
-----------------------

Znana również pod nazwami *scikits.learn* i *sklearn*, jest
open-source'ową biblioteką przeznaczoną dla języka programowania
Python. Dostarcza wiele algorytmów uczenia maszynowego do klasyfikacji,
regresji i grupowania danych. Prócz tego biblioteka zawiera również
funkcje pomocnicze służące między innymi do:

 * normalizacji danych,
 * kroswalidacji systemów,
 * mierzenia efektywności systemów.

Dla algorytmów takich jak regresja logistyczna i
maszyna wsparcia wektorowego *scikit-learn*
wykorzystuje zewnętrzne biblioteki *LIBLINEAR* [#]_ i *LIBSVM* [#]_,
co zapewnia wysoką wydajność obliczeń.

.. [#] http://www.csie.ntu.edu.tw/~cjlin/liblinear/
.. [#] http://www.csie.ntu.edu.tw/~cjlin/libsvm/

Elementy projektu
-----------------

W filtrze antyspamowym będącym tematem tej pracy możemy wyszczególnić
następujące elementy:

Parser wiadomości e-mail
~~~~~~~~~~~~~~~~~~~~~~~~

Podstawową funkcją parsera jest poprawne wczytanie wiadomości
e-mail, w tym celu musi on:

#. Wczytać nagłówki wiadomości.
#. Wczytać ciało wiadomości.
#. Zdekodować ciało wiadomości na podstawie kodowania, i strony
   kodowej znalezionych w nagłówku.
#. Rozpoznać czy ciało wiadomości jest HTMLem i poprawnie go sparsować.

Na parsowanie HTMLa składa się:

#. Przetworzenie ciała do prostego tekstu (plaintext).
#. Podsumowanie liczby i typów tagów użytych w wiadomości.
#. Podliczenie liczby błędów drzewa w wiadomości.

Parser stworzony został w oparciu o moduł *HTMLParser* [#]_ z
biblioteki standardowej języka Python.

.. [#] http://docs.python.org/2/library/htmlparser.html

..
    Sam parser ma postać modułu języka Python. Pozwala to na łatwe
    połączenie go z pozostałymi elementami pracy inżynierskiej.
    Po wczytaniu wiadomości możemy pobrać wszystkie zebrane informacje
    z wewnętrznej obiektowej struktury modułu.

Ekstraktor cech
~~~~~~~~~~~~~~~

Po wczytaniu wiadomości należy przedstawić zawarte w niej informacje
w formie numerycznej. Ekstraktor zajmuje się takimi zadaniami jak:

#. Zliczenie wystąpień słów w temacie wiadomości.
#. Zliczenie wystąpień słów w ciele wiadomości.
#. Zliczenie wystąpień linków i adresów w ciele wiadomości.

Do zliczania słów wykorzystane zostały narzędzia [#]_ pochodzące
z biblioteki *scikit-learn*.

.. [#] http://scikit-learn.org/stable/modules/feature_extraction.html#text-feature-extraction

Klasyfikator
~~~~~~~~~~~~

Jest to moduł odpowiedzialny za utworzenie modelu klasyfikatora wiadomości.
Wykorzystuje on informacje uzyskane z ekstraktora cech.
Znajdują się tutaj funkcje odpowiedzialne za trening oraz
testowanie modelu, a także wykonujące pomiar wydajności poszczególnych
algorytmów.

Serwer HTTP
~~~~~~~~~~~

Zadaniem serwera jest:

#. Nasłuchiwanie żądań HTTP z wiadomościami nadsyłanych przez programy
   pocztowe.
#. Sprawdzenie w klasyfikatorze nadesłanej wiadomości.
#. Odesłanie odpowiedzi zgodnej z przewidywaniami klasyfikatora.

Wtyczka do programu pocztowego
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

W celu demonstracji możliwości integracji filtra antyspamowego
z klientami poczty,
stworzona została przykładowa wtyczka do programu *Claws Mail* [#]_.

.. [#] http://www.claws-mail.org/

Przetwarzanie wiadomości
========================

Korpus wiadomości
-----------------

W projekcie wykorzystana została baza wiadomości
wykorzystywana w projekcie *SpamAssasin* [#]_. Znajdujące się
w niej wiadomości pochodzą z różnych źródeł, są to między innymi
publiczne fora, newslettery stron internetowych oraz skrzynki pocztowe
osób zaangażowanych w tworzenie korpusu [#]_. Wśród znajdujących
się w tej bazie e-maili możemy wyróżnić następujące kategorie:

 * **Spam** - wiadomości spamowe, żadne z tych wiadomości nie pochodzą
   z pułapek na spam - to znaczy - zostały wysłane na adresy e-mailowe
   służące do normalnej korespondencji.
 * **Easy Ham** - wiadomości niespamowe, stosunkowe łatwe do odróżnienia
   od spamu, rzadziej wykorzystują HTML i nieczęsto zawierają
   typowo spamowe frazy.
 * **Hard Ham** - wiadomości niespamowe, trudniejsze do odróżnienia od
   spamu, często zawierają błędnie sformatowany HTML, wykorzystują
   frazy spotykane w spamie.

   Tabela 2.1 zawiera informacje na temat liczby wiadomości w
   poszczególnych kategoriach.


.. [#] http://spamassassin.apache.org/
.. [#] http://spamassassin.apache.org/publiccorpus/readme.html

.. admonition:: TODO

   * Szczegółowe informacje na temat kategorii w korpusie

============= =================
Kategoria     Liczba wiadomości
============= =================
Easy Ham      2551
Hard Ham      250
Spam          500
**Suma**      **3301**
============= =================

.. class:: caption

   **Tab. 2.1.** - Liczba wiadomości poszczególnych
   kategorii znajdujących się w korpusie

Budowa wiadomości e-mail
------------------------

Surowa wiadomość e-mail składa się z dwóch części: nagłówków i
ciała. Części te oddzielone są od siebie sekwencją znaków
``<CR><LF><CR><LF>`` (CR - Carriage Return, LF - Line Feed).

Część nagłówkowa składa z wielu nagłówków w formacie::

    Nazwa nagłówka: Wartość nagłówka

Jeden taki nagłówek może zajmować kilka linijek (każda kolejna
linijka musi się rozpoczynać białymi znakami - spacje lub
tabulacje). Wielkość znaków w nazwie nagłówka nie ma znaczenia.
Listing 2.1 zawiera przykładowy nagłówek

::

    Return-Path: <bduyisj36648@Email.cz>
    Delivered-To: yyyy@netnoteinc.com
    Received: from tugo (unknown [211.115.78.51]) by mail.netnoteinc.com
        (Postfix) with ESMTP id F40CA1140BA; Fri,  6 Jul 2001 02:03:10 +0000
        (Eire)
    Received: from 127.0.0.1 ([202.72.66.134]) by tugo with Microsoft
        SMTPSVC(5.0.2172.1); Fri, 6 Jul 2001 11:00:31 +0900
    Message-Id: <Mp9U4NEPd9mpa.8zI7m9NaCf4dlKT-HBhxaL@127.0.0.1>
    From: bduyisj36648@Email.cz <bduyisj36648@Email.cz>
    Subject: Finally   collecct   your   judgment (71733)
    Date: Wed, 16 Aug 2000 17:38:13 -0400 (EDT)
    MIME-Version: 1.0
    Content-Transfer-Encoding: 7bit
    X-Originalarrivaltime: 06 Jul 2001 02:00:32.0843 (UTC) FILETIME=[708F81B0:
        01C105BF]
    To: undisclosed-recipients:;

.. class:: caption

   **Lis. 2.1.** - Przykładowy nagłówek wiadomości e-mail

Ciało wiadomości to właściwa zawartość e-maila. Może być ono zapisane
zarówno w języku znaczników jakim jest HTML, jak również jako
zwykły tekst. Ponadto ciało zapisane jest w konkretnej stronie kodowej.
Może również być dodatkowo zakodowane kodowaniem ``quoted-printable``.

Ważne nagłówki
--------------

Content-Type
~~~~~~~~~~~~

Jedną z podstawowych informacji jaką zawiera ten nagłówek jest typ
ciała wiadomości. Najczęściej wykorzystywane są tu:

* ``text/plain`` - wiadomość zapisana prostym tekstem,
* ``text/html`` - wiadomość zapisana z użyciem HTML.

E-maile często jednak nie zawierają tych informacji lub celowo
opisują je w sposób mylący. Z tego powodu parser nie polega na tej
informacji i sam stara się wykryć czy wiadomość zawiera HTML,
czy też nie.

Spotyka się również maile wieloczęściowe, przykładowo kiedy w mailu
zamieszczone są obrazki lub inne załączniki, albo kiedy mail
posiada swoją wersję zarówno w HTMLu i prostym tekście.
Wówczas ciało wiadomości podzielone jest na części ciągiem znaków
zwanym ``boundary`` (granica). Wówczas każda z części posiada
swoje własne nagłówki i ciało.

Inną ważną informacją zawartą w tym nagłówku jest deklaracja strony
kodowej, w której zapisane zostało ciało. Na podstawie
tej informacji parser dekoduje tekst wiadomości na swój
wewnętrzny format.

Listing 2.2 zawiera przykłady użycia tego nagłówka.

::

    Content-Type: text/html;
    Content-Type: text/html;	charset=iso-8859-1
    Content-Type: text/html; charset="CHINESEBIG5"
    Content-Type: text/html; charset="ISO-8859-1"
    Content-Type: text/html; charset="US-ASCII"
    Content-Type: text/html; charset="Windows-1251"
    Content-Type: text/html; charset="euc-kr"
    Content-Type: text/html; charset="gb2312"
    Content-Type: text/html; charset="ks_c_5601-1987"
    Content-Type: text/html; charset="us-ascii"
    Content-Type: text/html;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;; (...)
    Content-Type: text/html;charset=ks_c_5601-1987
    Content-Type: text/plain;
    Content-Type: text/plain; Charset = "us-ascii"
    Content-Type: text/plain; charset="DEFAULT"
    Content-Type: text/plain; charset="DEFAULT_CHARSET"
    Content-Type: text/plain; charset="GB2312"
    Content-Type: multipart/alternative; boundary="----=_NextPart_000_81109_01C25FF9.832EE820"
    Content-Type: multipart/mixed; boundary="=_NextPart_Caramail_0190361032516937_ID"

.. class:: caption

   **Lis. 2.2.** - Przykłady wykorzystania nagłówka ``Content-Type``

Content-Transfer-Encoding
~~~~~~~~~~~~~~~~~~~~~~~~~

Nagłówek ten opisuje jak zakodowane są dane w ciele wiadomości.
W przypadku wiadomości e-mail spodziewamy się takich
kodowań:

* ``7bit`` - dane tekstowe zakodowane tylko na 7 bitach (ASCII).
* ``8bit`` - dane tekstowe zakodowane na 8 bitach (inne strony kodowe).
* ``quoted-printable`` - dane zakodowane kodowaniem ``quoted-printable``
* ``base64`` - dane zakodowane za pomocą ``base64``

Listing 2.3 zawiera przykłady wykorzystania tego nagłówka.

::

    Content-Transfer-Encoding: 7BIT
    Content-Transfer-Encoding: 8bit
    Content-Transfer-Encoding: QUOTED-PRINTABLE
    Content-Transfer-Encoding: base64

.. class:: caption

   **Lis. 2.3.** - Przykłady wykorzystania
   nagłówka ``Content-Transfer-Encoding``

Subject
~~~~~~~

W nagłówku tym zapisany jest temat wiadomości. Domyślnie nagłówek
ten zawiera tylko znaki ASCII. Jednak tutaj podobnie
jak w ciele wiadomości spotkać się możemy z różnymi stronami kodowymi i
kodowaniami. Jeśli nagłówek jest dodatkowo zakodowany przyjmuje
on postać:

::

    =?strona_kodowa?kodowanie?zakodowany_temat?=

* ``strona_kodowa`` to nazwa strony kodowej, w jakiej zapisany jest temat,
* ``kodowanie`` to litera ``Q`` lub ``B``, wskazuje to typ użytego kodowania,
  ``Q`` to ``quoted-printable``, ``B`` to ``base64``,
* ``zakodowany_temat`` to zakodowany temat wiadomości.

W celu odczytania takiego tematu najpierw dekodujemy ``zakodowany_temat``
używając właściwego kodowania, a na końcu odczytujemy go przy pomocy
podanej strony kodowej.

::

    Subject: Your eBay account is about to expire!
    Subject: re: domain registration savings
    Subject: Make a Fortune On eBay                         24772
    Subject: Save $30k even if you've refi'd           1090
    Subject: =?Big5?B?rEKq96SjrE5+fqdPtsykRn5+?=
    Subject: =?GB2312?B?NTDUqrvxtcPSu9LazuXHp83yRU1BSUy12Na3tcS7+rvh?=
    Subject: =?GB2312?B?0rvN+KGwu92hsczsz8KjrNK71bnM7M/C1qotLS0tMjAwM8TqNNTCMcjVLS00?=

.. class:: caption

   **Lis. 2.4.** - Przykłady wykorzystania nagłówka ``Subject``

W listingu 2.4 widzimy, że
w końcówkach niektórych tematów pojawiają się dodatkowe
nieznaczące znaki. Jest to technika używana przez spamerów mająca
na celu zmylenie prostych filtrów antyspamowych, które sprawdzają
czy dana wiadomość jest spamem bądź na podstawie prostego porównania
tematu wiadomości z zebraną wcześniej bazą spamu.


Dekodowanie ciała wiadomości
----------------------------

W wiadomościach e-mail spotykamy się z dwoma różnorodnymi kodowaniami
(nie liczymy tutaj kodowań podstawowych ``7bit`` i ``8bit``).
Jedno z nich to ``quoted-printable``. Jest to stosunkowo proste kodowanie,
które zapisuje bajty o wartości większej od 127, bajty będące kodami sterującymi
ASCII oraz znak ``=`` zapisując każdy z tych bajtów jako wartość
szesnastkową poprzedzoną znakiem ``=``. Ponieważ zakodowane są tylko
pojedyncze znaki kodowanie to jest proste do zdekodowania.

W listingu 2.5 zamieszczono fragment ciała wiadomości
zakodowanego z wykorzystaniem ``quoted-printable``.

::

    <html><body><center>

    <table bgcolor=3D"663399" border=3D"2" width=3D"999" cellspacing=3D"0" cel=
    lpadding=3D"0">
      <tr>
        <td colspan=3D"3" width=3D"999"> <hr><font color=3D"yellow"> 
    <center>
    <font size=3D"7"> 
    <br><center><b>Get 12 FREE VHS or DVDs! </b><br>
    <table bgcolor=3D"white" border=3D"2" width=3D"500">

.. class:: caption

   **Lis. 2.5.** - Fragment ciała wiadomości e-mail zakodowany przy
   użyciu ``quoted-printable``

Drugim spotykanym kodowaniem jest ``base64``. Jest to inny rodzaj kodowania,
koduje się za jego pomocą już nie pojedyncze znaki a cały blok danych.
W niektórych wiadomościach zdarza się spotkać z sytuacją kiedy tylko
początek ciała jest zakodowane jako ``base64``, natomiast reszta tekstu
zapisana jest prostym tekstem. Z tego powodu do wyznaczenia
części wiadomości, która jest zakodowana wykorzystane zostało
wyrażenie regularne, które dopasowywane jest do ciała::

    RE_BASE64 = re.compile('(?:(?:[a-zA-Z0-9+/=]+)[\n]?)+')

Tekst "Ala ma kota" zapisany w ``base64`` wygląda następująco::

    QWxhIG1hIGtvdGE=

Aby wiadomość mogła być prawidłowo wyświetlona musi zostać ona wczytana
przy pomocy odpowiedniej strony kodowej. Strona kodowa jakiej potrzebujemy
zadeklarowana jest w nagłówku ``Content-Type`` jako ``charset``.
Przy przetwarzaniu tekstu może się zdarzyć sytuacja, że bajt, który
przetwarzamy nie został przewidziany w stronie kodowej. W takim przypadku
bajt taki jest ignorowany.


Przetwarzanie HTML
------------------

Jeśli ciało wiadomości zostanie rozpoznane jako HTML zostaje podjęta
akcja parsowania go. Proste podejście do tego problemu (czyli zbudowanie
drzewa tagów) nie jest tutaj skuteczne. Powodem tego jest ogromna liczba
błędów występujących w mailach. Najczęściej spotykane to:

* brak domknięć części otwartych tagów,
* "zakleszczanie" tagów (np. ``<b><i>Tekst</b></i>``),
* brak elementu ``<html>`` w dokumencie.

Z tego powodu wykorzystany został parser, który wczytuje kolejne
otwarcia tagów, prosty tekst między nimi i zamknięcia tagów.
Na podstawie napotkanych otwarć i zamknięć tworzy on stos tagów,
ignoruje jednak przy tym wszelkie niewłaściwe domknięcia (zapisuje
jednak ich liczba). Zwykły tekst pomiędzy tagami zostaje zapisany do bufora
z prostym tekstem.

Prócz ekstrakcji tekstu z dokumentu HTML powyższy parser zbiera również
statystyki na temat pokrycia tekstu przez tagi (np. ile liter w dokumencie
było obłożone tagami pogrubienia), oraz zlicza liczba błędów napotkanych
przy przetwarzaniu struktury HTML.


Wiadomości wieloczęściowe
-------------------------

Jak już wcześniej wspomniano niektóre wiadomości mają formę wieloczęściową.
Takie e-maile rozpoznajemy po typie ``multipart/`` zawartym w nagłówku
``Content-Type``. Wówczas nagłówek ten zawiera również wartość ``boundary``,
która posłuży do podzielenia wiadomości. Przykładowo jeśli nasze ``boundary``
przyjmuje wartość ``QWERTY`` to separatory jakich szukamy w dokumencie
mają wartość ``--QWERTY``. Wyjątkiem jest tu ostatni separator,
jego wartość to ``--QWERTY--``. Wszystkie informacje zawarte przed
pierwszym i za ostatnim separatorem zostają zignorowane.

Następnie wszystkie znalezione w ten sposób części wiadomości zostają
ponownie sparsowane (traktowane są jako osobna wiadomość) a następnie
ponownie zebrane w całość (teksty zostają połączone, a statystyki
zsumowane).

Może się również zdarzyć sytuacja, że część wiadomości również
jest wiadomością wieloczęściową. Z tego powodu wykorzystane zostało
rozwiązanie rekurencyjne, które łatwo radzi sobie z takim
problemem.

Listing 2.6 zawiera przykładową wiadomość wieloczęściową.
Wartość ``boundary`` dla niej to ``BoundaryOfDocument``.

::

    This is a multi-part message in MIME format.

    --BoundaryOfDocument
    Content-Type: text/plain
    Content-Transfer-Encoding: 7bit

    FREE CD-ROM LESSONS
    http://isis.webstakes.com/play/Isis?ID=89801

    1. Choose from 15 titles
    2. Learn new skills in 1 hour
    3. Compare at $59.95
    4. Quick, easy and FREE!

    (...)

    --BoundaryOfDocument
    Content-Type: text/html
    Content-Transfer-Encoding: 7bit

    <META HTTP-EQUIV="Content-Type" CONTENT="text/html;charset=iso-8859-1">
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
    <HTML><HEAD><TITLE>Untitled Document</TITLE>
    <META content="text/html; charset=iso-8859-1" http-equiv=Content-Type>
    </HEAD>
    <BODY bgColor=#ffffff><CENTER>
    <TABLE align=center border=0 cellPadding=0 cellSpacing=0 width=500>

    (...)

    --BoundaryOfDocument--

.. class:: caption

   **Lis. 2.6.** - Przykładowa wiadomość wieloczęściowa.

Istotne cechy wiadomości
------------------------

.. note::

  Zaproponowanie cech wiadomości które mogą być wykorzystane w uczeniu
  maszynowym

Przygotowanie danych wejściowych dla klasyfikatorów
---------------------------------------------------

.. note::

  Określenie formatu w jakim dane zostaną przekazane klasyfikatorom,
  ewentualne ich wcześniejsze przetworzenie (np. normalizacja)


Algorytmy uczenia maszynowego
=============================

Kroswalidacja
-------------

W celu uzyskania miarodajnych wyników podczas testowania algorytmów
uczenia maszynowego wszystkie pomiary wydajności należy wykonywać
na innym zestawie danych niż te użyte do treningu. W tym celu, korpus
wiadomości został podzielony na zestaw treningowy i zestaw testowy
według poniższych reguł:

#. Cały korpus zostaje podzielony na :math:`k` równych części, przy
   czym w każdej z części proporcja wiadomości spamowych i niespamowych
   jest taka sama.
#. Walidacja zostaje wykonana :math:`k` razy.
#. W każdej walidacji :math:`k - 1` części zostaje wykorzystanych jako
   dane treningowe, a pozostała część jako dane testowe.
#. Wyniki powyższych walidacji zostają uśrednione.

Krzywa ROC
----------

Krzywa ROC (ang. *receiver operator characteristic*) jest techniką wizualizacji
wydajności klasyfikatora. Technika ta wykorzystywana jest głównie
w teorii detekcji sygnałów,
znalazła zastosowanie również w uczeniu maszynowym. Krzywa taka opisuje
trafność klasyfikacji w zależności od progu decyzyjnego. Tworzona jest
poprzez wyznaczanie liczby przykładów, które zostały poprawnie zakwalifikowane
jako należące do rozważanej klasy (TPR, ang. *true positive rate*) oraz
liczby przykładów, które zostały błędnie zakwalifikowane jako należące do klasy
(FPR, ang. *false positive rate*) dla różnych progów decyzyjnych.

W celu uzyskania skalarnej miary wydajności liczone jest pole pod krzywą,
miara taka nosi nazwę AUC (ang. *Area Under Curve*).


Regresja logistyczna
--------------------

Regresja logistyczna jest modelem liniowym klasyfikacji danych.
Dzięki wykorzystaniu funkcji logistycznej wartość przewidywana przez
ten model zawiera się w przedziale :math:`0 \leq p \leq 1`.

Rys. 3.1 przedstawia krzywe ROC dla regresji logistycznej z użyciem
różnych wartości parametru :math:`C`.

.. image:: charts/ROC_LogisticRegression.png
   :width: 70%
   :align: center

.. class:: caption

   **Rys. 3.1.** - Krzywa ROC dla regresji logistycznej

.. admonition:: TODO

   * Wpływ parametrów na efektywność klasyfikatora

Naiwny klasyfikator bayesowski
------------------------------

.. image:: charts/ROC_MultinomialNB.png
   :width: 70%
   :align: center

.. class:: caption

   **Rys. 3.2.** - Krzywa ROC dla naiwnego klasyfikatora
   bayesowskiego

Maszyna wsparcia wektorowego
----------------------------

.. image:: charts/ROC_SVC.png
   :width: 70%
   :align: center

.. class:: caption

   **Rys. 3.3.** - Krzywa ROC dla maszyny wsparcia wektorowego

Las drzew losowych
------------------

.. image:: charts/ROC_RandomForestClassifier.png
   :width: 70%
   :align: center

.. class:: caption

   **Rys. 3.4.** - Krzywa ROC dla lasu drzew losowych

.. note::

  Wykorzystane algorytmy mogą ulec zmianie


Porównanie efektywności klasyfikatorów
======================================

.. note::

  Obliczenie efektywności algorytmów, z uwzględnieniem użytych parametrów,
  wykresy, wykresy, wykresy...

Przykład:

.. image:: charts/ROC_ALL.png
   :width: 70%
   :align: center

.. class:: caption

   **Rys. 4.1.** - Zbiór krzywych ROC poszczególnych algorytmów


Integracja z programem pocztowym
================================

Protokół komunikacji
--------------------

Założeniem projektu jest umożliwienie dowolnemu klientowi poczty
na korzystanie z filtra antyspamowego. W tym celu zastosowano
komunikację bazującą na protokole sieciowym, a dokładniej
protokole HTTP. Klient chcąc sprawdzić czy dana wiadomość jest
spamem, wysyła ją do serwera HTTP filtra antyspamowego, a w odpowiedzi
otrzymuje wartość logiczną (prawda lub fałsz) mówiącą, czy wiadomość
została uznana za spam.

Serwer działa na porcie ``2220``. Oczekuje na wiadomości w formie
surowej, wysłane z użyciem metody ``PUT`` [#]_ protokołu HTTP.
Po otrzymaniu takiej wiadomości serwer podejmuje następujące
działania:

#. Parsuje surową wiadomość korzystając z opisanego wcześniej
   parsera wiadomości.
#. Przekazuje sparsowaną wiadomość do ekstraktora cech.
#. Dane otrzymane z ekstraktora cech zostają przekazane do
   wytrenowanego wcześniej algorytmu uczenia maszynowego.
#. Jeśli algorytm uzna wiadomość za spam, serwer zwróci
   pustą odpowiedź z kodem HTTP ``221``, w przeciwnym wypadku
   zwróci pustą odpowiedź z kodem ``220``.

.. [#] http://www.w3.org/Protocols/rfc2616/rfc2616-sec9.html
   Sekcja 9.6.

Wtyczka do klienta poczty
-------------------------

*Claws Mail* jest prostym klientem poczty elektronicznej przeznaczonym
zarówno na systemy operacyjne z rodziny Windows jaki i Unix.

Został on wykorzystany w tej pracy, ze względu na możliwość wykonywania
przez niego skryptów języka Python. Skrypt taki w trakcie wykonania
uzyskuje dostęp do okna programu i znajdujących się w nim
wiadomości i folderów. Z użyciem tego mechanizmu wykonana została integracja
klienta poczty z filtrem antyspamowym (a dokładniej jego serwerem HTTP).
Po uruchomieniu skrypt wykonuje następujące kroki:

#. W API klienta uzyskuje dostęp do aktualnie wybranego folderu i znajduje
   w nim wszystkie nieprzeczytane wiadomości.
#. Dla każdej nieprzeczytanej wiadomości odczytany zostaje plik zawierający
   e-mail w postaci surowej.
#. Każda surowa wiadomość zostaje wysłana osobno, za pomocą protokołu HTTP,
   metodą ``PUT``, na adres ``127.0.0.1``, port ``2220``.
#. Skrypt oczekuje na odpowiedź od serwera, jeśli w odpowiedzi otrzyma
   kod HTTP ``221`` wiadomość zostaje uznana za spam i przeniesiona do
   folderu "Kosz".
#. Po sprawdzeniu wszystkich wiadomości wyświetlone zostaje podsumowanie o
   liczbie wiadomości, które zostały rozpoznane jako spam.

Uruchomienie i efekt działania skryptu widoczne są na Rys. 5.1 i Rys. 5.2.

.. image:: images/plugin1_c.png
   :width: 85%
   :align: center

.. class:: caption

   **Rys. 5.1.** - Wywołanie skryptu sprawdzającego wiadomości e-mail

.. image:: images/plugin2_c.png
   :width: 85%
   :align: center

.. class:: caption

   **Rys. 5.2.** - Efekt działania skryptu sprawdzającego wiadomości e-mail


.. note::

  Opis mechanizmów programu pocztowego (prawdopodobnie Claws Mail), które
  umożliwiają stworzenie pluginu, pokazanie jak program został zintegrowany z
  filtrem.


Podsumowanie i wnioski
======================

.. note::

  Który algorytm okazał się najlepszy, dlaczego tak a nie inaczej, co można
  poprawić/ulepszyć/przemyśleć

Bibliografia
============

.. Ogólne notatki

   * pokazać przykładowe dane wyciągnięte przez parser wiadomości
