default: compile

clean:
    rm prose.json
    rm -rf data/src
    cp -R data/src.orig data/src

build:
    poetry build

install:
    poetry install

compile:
    poetry run python src/prose

merge:
    poetry run python src/prose --merge --inplace
