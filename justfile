set dotenv-load := true

default: prepare

clean:
    rm -rf data/src
    rm -rf .prose

prepare:
    cp -R data/src.orig data/src
    poetry run python src/prose config set-base-path data/src/main

build:
    poetry build

install:
    poetry install

compile:
    poetry run python src/prose add .

merge:
    poetry run python src/prose commit --merge
