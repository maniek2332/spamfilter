STYLE=-s pk_inz
EXTENSIONS=-e preprocess -e dotted_toc
OPTS=--font-path=fonts

# requires: docutils
pdf: paper.rst
	rst2pdf paper.rst -o paper.pdf ${STYLE} ${EXTENSIONS} ${OPTS}

all: pdf
