TDD Ansible - systemd daemons
===
g
Se sei qui, è perché stai usando Infrastructure-as-Code (IaC), giusto? Hai mai sentito parlare di Test-Driven
Development_ forse starai pensando: "TDD quella roba da sviluppatori maledetti". Ottimo! Il fatto è che quando fai IaC
tu stai realmente scrivendo del codice, quindi è molto importante scrivere anche i test e TDD è probabilmente il metodo
più efficace per scrivere codice di qualità con una buona copertura di test case! 

## Introduzione
[Ansible](http://docs.ansible.com/ansible/latest/index.html) è uno strumento di _agent-less_ orchestrazione IT scritto
in Python. Esso semplifica l'automazione e il deploy dell'infrastruttura IT, dei pacchetti software e la loro 
configurazione.

Le caratteristiche di _Ansible_ sembrano davvero interessanti, ma voglio fare un passo in avanti nel mio viaggio sulla
via _"DeOps"_ e applicare il concetto di _"Infrastructure as Code"_. Come posso fare? Di certo non basta prendere questi
file e metterli in un repository condiviso... devo trovare un modo per verificare quello che scrivo, magari usare un
linter, eseguire dei **"test veri"** della mia automazione e, infine, dato che sto scrivendo codice (usando un DSL),
perché non applicare **TDD** o BDD? Quali strumenti possono aiutarmi?

Il codice completo scritto durante questo tutorial e altri esempi di playbook Ansible scritti in TDD li potete trovare
nel seguente repsitory: [https://github.com/bombo82/tdd-ansible](https://github.com/bombo82/tdd-ansible)

## Obiettivo
Installare, abilitare ed eseguire un servizio che usa _**systemd**_ su macchine CentOS.

In questo tutorial userò il servizio **Apache2/HTTPD** e lo useremo per servire un file _HTML_ statico.

Non mi dilungo nel raccontarvi cosa sia **TDD** o su come scrivere dei buoni test... per questi argomenti vi rimando ai
seguenti link:
[Wikipedia-TDD](https://it.wikipedia.org/wiki/Test_driven_development),
[Agile Book - TDD](https://www.jamesshore.com/Agile-Book/test_driven_development.html),
[Kent Beck - Programmer Test Principles](https://medium.com/@kentbeck_7670/programmer-test-principles-d01c064d7934)

## Prima di iniziare
Vi consiglio di leggere e magari seguire il tutorial
[TDD Ansible - primi passi](primi-passi.md)
in cui trovate una descrizione dei pre-requisiti e degli strument strumenti utilizzati, oltre a una breve trattazione
relativa alla creazione dello scheletro del ruolo e dello scenario di test. 

## Iniziamo
Dato che useremo **TDD** è necessario configurare e impostare l'ambiente di test e solo in seguito possiamo procedere
scrivendo del codice, ma prima ancora dobbiamo creare lo scheletro del nostro ruolo e dello scenario di test.

### 1. Creazione dello scheletro
L'approccio migliore per farlo è quello di creare prima il ruolo Ansible usando il comando `ansible-galaxy init` e poi
aggiungiamo lo scenario di test mediante `molecule init`.
```bash
ansible-galaxy init systemd-daemons
cd systemd-daemons
molecule init scenario --scenario-name default --role-name systemd-daemons
```

### 2. Configurazione test framework e molecule
Innanzitutto, dobbiamo verificare ed eventualmente ridefinire il file di configurazione predefinito di Molecule. Esso
viene generato dal comando `molecule init` e contiene il driver, le piattaforme, i _verifier_ e la sequenza di test
(se non vogliamo utilizzare quella predefinita) per il nostro scenario.
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
Sopra trovate il file `<role_name>/molecule/molecule.yml` creato dal comando `molecule init` ed è praticamente perfetto. 

Se eseguissimo in questo momento i test con il comando `molecule test` avremmo un errore perchè il _linter_ dei ruoli
Ansible ci segnala che il file `<role_name>/meta/main.yml` contiene alcuni valori di default che andrebbero modificati e
l'indicazione delle _platforms_ è mancante. Potete correggere i metadata oppure eliminare il file... questo file è
indispensabile solo quando il ruolo viene pubblicato e condiviso su **Ansible Galaxy** o un altro repository per i ruoli.

Sistemato il file `<role_name>/meta/main.yml` tutti i test saranno verdi e possiamo procedere a scrivere il codice.

### 3. Assicurarsi che il pacchetto apache2 sia installato
Scriviamo il test che verifica la presenza del pacchetto **apache2**, quindi editiamo il file
`<role_name>/molecule/default/test_default.py`, rimuovendo il test case di default e inseriamo il seguente codice:
```python
def test_apache2_package(host):
    assert host.package('httpd').is_installed
```
Dopo aver lanciato il test con il comando `molecule test` e verificato che esso fallisce, possiamo procedere scrivendo
la parte di playbook Ansible che installa il pacchetto **apache**. Editate il file `<role_name>/task/main.yml` e
inserite il seguente codice:
```yaml

---
- name: ensure Apache2 is installed
  yum:
    name: httpd
    state: present
```

A questo punto il test sarà verde e abbiamo terminato la parte d'installazione del pacchetto.
Abbiamo scritto così poco codice che non è necessario fare refactor.

### 4. Lanciare il servizio e avviarlo in automatico
Scriviamo il test per verificare se il servizio è stato avviato ed è messo in avvio automatico. Potremmo scrivere un
solo test case che effettua 2 differenti `assert`, come nell'esempio sotto, oppure 2 differenti test case.
```python
def test_apache_is_running_and_enabled(host):
    service = host.service('httpd')

    assert service.is_running
    assert service.is_enabled
```
Ci aspettiamo che le `assert` presenti nel nostro test non siano verificate (non abbiamo ancora scritto l'automazione),
ma come potete vedere dai log sotto, è proprio il test che fallisce malamente con un errore :-(

Questo errore è dovuto al fatto che i servizi in CentOS, utilizzano **systemd** come _"System and Service Manager"_, ma
i container Docker ufficiali di tutte le distribuzioni non hanno al loro interno alcun _"System and Service Manager"_
configurato e funzionante. La spiegazione della scelta di non inserire un _"System and Service Manager"_ nei container
Docker esula dal presente tutorial, quindi prendetelo come un dato di fatto e passiamo direttamente a come risolvere
questo inconveniente!

#### Abilitare systemd all'interno di un container Docker
Se durante l'esecuzione dei test trovate il seguente errore `ValueError: cannot find "service" command` significa che
**testinfra** non è riuscito a trovare il gestore dei servizi. Sotto è riportato il log per intero: 
```bash
    host = <testinfra.host.Host object at 0x7fbd978184e0>
    
        def test_apache_is_running_and_enabled(host):
            service = host.service('httpd')
        
    >       assert service.is_running
    
    tests/test_default.py:17:
    _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
    ~/.local/lib64/python3.6/site-packages/testinfra/modules/service.py:110: in is_running
        return super(SystemdService, self).is_running
    ~/.local/lib64/python3.6/site-packages/testinfra/modules/service.py:92: in is_running
        self._service_command, self.name).rc == 0
    ~/.local/lib64/python3.6/site-packages/testinfra/utils/__init__.py:44: in __get__
        value = obj.__dict__[self.func.__name__] = self.func(obj)
    ~/.local/lib64/python3.6/site-packages/testinfra/modules/service.py:80: in _service_command
        return self.find_command('service')
    _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
    
    self = <testinfra.host.Host object at 0x7fbd978184e0>, command = 'service'
    extrapaths = ('/sbin', '/usr/sbin')
    
        def find_command(self, command, extrapaths=('/sbin', '/usr/sbin')):
            """Return path of given command
        
            raise ValueError if command cannot be found
            """
            out = self.run_expect([0, 1, 127], "command -v %s", command)
            if out.rc == 0:
                return out.stdout.rstrip('\r\n')
            for basedir in extrapaths:
                path = os.path.join(basedir, command)
                if self.exists(path):
                    return path
    >       raise ValueError('cannot find "%s" command' % (command,))
    E       ValueError: cannot find "service" command
    
    ~/.local/lib64/python3.6/site-packages/testinfra/host.py:46: ValueError
```
Se invece riscontrate il seguente errore mentre eseguite il playbook... come diceva una vecchia pubblicità: _DevOps fai
da te? No **TDD**? Ahiahiahihahihaihiiiiiiii_
```bash
Failed to get D-Bus connection: Operation not permitted
```
La causa è sempre quella... la mancanza di un _"System and Service Manager"_.
Possiamo risolvere questo inconveniente in svariati modi, ma i principali sono:
1. creare noi alcune immagini custom con **systemd** installato e funzionante
2. usare delle immagini custom create da un'altra persona che le ha rese disponibili tramite
[Docker Registry](https://hub.docker.com/_/registry)

Personalmente preferisco la seconda opzione e solitamente utilizzo le immagini preparare da
[Jeff Geerling](https://hub.docker.com/u/geerlingguy/), perché sono state create proprio per essere utilizzate con
**molecule**. Esse sono fatte in modo professionale, stabili, testate e aggiornate con un ritmo ragionevole.

Purtroppo per utilizzare **systemd** non basta cambiare immagine, ma è indispensabile che l'host sia una macchina
GNU/Linux con **systemd**! Non preoccupatevi... normalmente non c'è niente da fare anche se non utilizzate GNU/Linux
come host! Distinguiamo i vari casi per sistema operativo che usate per eseguere Docker:
- **macOS**: Docker installa di nascosto una VM che usa come host per i container, quindi siete a posto;
- **MS Windows 10** fa cose magiche e sfrutta il WSL, quindi dovrebbe andare tutto... basta avere fede in Bill Gates;
- **GNU/Linux** la maggior parte delle distribuzioni usa **systemd**, quindi quasi nessuno ha problemi.

Nel caso in cui la vostra distribuzione GNU/Linux non usi **systemd** oppure riscontrate problemi con macOS o MS Windows
potete creare una macchina virtuale ad-hoc da eseguire come host per i container Docker usati durante i test.
Nella cartella `vagrant` di questo repsitory
[https://github.com/bombo82/tdd-ansible](https://github.com/bombo82/tdd-ansible) trovate un possibile modo per creare
la vostra VM da usare come host.

#### Immagini già pronte che supportano systemd
Modifichiamo la sezione _platforms_ del file `<role_name>/molecule/default/molecule.yml` come segue:
```yaml
platforms:
  - name: centos7
    image: geerlingguy/docker-centos7-ansible:latest
    command: ""
    volumes:
      - /sys/fs/cgroup:/sys/fs/cgroup:ro
    privileged: true
    pre_build_image: true
```
Ora eseguendo il comando `molecule test` l'errore relativo a **systemd** dovrebbe essere sparito e dovreste trovare il
log della _assert_ fallita. Sotto trovare un esempio:
```bash
    host = <testinfra.host.Host object at 0x7f80d8ee3400>
    
        def test_apache_is_running_and_enabled(host):
            service = host.service('httpd')
        
    >       assert service.is_running
    E       assert False
    E        +  where False = <service httpd>.is_running
    
    tests/test_default.py:17: AssertionError
```

#### Infine scriviamo l'automazione
A questo punto non ci resta che assicurarci che **Apache2** sia avviato e messo in avvio automatico. Aggiungiamo il
seguente codice al task del playbook:
```yaml
- name: ensure apache is running and enabled
  service:
    name: httpd
    state: started
    enabled: true
```

### 5. Servire un file HTML statico
Questo punto dovrebbe andar via liscio senza alcun inconveniente. Ci bastano veramente poche righe per il test e per
l'implementazione! Come al solito partiamo dal test... al file statico diamo casualmente il nome `index.html` e il test
si limiterà a verificare che esso esiste all'interno del container Docker e che sia nella folder corretta.
```python
def test_index_html_exists(host):
    index_html = host.file("/var/www/html/index.html")

    assert index_html.exists
```
Creare il file statico `index.html` e automatizzare il suo deploy... ehm, copiarlo nella cartella radice del sito.
Procedendo con ordine, partiamo con creare un file `index.html` all'interno della folder `<role_name>/files` e, anche
se il contenuto del file non viene controllato dal test, scriviamo al suo interno del codice HTML valido, per esempio:
```html
<html>
    <head>
        <title>My Page</title>
    </head>
    <body>
        <h1>YEAAAAAH</h1>
        <p>This is just a simple html page</p>
    </body>
</html>
```
Ora aggiungiamo al task l'istruzione che copia il file, notate che in _src_ abbiamo messo solo il nome del file...
per convenzione di Ansible i file usati all'interno dei playbook si trovano nella folder `<role_name>/files` ed essa
viene considerata come _radice_ dei path quando usiamo questi file.
```yaml
- name: ensure index.html is present
  copy:
    src: index.html
    dest: "/var/www/html/index.html"
```
Eseguiamo `molecule test` e visto che tutto funziona e abbiamo finito!
