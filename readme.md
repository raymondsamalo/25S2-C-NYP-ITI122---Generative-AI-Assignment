# loan_risk chat bot

## Python Environment

For this project I am using conda (miniconda) to create the python environment.
This provide consistent setup to run the application.

The conda environment is defined in `conda_environment.yml`
as followed:
```yaml
name: lr
channels:
  - defaults
dependencies:
  - python=3.12
  - pip
  - pip:
      - sqlmodel==0.0.27
      - langchain==1.0.3
      - langchain-classic==1.0.0
      - langchain-community==0.4.1
      - langchain-core==1.0.1
      - langchain-groq==1.0.0
      - langchain-ollama==1.0.0
      - langchain-openai==1.0.1
      - aiologic==0.15.0
      - camelot-py==1.0.9
      - chromadb==1.3.0
```      
To activate this environment, use
`conda activate lr `
To deactivate an active environment, use
`conda deactivate`
## PyTest

All tests are defined in `tests` folder, use `pytest` to run 

## Policy Service: Loading PDF Policy Documents

One of the problems we face is to extract policies from unstructured documents.
In our case, the documents are two pdf files that maybe updated from time to time.
We need to extract the policy within each document and make it usable for our LLM.

However, the policy on each document is presented in form of table without much context. Hence, we need to customise handling of each policy and reformat it by adding context also. We may not be able to simply translate the policy into text and then use tokenizer to store it into vector database. Nevertheless, we will attempt to do this at first using Chroma.

Later on we discover that after experimenting with chroma and the pdf tokenizer approach, we found the result is not very good and it is hard to break the table into proper and consistent chunks. 

We need a better more consistent approach that perhaps also less complicated which we will document at the end of this section.s


### Chroma

Originally we were thinking of using chroma database to store tokenized pdf policies document. However, I soon realize that the policies documents are mostly storing a single concise table which makes it hard to tokenize unlike prose.

Also in banks and financial institution, the document formats although unstructured are
usually consistent. Hence those documents will not change in form of format.

Hence, instead of using vector database to store context which then feed to the LLM as in RAG patterns, we pivoted to parse the table within the pdf and cache them in memory.
This will then provided to LLM as a policy service which called by one of the tools.

When the document updated, the policy service will check document modification time and reload the new document to replace the cache.

The challenge is to find the right tool to parse the pdf unstructured document and extract the table.

### Camelot

There are a whole bunch of tools to parse pdf but some like `tabula-py` :
- requires external dependencies ( `tabula java` in the case of `tabula-py`)
- requires manual manipulation of the pdf e.g. `PyMuPDF`,`PyPDF2`

What we need is a tool that simply extract the table and parse it. After exploring multiple tools, we discovered [`camelot-py`](https://camelot-py.readthedocs.io/en/master/). 

Some factors that influence our choice of Camelot:
- Camelot library focus on table extraction from pdf files. It requires minimum configuration.
- Camelot learned from older libraries and incorporate multiple algorithm to detect table and extract it https://camelot-py.readthedocs.io/en/master/user/how-it-works.html
- It extract table and provide us with panda data frame.

This approach is consistent, which is needed for our task. As long as the document format does not change, this extraction will work as expected.

### Our Policies Service Algorithm

Our final algorithm for using PDF policy documents prioritise reliability and consistency. 

It is based on assumption that the bank policy documents format remain consistent.

when LLM agent call tool:
- If the cache exist and its cached mtime is the same as current document's mtime then use data based on the cache. (mtime is unix modification timestamp for file)
- else:
    - use camelot to extract table from pdf
    - convert table to python dictionary or array in memory
    - cache the data and document mtime
- the cached data depends on each policy:
    - Bank Loan Interest Rate Policy is an dictionary of risk : interest rate
    - Bank Loan Overall Risk Policy is an array of rule objects that determine overall risk

We probably could use LLM for understanding the data but simple algorithm provide us with the predictability that we need for our Policies service.

# LLM

we are using local llm tinyllama with gguf optimization
```bash
ollama pull pacozaa/tinyllama
```
