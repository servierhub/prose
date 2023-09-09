default: prepare

clean:
    rm -rf data/src
    rm prose.json

prepare:
    cp -R data/src.orig data/src

build:
    poetry build

install:
    poetry install

compile:
    poetry run python src/prose parse --src="data/src/main/java/"

merge:
    poetry run python src/prose merge --in-place
