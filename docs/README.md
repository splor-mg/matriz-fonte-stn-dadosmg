# Documentação Técnica

## Pré-requisitos

Para criar um ambiente chamado `venv`, ativar o mesmo e instalar as dependências execute:

```
python -m venv venv
. venv/Scripts/activate
python -m pip install -r requirements.txt
```

O dpckan necessita da versão v4 do frictionless-py para funcionar corretamente (vide [dpckan#202](https://github.com/transparencia-mg/dpckan/issues/202)).

## Uso

A publicação inicial do conjunto de dados deve ser realizada manualmente. Primeiro crie o arquivo `.env` com as variáveis de ambiente:

```
CKAN_HOST=https://homologa.cge.mg.gov.br
CKAN_KEY=ayJ5eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJsaDBsV29TVEN6Q01LeFVuWW90TW5oeVJMc2QtcTdXMk40MDVBUzY4MkpmUW82SHo5cVdYRks0ck1FSUxxM05FTUNvV0NESk05dzRYS3lQMCIsImlhdCI6MTY4MDAyMzQ2Pn0.WFgWR5i5bheI-p_aVnXrVwrkaRZjp5tw9Ua1COe3_JE
```

Os valores adequados devem ser obtidos na sua página de usuário do CKAN (eg. https://homologa.cge.mg.gov.br/user/fjunior).

Para efetivamente criar o conjunto execute

```bash
dpckan --datapackage datapackage.yaml dataset create
```

Para atualizar o conjunto execute

```bash
make all
```
