isiman
======

Centralized dashboard to manage multiple EMC Isilon clusters

### Changelog

- v0.1: Allow aggregate and view multiple clusters in a single screen

### Pre-requisites

To make the isiman system up and running, we need create an isilon role authentication to isiman user, besides that, we need to generate an ssh key on host origin where isiman will run to make the SSH connection and execute specific commands.

Bellow the procedure to configure the isiman host and Isilon cluster:

#### Isilon authentication

- Create a role authentication on Isilon cluster

```
isi auth roles create IsiMan
```

- Create a group on Isilon cluster

```
isi auth groups create IsiMan
```

- Add privileges to isiman user run necessary commands

```
isi auth roles modify IsiMan --add-priv ISI_PRIV_LOGIN_SSH
isi auth roles modify IsiMan --add-priv ISI_PRIV_EVENT
isi auth roles modify IsiMan --add-priv ISI_PRIV_STATISTICS
isi auth roles modify IsiMan --add-priv ISI_PRIV_JOB_ENGINE
```

- Add IsiMan role to group IsiMan

```
isi auth roles modify IsiMan --add-group IsiMan
```

- Create isiman user and add to Isiman group

```
isi auth users create isiman --enabled true --password-expires no --primary-group IsiMan
```

#### Generate ssh-key

 To make a connection with the clusters we need generate a ssh key without passphrase following the procedure below:

```
root@host:~# ssh-keygen
Generating public/private rsa key pair.
Enter file in which to save the key (/root/.ssh/id_rsa): [ Press <Enter> ]
Enter passphrase (empty for no passphrase): [ Press <Enter> ]
Enter same passphrase again: [ Press <Enter> ]
Your identification has been saved in /root/.ssh/id_rsa.
Your public key has been saved in /root/.ssh/id_rsa.pub.
The key fingerprint is:
8a:4d:23:85:62:2f:5f:fc:ed:b8:b8:e4:37:c0:b4:58 root@debian-template
The key's randomart image is:
+--[ RSA 2048]----+
|                 |
|     .           |
|  o . .          |
| . o oE          |
|  . o==.S        |
|   o.*++ .       |
|    o +.. .      |
|     o .oo       |
|      +ooo.      |
+-----------------+
```

#### Add public ssh key to isiman's authorized_keys2 on Isilon

- Create ssh directory
```
mkdir /ifs/home/isiman/.ssh
chmod 700 /ifs/home/isiman/.ssh
```

- Create authorized_keys2 and add public ssh key
```
vi /ifs/home/isiman/.ssh/authorized_keys2
chmod 600 /ifs/home/isiman/.ssh/authorized_keys2
```

- Change the owner of isiman user directory
```
chown -R isiman: /ifs/home/isiman/
```
