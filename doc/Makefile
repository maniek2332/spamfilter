STYLE=-s pk_inz
EXTENSIONS=-e preprocess -e dotted_toc
OPTS=--real-footnotes --font-path=fonts

# requires: docutils
pdf: praca.rst
	rst2pdf praca.rst -o praca.pdf ${STYLE} ${EXTENSIONS} ${OPTS}

all: pdf
