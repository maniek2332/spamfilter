PAPER_STYLE=-s pk_inz
PAPER_EXTENSIONS=-e preprocess -e dotted_toc
PAPER_EXTRA=-b 1 --font-path=fonts
PAPER_OPTS=${PAPER_STYLE} ${PAPER_EXTENSIONS} ${PAPER_EXTRA}

SLIDES_STYLE=-s slides,dejavu
SLIDES_EXTENSIONS=-e preprocess
SLIDES_EXTRA=-b 1
SLIDES_OPTS=${SLIDES_STYLE} ${SLIDES_EXTENSIONS} ${SLIDES_EXTRA}

# requires: docutils
pdf: paper.rst
	rst2pdf paper.rst -o paper.pdf ${PAPER_OPTS}

slideshow: slideshow.rst
	rst2pdf slideshow.rst -o slideshow.pdf ${SLIDES_OPTS}

all: pdf slideshow
