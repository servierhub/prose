default: prepare

clean:
    rm -rf data/src
    rm prose.json

prepare: clean
    cp -R data/src.orig data/src

build:
    poetry build

install:
    poetry install

compile:
    poetry run python src/prose

merge:
    poetry run python src/prose --merge --inplace
