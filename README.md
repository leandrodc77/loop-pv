# chen-pv-loop (método de Chen) — extrair dados e calcular métricas do loop Pressão–Volume

Este repositório transforma a tabela do arquivo **“Loop PV - metodo de chen.xlsm”** (aba `Planilha2`) em:
- um **pipeline de extração** (ler valores da planilha e exportar JSON/CSV);
- um **motor de cálculo em Python** que replica as fórmulas do template;
- geração opcional de **pontos do loop PV** e **gráfico**.

> Aviso rápido (para evitar dor de cabeça): isto é **código de apoio** (pesquisa/ensino/auditoria).  
> **Não use como decisão clínica isolada** sem validação local e checagem de unidade/entrada.

## O que a planilha contém (aba `Planilha2`)

### Entradas (inputs)
- `PAS` (mmHg)
- `PAD` (mmHg)
- `VDF` (mL)
- `VSF` (mL)
- `PET` (ms)  *(na planilha: “PET (CIV)”)*
- `ET` (ms)
- `Ees` (mmHg/mL)
- `V0` (mL)

### Saídas calculadas (outputs)
- `PAt` = 0,9 × PAS  (mmHg)
- `VS` = VDF − VSF (mL)
- `FE` = (VDF − VSF) / VDF × 100  (%)
- `tNd` = PET / ET (adimensional)
- `Endavg` (polinômio de 7º grau em tNd)
- `Endest` (função de FE, PAD/PAt e Endavg)
- `Ea` = PAt / VS (mmHg/mL)
- `VAC` = Ea / Ees (adimensional)
- `Ptop` = Ees × (VSF − V0) (mmHg)  *(na planilha: “Ptop ou PAS”)*


### Extra: Ees e VAC pela fórmula single-beat (Chen)
Mesmo que o template traga `Ees` como campo preenchível, o pacote também calcula, quando possível:
- `Ees_chen` = (PAD − (Endest × 0,9×PAS)) / (Endest × VS)
- `VAC_chen` = Ea / Ees_chen
- `Ptop_chen` = Ees_chen × (VSF − V0)

Se você fornecer `Ees` (medido/assumido), o código mantém `VAC` (igual ao Excel) e ainda fornece `VAC_chen` para comparação.

Além disso, o pacote gera os pontos para plotar:
- **ESPVR**: (V0, 0) → (VSF, Ptop)
- **Loop PV**: (VDF,0) → (VDF,Ptop) → (VSF,Ptop) → (VSF,0) → (VDF,0)

## Instalação

Requisitos: Python 3.10+.

```bash
pip install -r requirements.txt
```

Ou modo dev (com testes):

```bash
pip install -e ".[dev]"
pytest
```

## Como usar

### 1) Calcular a partir de um CSV (batch)

Crie um CSV com colunas:

`id,PAS,PAD,VDF,VSF,PET,ET,Ees,V0`

Exemplo em `data/example_input.csv`.

```bash
python -m chen_pv.cli compute --input data/example_input.csv --output out/results.csv
```

### 2) Extrair valores de um .xlsm preenchido

**Importante:** `openpyxl` lê **valores salvos** (cache). Se você alterou entradas, abra no Excel/LibreOffice e **salve** antes de extrair, ou então use o comando `compute`.

```bash
python -m chen_pv.cli extract --workbook "Loop PV - metodo de chen.xlsm" --output out/vars.json
```

### 3) Preencher o template .xlsm com entradas e salvar cópia

```bash
python -m chen_pv.cli fill-template \
  --template "Loop PV - metodo de chen.xlsm" \
  --row-json '{"PAS":120,"PAD":70,"VDF":67.35,"VSF":34.35,"PET":110,"ET":300,"Ees":2.39,"V0":-8.21}' \
  --output "out/paciente_001.xlsm"
```

### 4) Gerar gráfico do loop PV

```bash
python -m chen_pv.cli plot --input data/example_input.csv --outdir out/plots
```

## Estrutura

- `src/chen_pv/core.py`: fórmulas e cálculo (sem Excel).
- `src/chen_pv/excel_template.py`: leitura/escrita do template `.xlsm`.
- `src/chen_pv/plotting.py`: pontos e gráfico.
- `src/chen_pv/cli.py`: linha de comando.
- `tests/`: testes básicos (sanidade).

## Licença

MIT.

