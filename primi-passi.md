TDD Ansible - Primi Passi
===

Se sei qui stai usando Infrastructure-as-Code (IaC), giusto? Hai mai sentito parlare di Test-Driven Development...
forse starai pensando: "TDD quella roba da sviluppatori maledetti". Ottimo! Il fatto è che quando fai IaC tu stai
realmente scrivendo del codice, quindi è molto importante scrivere anche i test e TDD è probabilmente il metodo più
efficace per scrivere codice di qualità con un buona copertura di test case! 

## Introduzione
[Ansible](http://docs.ansible.com/ansible/latest/index.html) è uno strumento di orchestrazione IT _agent-less_ scritto
in Python che semplifica l'automazione e la distribuzione dell'infrastruttura e dei pacchetti software e la loro
configurazione.

Le caratteristiche di _Ansible_ sembrano davvero interessanti, ma voglio fare un passo in avanti nel mio viaggio sulla
via _"DeOps"_ e applicare il concetto di _"Infrastructure as Code"_. Come posso fare? Di certo non basta prendere questi
file e metterli in un repository condiviso... devo trovare un modo per verificare quello che scrivo, magari usare un
linter, eseguire dei **"test veri"** della mia automazione e, infine, dato che sto scrivendo codice (usando un DSL),
perché non applicare **TDD** o BDD? Quali strumenti possono aiutarmi?

Il codice completo scritto durante questo tutorial e altri esempi di playbook Ansible scritti in TDD li potete trovare
nel seguente repsitory: [https://github.com/bombo82/tdd-ansible](https://github.com/bombo82/tdd-ansible)

## Obiettivo
Installare un pacchetto di _SOS Report_ su macchine Ubuntu e CentOS.

SOS Report SOS è uno strumento per acquisire le informazioni di debug per il sistema corrente in formato tarball
compresso che può essere utilizzato da noi per analizzare un problema oppure inviato al supporto tecnico per ulteriori
analisi.

Non mi dilungo nel raccontarvi cos'è **TDD** o su come scrivere dei buoni test... per questi argomenti vi rimando ai
seguenti link:
[Wikipedia-TDD](https://it.wikipedia.org/wiki/Test_driven_development),
[Agile Book - TDD](https://www.jamesshore.com/Agile-Book/test_driven_development.html),
[Kent Beck - Programmer Test Principles](https://medium.com/@kentbeck_7670/programmer-test-principles-d01c064d7934)

## Pre-requisiti
I pre-requisiti sono veramente minimi, ci basta un computer con installato Docker e Python, senza alcuna esigenza
particolare per il sistema operativo (ovviamente una versione attuale di esso è consigliata).

## Strumenti
In questo breve tutorial verranno utilizzati i seguenti strumenti:
- [Molecule](https://molecule.readthedocs.io/en/latest/)
- [Testinfra](https://testinfra.readthedocs.io/en/latest/)
- [PyTest](https://pytest.org/en/latest/)
- [Docker](https://docs.docker.com/)

[Molecule](https://molecule.readthedocs.io/en/latest/) contiene una serie di strumenti che ci aiutano a sviluppare e
testare ruoli Ansible. I ruoli Ansible possono essere testati su più sistemi operativi e distribuzioni, provider di
virtualizzazione come [Docker](https://docs.docker.com/) e vagrant, framework di test come
[testinfra](https://testinfra.readthedocs.io/en/latest/) e Goss possono essere utilizzati tramite Molecule. 

[Testinfra](https://testinfra.readthedocs.io/en/latest/) permette di scrivere unit test in Python per testare lo stato
attuale dei tuoi server configurati da strumenti di gestione come Ansible, Salt, Puppet, Chef e così via.

Per prima cosa procediamo con l'installazione degli strumenti che useremo in questo tutorial. Il comando sotto riportato
usa il _package manager_ di Python per installare tutto quello che ci serve e le relative dipendenze. L'istruzione
installa delle versioni dei software che corrispondono all'ultima stabile al momento della scrittura di questo tutorial,
quindi siete liberi di utilizzare tale versioni, oppure rimuoverle e utilizzare l'ultima versione disponibile.
```bash
pip install --user ansible==2.8.4 testinfra==3.1.0 molecule==2.22
```

## Creare lo scheletro del ruolo Ansible e lo scenario di test
Possiamo utilizzare due differenti approcci per creare il ruolo (escludendo a priori l'idea di crearlo manualmente).

### Approccio 1: ansible-galaxy init command
In questo approccio creiamo prima il ruolo Ansible usando il comando `ansible-galaxy init` e poi aggiungiamo lo scenario
di test mediante `molecule init`.
```bash
ansible-galaxy init sos-report-galaxy
cd sos-report-galaxy
molecule init scenario --scenario-name default --role-name sos-report-galaxy
```

### Approccio 2: molecule init command
Con questo apporoccio useremo un solo comando che creerà automaticamente sia il ruolo Ansible che lo scenario di test.
```bash
molecule init role --role-name sos-report-molecule
```

### Approccio 1 vs. Approccio 2
Una cosa che ho imparato e ci è voluto tanto sudore è che nell'informatica se usi 2 procedure differenti per raggiungere
lo stesso scopo non otterrai mai lo stesso risultato, ma 2 risultati differenti seppur equivalenti.

Nel primo approccio, usando due comandi differenti (tre con il _cd_) crea uno scheletro più completo e che rispetta
tutte le **best-practices** di Ansible, mentre con il secondo approccio usiamo un solo comando per fare tutto.

Io sono uno sviluppatore veramente pigro e normalmente uso il secondo approccio e poi mi lamento della mancanza di
alcune cartelle o alcuni file che sarebbero stati presenti se avessi usato il primo approccio :-(

## Iniziamo
Dato che useremo **TDD** è necessario configurare e impostare l'ambiente di test e solo in seguito possiamo procedere
scrivendo del codice.

###  1. Configurazione test framework e molecule
Innanzitutto, dobbiamo verificare ed eventualmente ridefinire il file di configurazione predefinito di Molecule, che
viene generato dal comando `molecule init` e che contiene il driver, la piattaforme, i _verifier_ e la sequenza di test
(se non vogliamo utilizzare quella predefinita) per il nostro scenario.

file: `<role_name>/molecule/molecule.yml`
```yaml

---
dependency:
  name: galaxy
driver:
  name: docker
lint:
  name: yamllint
platforms:
  - name: instance
    image: centos:7
provisioner:
  name: ansible
  lint:
    name: ansible-lint
verifier:
  name: testinfra
  lint:
    name: flake8
```
Sopra trovate il filecreate di default dal comando `molecule init` ed è quasi perfetto per il nostro scopo...
noi vorremmo creare il playbook compatibile sia per CentOS sia per Ubuntu, ma applicando lo spirito **TDD** direi che
possiamo iniziare con CentOS, lasciando inalterato i file, e aggiungere Ubuntu in un secondo momento. 

### 2. Prima esecuzione dei test
Ora molecule è configurato e il comando `molecule init` ha creato un test per noi... il test è molto semplice ed esso
verrà eseguito tramite _PyTest_ e grazie a _TestInfra_ verifica l'esistenza del file `/etc/hosts` (file che in ogni
distribuzione linux è sempre presente).

I test sono eseguiti tramite il comando `molecule test` che prima di eseguire i test veri e propri, si preoccupa di
scaricare le immagini Docker necessarie, eseguire alcuni linter per verificare la correttezza sintattica e formale del
codice e in generale _molecule_ eseguirà altri controlli sul nostro playbook Ansible.

Eccoci al momento della verità e come dice una vecchia canzone... **La verità mi fa male, lo sai!**
A differenza da quello che uno si aspetta l'esecuzione del test fallisce, o meglio a fallire è il _linter_ del playbook
Ansible. L'errore è abbastanza banale e ci segnala che il file `<role_name>/meta/main.yml` contiene alcuni valori di
default che andrebbero modificati e l'indicazione delle _platforms_ è mancante. Potete correggere i metadata oppure
eliminare il file... questo file è indispensabile quando il ruolo viene pubblicato e condiviso su **Ansible Galaxy**
o un altro repository.

### 3. Assicurarsi che il pacchetto sos-report sia installato
Scriviamo il test che verifica la presenza del pacchetto **sosreport**, quindi editiamo il file
`<role_name>/molecule/default/test_default.py`, rimuovendo il test case di default e inseriamo il seguente codice:
```python
def test_sos_report_package(host):
    assert host.package('sosreport').is_installed
```
Dopo aver lanciato il test con il comando `molecule test` e verificato che esso fallisce, possiamo procedere scrivendo
la parte di playbook Ansible con installa il pacchetto **sosreport**. Editate il file `<role_name>/task/main.yml` e
inserite il seguente codice:
```yaml

---
- name: install sosreport
  yum:
    name: sosreport
    state: present
```

A questo punto il test sarà verde e abbiamo terminato la parte d'installazione del pacchetto.
Abbiamo scritto così poco codice che non è necessario fare refactor, anzi provare a fare del refactoring ora significa
fare speculazioni e azzardi su come potrebbe evolversi il nostro playbook, quindi quello che abbiamo scritto è perfetto.

### 4. Aggiungiamo il supporto a Ubuntu
In generale, aggiugnere il supporto per una distribuzione significa fare 3 cose:
1. aggiungere la distribuzione desiderata nella sezione _platforms_ del file `<role_name>/meta/main.yml`
2. aggiugnere la distribuzione da testare nella sezione _platforms_ del file `<role_name>/molecule/default/molecule.yml`
3. modificare l'implementazione, ed eventualmente i test, per quanto riguarda le parti specifiche per la distribuzione

Procediamo con ordine e modifichiamo la sezione _platforms_ del file `<role_name>/meta/main.yml` ed eseguimo nuovamente
i test.
```yaml
  platforms:
    - name: centos
      versions: 7
    - name: ubuntu
      versions: 18.04
```
Perfetto, i test passano con successo! quindi possiamo procedere modificando il file _molecule.yml_ in modo da testare
il playbook sia con CentOS sia con Ubuntu.
Modifichiamo come segue la sezione _platforms_ del file `<role_name>/molecule/default/molecule.yml` ed eseguiamo
nuovamente i test.
```yaml
platforms:
  - name: centos7
    image: centos:7
  - name: ubuntu1804
    image: ubuntu:18.04
```
Questa volta il comando `molecule test` fallirà! Il motivo è molto semplice... la parte di automazione che installa il
pacchetto **sosreport** dipende dalla distribuzione target, per il semplice motivo che il pacchetto ha il nome diverso
in CentOS e in Ubuntu :-(

A questo punto dobbiamo modificare l'implementazione, prima dei test e poi dell'automazione al fine di gestire la
differenza tra i nomi. La soluzione che normalmente adotto nei test è creare una mappa `distribuzione -> nome_pacchetto`
contenente i valori di nostro interesse.
```python
def _get_sosreport_package_name(distribution):
    return {
        "ubuntu": "sosreport",
        "centos": "sos"
    }.get(distribution)


def test_sos_report_is_installed(host):
    package_name = _get_sosreport_package_name(host.system_info.distribution)
    package = host.package(package_name)

    assert package.is_installed
```
Per la parte di Ansible invece ci sono più soluzioni possibili strade. La più semplice prevede di duplicare il blocco di
codice per l'installazione del pacchetto ed eseguire in modo condizionale il blocco per CentOS o per Ubuntu.
```yaml

---
- name: ensure sosreport is installed (RedHat-based)
  yum:
    name: sos
    state: present
  when: ansible_os_family == 'RedHat'

- name: ensure sosreport is installed (Debian-based)
  apt:
    name: sosreport
    state: present
  when: ansible_os_family == 'Debian'
```

### 5. Code Refactor
Il codice scritto durante questo tutorial è abbastanza semplice e soprattutto sono poche righe. All'interno del playbook
abbiamo 2 blocchi differenti di codice molto simile tra loro e che verranno eseguiti in modo condizionale in base alla
distribuzione target. Un possibile refactor è quello di rimuovere i blocchi condizionali in favore di spezzare il
playbook in più file da includere in base alla distribuzione. Visto la semplicità e brevità del playbook non effettuto
questo refactor, ma potete vedere un esempio nel playbook **lamp-live** che trovate sempre in questo repository.

[https://github.com/bombo82/tdd-ansible](https://github.com/bombo82/tdd-ansible)  
