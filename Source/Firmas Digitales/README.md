# [DEPRECATED].
This guide is deprecated. Using bash is not recommended for creating certificates anymore, and the process is now simplified with python scripts.

# Step 0: Prior Setup
This guide assumes you have OpenSSL installed on your system. If not, please install it first. If you have Git, you can use Git Bash which already includes OpenSSL.

# 🔧 Step 1: Create a Root Certificate Authority (CA)
This will be your trust anchor. It will sign your server and client certificates. (./certs/root/)

## Generate the private key:
```bash
openssl genrsa -out rootCA.key 4096
```

## Create the root certificate config (rootCA.cnf):
```ini
[ req ]
default_bits        = 4096
prompt              = no
default_md          = sha256
distinguished_name  = dn
x509_extensions     = v3_ca

[ dn ]
C=MX
ST=Nuevo-Leon
L=Monterrey
O=RaulCA
CN=Raul Root CA

[ v3_ca ]
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always,issuer
basicConstraints = critical, CA:true
keyUsage = critical, digitalSignature, cRLSign, keyCertSign

```

## Generate the root certificate:
```bash
openssl req -x509 -new -nodes -key rootCA.key -days 3650 -out rootCA.pem -config rootCA.cnf
```

# 🔏 Step 2: Issue a certificate for signing documents
This certificate will be used to sign documents. This will be the certificate you use with pyhanko.sign (./certs/users/user/).

## Generate a key for the signer:
```bash
openssl genrsa -out signer.key 2048
```

## Create a certificate signing request (CSR)
```bash
openssl req -new -key signer.key -out signer.csr
```

## Create the signer cert extension config (signer_cert.cnf)
```ini
[ v3_user ]
basicConstraints = CA:FALSE
keyUsage = critical, digitalSignature, nonRepudiation
extendedKeyUsage = emailProtection
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid,issuer
```

## Sign the CSR with your root CA

```bash
openssl x509 -req -in signer.csr -CA rootCA.pem -CAkey rootCA.key -CAcreateserial \
-out signer.crt -days 825 -sha256 -extfile signer_cert.cnf -extensions v3_user
```

Now you have:
- ./certs/users/user/signer.key → private key for signing
- ./certs/users/user/signer.crt → certificate with digitalSignature and nonRepudiation
- ./certs/root/rootCA.pem → trusted root certificate