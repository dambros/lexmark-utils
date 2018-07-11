## Lexmark-Utils
Repositório contendo scripts auxiliares para POC usando MFP Lexmark e EasySearch para ABIN.

### Requisitos

* Python 3.6+
* [ImageMagick](https://www.imagemagick.org/script/convert.php)


### Instalação

```
cd lexmark-utils
pipenv install
```


### Como Usar

#### file_merger.py

O script pode ser executado da seguinte forma:

```
 file_merger.py merge MFP_FOLDER_PATH OCR_FOLDER_PATH -c CONVERT_PATH
```

Para informações adicionais:
```
file_merger.py --help
```
ou
```
file_merger.py merge --help
```

#### index_verifier.py

É necessário especificar as configurações pertinentes no arquivo ```config.py```. Após configuração, o script pode ser executado da seguinte forma:

```
 index_verifier.py check
```

Para informações adicionais:
```
index_verifier.py --help
```
ou
```
index_verifier.py check --help
```