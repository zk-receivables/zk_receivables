#!/bin/zsh

open -a /Applications/Docker.app && cd /Volumes/samsungt7/Users/johnmccallig/Data/Code/crypto_web3/git/ZK_Receivables

sleep 5

docker compose up -d

sleep 5

docker compose exec sandbox bash

cd myprojects/ZK_Receivables/